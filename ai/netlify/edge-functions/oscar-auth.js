/* OSCAR's team sign-in: every request under /oscar passes through here first.

   A visitor without a session is sent to "Sign in with Google" through the RenewaBlox Supabase
   project (renewablox-crm), the same Google sign-in crm.renewablox.com uses, so there is no
   second Google client to keep. Supabase sends the browser back to /oscar/auth/callback with a
   one-time code, which only this browser can redeem (PKCE: the verifier sits in a signed cookie
   here). If the Google account is on OSCAR's list, a signed session cookie lets it in for
   SESSION_SECONDS, and the list is checked again on every request, so taking someone off it
   shuts them out at once (after the redeploy any environment change needs). Anything missing or
   wrong fails closed: OSCAR is never served without a valid session.

   Set in Netlify (Project configuration > Environment variables, scope including Functions):
     SUPABASE_URL              https://<project ref>.supabase.co
     SUPABASE_PUBLISHABLE_KEY  the project's publishable (public) key
     OSCAR_SESSION_SECRET      a long random secret that signs the cookies; changing it signs
                               everyone out
     OSCAR_ALLOWED_EMAILS      comma-separated Google accounts, any domain (gmail.com included)
     OSCAR_ALLOWED_DOMAINS     comma-separated Google Workspace domains, e.g. renewablox.com: any
                               account that Workspace manages (Google's "hd" claim), not merely any
                               address ending in it
   And in Supabase (Authentication > URL Configuration > Redirect URLs), the callback for each host
   OSCAR is served on: https://ai.renewablox.com/oscar/auth/callback. Without it Supabase sends the
   browser to the CRM instead and the sign-in can't finish.

   Netlify's [[headers]] rules don't reach responses an edge function makes, so OSCAR's own
   headers (its Content-Security-Policy among them) are set here; ai/build.py checks the policy
   still allows the live sources oscar.html calls. */

const SESSION_COOKIE = 'oscar_session';
const STATE_COOKIE = 'oscar_signin';
const USER_COOKIE = 'oscar_user';              // the signed-in address, for the page to show; not a credential
const SESSION_SECONDS = 7 * 24 * 3600;
const STATE_SECONDS = 10 * 60;

const OSCAR_HEADERS = {
  'content-security-policy': "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; " +
    "connect-src 'self' https://api.coingecko.com https://mempool.space https://api.blockchain.info; " +
    "base-uri 'none'; form-action 'none'; frame-ancestors 'self'",
  'x-content-type-options': 'nosniff',
  'referrer-policy': 'no-referrer',
  'x-robots-tag': 'noindex',
  'cache-control': 'private, no-cache'
};
const PAGE_HEADERS = {
  'content-type': 'text/html; charset=utf-8',
  'content-security-policy': "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
  'x-content-type-options': 'nosniff',
  'referrer-policy': 'no-referrer',
  'x-robots-tag': 'noindex',
  'cache-control': 'no-store'
};

export default async (request, context) => {
  const url = new URL(request.url);
  const cfg = settings();
  if (!cfg) {
    return page(503, 'OSCAR&rsquo;s sign-in isn&rsquo;t set up yet',
      'The sign-in needs its settings in Netlify before OSCAR can open. Until then it stays locked.');
  }
  if (url.pathname === '/oscar/auth/start') return start(url, cfg);
  if (url.pathname === '/oscar/auth/callback') return callback(request, url, cfg);
  if (url.pathname === '/oscar/auth/sign-out') return signOut(url);

  const session = await unseal(readCookie(request, SESSION_COOKIE), 'session', cfg);
  if (session && allowed(session.e, session.h, cfg)) {
    const res = await context.next();
    const out = new Response(res.body, res);
    for (const [k, v] of Object.entries(OSCAR_HEADERS)) out.headers.set(k, v);
    return out;
  }
  if (!isPageRequest(request)) {
    return new Response('Sign in to OSCAR first.', { status: 401, headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' } });
  }
  return signInPage(url);
};

export const config = { path: ['/oscar', '/oscar/*'] };

/* ---- the sign-in round trip ---- */

// A signed-out page request: hand over to the sign-in, keeping whatever followed the path (a shared
// scenario travels in the #fragment, which never reaches a server) for OSCAR to restore after.
function signInPage(url) {
  const go = `/oscar/auth/start?r=${encodeURIComponent(safeReturn(url.pathname))}`;
  return page(401, 'Signing you in&hellip;',
    'OSCAR is for the RenewaBlox team. Sign in with your Google account to open it.',
    { href: go, label: 'Sign in with Google' },
    `<script>try{if(location.search||location.hash)sessionStorage.setItem('oscar.returnTo',location.search+location.hash)}catch(e){}` +
    `location.replace(${JSON.stringify(go)})</script>`);
}

async function start(url, cfg) {
  const verifier = randomToken(48);
  const challenge = b64url(await crypto.subtle.digest('SHA-256', encoder.encode(verifier)));
  const sealed = await seal({ t: 'state', v: verifier, r: safeReturn(url.searchParams.get('r')), x: now() + STATE_SECONDS }, cfg);
  const auth = new URL(`${cfg.supabaseUrl}/auth/v1/authorize`);
  auth.search = new URLSearchParams({
    provider: 'google', redirect_to: `${url.origin}/oscar/auth/callback`,
    code_challenge: challenge, code_challenge_method: 's256', prompt: 'select_account'
  }).toString();
  // With one Workspace domain and no one from outside it, Google offers only that domain's accounts.
  if (cfg.domains.length === 1 && !cfg.emails.length) auth.searchParams.set('hd', cfg.domains[0]);
  return redirect(auth.toString(), [cookie(STATE_COOKIE, sealed, '/oscar/auth', STATE_SECONDS)]);
}

async function callback(request, url, cfg) {
  const q = url.searchParams;
  const clearState = cookie(STATE_COOKIE, '', '/oscar/auth', 0);
  const retry = { href: '/oscar/auth/start', label: 'Try again' };
  if (q.get('error')) {
    return page(401, 'Sign-in didn&rsquo;t finish', `The sign-in answered: ${esc(q.get('error_description') || q.get('error'))}.`, retry, '', [clearState]);
  }
  const st = await unseal(readCookie(request, STATE_COOKIE), 'state', cfg);
  if (!st || !q.get('code')) {
    return page(400, 'That sign-in has expired', 'Sign-ins have ten minutes to finish, in the browser they started in.', retry, '', [clearState]);
  }
  let session;
  try {
    // The code is only good with this browser's verifier, straight from Supabase over HTTPS.
    const res = await fetch(`${cfg.supabaseUrl}/auth/v1/token?grant_type=pkce`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', apikey: cfg.supabaseKey },
      body: JSON.stringify({ auth_code: q.get('code'), code_verifier: st.v })
    });
    if (!res.ok) throw new Error(`token endpoint answered ${res.status}`);
    session = await res.json();
  } catch (err) {
    console.error('OSCAR sign-in: no session from Supabase:', err && err.message);
    return page(400, 'That sign-in couldn&rsquo;t be completed', 'It may have expired or been used already. Try again.', retry, '', [clearState]);
  }
  const user = session && session.user;
  const google = user && (user.identities || []).find(i => i && i.provider === 'google');
  const claims = (google && google.identity_data) || {};
  const email = String(claims.email || '').toLowerCase();
  const hd = String((claims.custom_claims && claims.custom_claims.hd) || '').toLowerCase();
  const verified = claims.email_verified === true || claims.email_verified === 'true';
  if (!google || !email || !verified || email !== String(user.email || '').toLowerCase() || !allowed(email, hd, cfg)) {
    return page(403, 'This account can&rsquo;t open OSCAR',
      `${esc(email || 'That account')} isn&rsquo;t on OSCAR&rsquo;s list. Use your RenewaBlox Google account, or ask for this one to be added.`,
      { href: '/oscar/auth/start', label: 'Use a different account' }, '', [clearState]);
  }
  const sealed = await seal({ t: 'session', e: email, h: hd, x: now() + SESSION_SECONDS }, cfg);
  return redirect(new URL(st.r, url.origin).toString(), [
    clearState,
    cookie(SESSION_COOKIE, sealed, '/oscar', SESSION_SECONDS),
    cookie(USER_COOKIE, encodeURIComponent(email), '/oscar', SESSION_SECONDS, false)
  ]);
}

function signOut(url) {
  return redirect(new URL('/', url.origin).toString(), [
    cookie(SESSION_COOKIE, '', '/oscar', 0),
    cookie(USER_COOKIE, '', '/oscar', 0, false)
  ]);
}

/* ---- who may come in ---- */

function settings() {
  const env = k => String((globalThis.Netlify && Netlify.env.get(k)) || '').trim();
  const list = k => env(k).toLowerCase().split(',').map(s => s.trim()).filter(Boolean);
  const cfg = { supabaseUrl: env('SUPABASE_URL').replace(/\/+$/, ''), supabaseKey: env('SUPABASE_PUBLISHABLE_KEY'),
    secret: env('OSCAR_SESSION_SECRET'), emails: list('OSCAR_ALLOWED_EMAILS'), domains: list('OSCAR_ALLOWED_DOMAINS') };
  const missing = [!/^https:\/\//.test(cfg.supabaseUrl) && 'SUPABASE_URL', !cfg.supabaseKey && 'SUPABASE_PUBLISHABLE_KEY',
    cfg.secret.length < 32 && 'OSCAR_SESSION_SECRET (32 characters or more)',
    !cfg.emails.length && !cfg.domains.length && 'OSCAR_ALLOWED_EMAILS or OSCAR_ALLOWED_DOMAINS'].filter(Boolean);
  if (missing.length) { console.error('OSCAR sign-in is locked until these are set:', missing.join(', ')); return null; }
  return cfg;
}

// A listed address, or an account the listed Workspace domain manages (Google's hd claim).
function allowed(email, hd, cfg) {
  email = String(email || '').toLowerCase();
  const domain = email.split('@')[1] || '';
  return cfg.emails.includes(email) || (!!domain && cfg.domains.includes(domain) && String(hd || '').toLowerCase() === domain);
}

// Only paths inside OSCAR, so the round trip can't be turned into a redirect elsewhere. A path
// that changes when resolved (dot segments, %2e%2e) is refused rather than trusted.
function safeReturn(r) {
  if (typeof r !== 'string' || !/^\/oscar(?:\/[A-Za-z0-9._~%\-\/]*)?$/.test(r) || r.includes('//') || r.startsWith('/oscar/auth/')) return '/oscar/';
  try { return new URL(r, 'https://oscar.invalid').pathname === r ? r : '/oscar/'; } catch (e) { return '/oscar/'; }
}

/* ---- signed values: payload.signature, HMAC-SHA-256 under a key derived from the session secret ---- */

const encoder = new TextEncoder(), decoder = new TextDecoder();
const keys = new Map();
async function keyFor(cfg) {
  if (!keys.has(cfg.secret)) {
    keys.set(cfg.secret, (async () => {
      const raw = await crypto.subtle.importKey('raw', encoder.encode(cfg.secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
      const derived = await crypto.subtle.sign('HMAC', raw, encoder.encode('oscar-sign-in-v1'));
      return crypto.subtle.importKey('raw', derived, { name: 'HMAC', hash: 'SHA-256' }, false, ['sign', 'verify']);
    })());
  }
  return keys.get(cfg.secret);
}
async function seal(obj, cfg) {
  const body = b64url(encoder.encode(JSON.stringify(obj)));
  return `${body}.${b64url(await crypto.subtle.sign('HMAC', await keyFor(cfg), encoder.encode(body)))}`;
}
async function unseal(token, purpose, cfg) {
  const [body, sig, extra] = String(token || '').split('.');
  if (!body || !sig || extra !== undefined) return null;
  try {
    if (!(await crypto.subtle.verify('HMAC', await keyFor(cfg), unb64url(sig), encoder.encode(body)))) return null;
    const obj = JSON.parse(decoder.decode(unb64url(body)));
    return obj && obj.t === purpose && Number(obj.x) > now() ? obj : null;
  } catch (e) { return null; }
}

/* ---- small things ---- */

const now = () => Math.floor(Date.now() / 1000);
function b64url(bytes) {
  let s = '';
  for (const b of new Uint8Array(bytes)) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
function unb64url(s) {
  s = s.replace(/-/g, '+').replace(/_/g, '/');
  return Uint8Array.from(atob(s + '='.repeat((4 - s.length % 4) % 4)), c => c.charCodeAt(0));
}
function randomToken(bytes = 24) { return b64url(crypto.getRandomValues(new Uint8Array(bytes))); }
function readCookie(request, name) {
  for (const part of (request.headers.get('cookie') || '').split(';')) {
    const i = part.indexOf('=');
    if (i > 0 && part.slice(0, i).trim() === name) return part.slice(i + 1).trim();
  }
  return '';
}
function cookie(name, value, path, maxAge, httpOnly = true) {
  return `${name}=${value}; Path=${path}; Max-Age=${maxAge}; Secure; SameSite=Lax${httpOnly ? '; HttpOnly' : ''}`;
}
function isPageRequest(request) {
  return request.method === 'GET' && (request.headers.get('sec-fetch-dest') === 'document' || (request.headers.get('accept') || '').includes('text/html'));
}
function redirect(location, cookies = []) {
  const headers = new Headers({ location, 'cache-control': 'no-store' });
  for (const c of cookies) headers.append('set-cookie', c);
  return new Response(null, { status: 303, headers });
}
function esc(s) {
  return String(s).replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
}
function page(status, title, text, action, script = '', cookies = []) {
  const headers = new Headers(PAGE_HEADERS);
  for (const c of cookies) headers.append('set-cookie', c);
  return new Response(`<!DOCTYPE html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>OSCAR &middot; RenewaBlox</title><meta name="robots" content="noindex">
<style>
  :root{color-scheme:light;--bg:#f4f8fa;--surface:#fff;--line:#dfe8ed;--ink:#0d1b23;--ink-2:#33454f;--brand:#12475e;--accent:#1f5f7f;--on-brand:#fff}
  @media (prefers-color-scheme: dark){:root{color-scheme:dark;--bg:#0b161c;--surface:#10222b;--line:#22363f;--ink:#e8f0f4;--ink-2:#c3d2da;--brand:#a9d6ea;--accent:#6fb3d3;--on-brand:#07161e}}
  html,body{margin:0;height:100%}
  body{display:grid;place-items:center;background:var(--bg);color:var(--ink);padding:24px;box-sizing:border-box;font-family:"Inter","Inter var",system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
  .card{max-width:480px;text-align:center;background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:40px 32px;box-shadow:0 1px 2px rgba(9,26,35,.06),0 6px 18px rgba(9,26,35,.08)}
  .k{font-size:13px;font-weight:850;letter-spacing:.14em;color:var(--brand)}
  h1{margin:12px 0 0;font-size:26px;letter-spacing:-.02em;color:var(--brand)}
  p{margin:12px 0 0;font-size:15px;line-height:1.6;color:var(--ink-2)}
  a{display:inline-block;margin-top:22px;font-size:14px;font-weight:700;text-decoration:none;padding:11px 20px;border-radius:999px;background:var(--brand);color:var(--on-brand)}
  a:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
  .home{display:block;margin-top:14px;padding:0;background:none;color:var(--accent);font-weight:600}
</style></head>
<body><div class="card"><div class="k">OSCAR</div><h1>${title}</h1><p>${text}</p>
${action ? `<a href="${esc(action.href)}">${action.label}</a>` : ''}<a class="home" href="/">RenewaBlox AI tools</a></div>
${script}</body></html>`, { status, headers });
}
