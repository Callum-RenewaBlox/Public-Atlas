/* ai.renewablox.com's sign-in: every request to the site passes through here first, whatever its address, and only
   the sign-in's own round trip under /access/ is answered without a session. Only RenewaBlox staff get in: a Google
   account with a verified @renewablox.com address.

   It is the Atlas's sign-in (atlas/netlify/edge-functions/atlas-gate.js), cut down: the same Supabase project
   (renewablox-crm, whose Google sign-in the CRM and the Atlas use), the same PKCE round trip, the same check that every
   Google and Microsoft identity on the account vouches for its address, the same sealed cookies and the same way of
   keeping a #fragment across the round trip. What differs: it covers the whole site, it offers Google only, and who may
   come in is decided here, by the address's domain, rather than by public.atlas_my_access(). A session lasts
   SESSION_SECONDS and holds only the address: no Supabase token is kept, so it ends when it runs out (or on sign-out).

   Anything missing or wrong fails closed: no page, asset or file of the site is served without a valid session, and if
   this function errors Netlify shows its error page (onError: 'fail') rather than the site.

   Set in Netlify (renewablox-ai > Project configuration > Environment variables, scope including Functions, deploy
   contexts including Deploy Previews; a change needs a redeploy):
     SUPABASE_URL              https://enghoowpiwopsfabfurx.supabase.co (renewablox-crm), as for the Atlas
     SUPABASE_PUBLISHABLE_KEY  renewablox-crm's publishable (public) key, as for the Atlas
     AI_SESSION_SECRET         32 or more random characters, marked secret, not the Atlas's; changing it signs everyone out
   And in Supabase (renewablox-crm > Authentication > URL Configuration > Redirect URLs):
     https://ai.renewablox.com/access/callback
     https://deploy-preview-*--renewablox-ai.netlify.app/access/callback   (for deploy previews)
   Without them Supabase sends the browser to the CRM instead and the sign-in can't finish. Google itself needs nothing
   new: it only ever sends the browser back to Supabase.

   Netlify's custom headers (netlify.toml's [[headers]]) don't reach a response that passes through an edge function,
   so build.py copies them into ../edge-lib/site.js and this function sets them on each page it lets through. */

import { HEADERS, WORDMARK } from '../edge-lib/site.js';

const DOMAIN = 'renewablox.com';
const SESSION_COOKIE = 'rbx_ai';
const STATE_COOKIE = 'rbx_ai_signin';
const SESSION_SECONDS = 7 * 24 * 3600;   // how long a sign-in lasts: a week, then Google is asked again
const STATE_SECONDS = 10 * 60;           // how long a sign-in has to finish
const SUPABASE_TIMEOUT_MS = 8000;
// Google, through Supabase; hd asks Google's account chooser for RenewaBlox accounts (a hint only: the check is below)
const GOOGLE = { provider: 'google', prompt: 'select_account', hd: DOMAIN };

const GATED_HEADERS = {
  'x-robots-tag': 'noindex, nofollow',
  'x-content-type-options': 'nosniff',
  'cache-control': 'private, no-cache'
};
const PAGE_HEADERS = {
  'content-type': 'text/html; charset=utf-8',
  'content-security-policy': "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; " +
    "base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
  'x-robots-tag': 'noindex, nofollow',
  'x-content-type-options': 'nosniff',
  'referrer-policy': 'same-origin',
  'x-frame-options': 'DENY',
  'cache-control': 'no-store'
};

export default async (request, context) => {
  const url = new URL(request.url);
  const cfg = settings();
  if (!cfg) {
    return page(503, 'The sign-in isn&rsquo;t set up yet',
      'RenewaBlox AI opens once its sign-in has its settings. Until then it stays locked.');
  }
  const path = url.pathname;
  if (path === '/access' || path === '/access/') return signInPage(url);
  if (path === '/access/start') return start(url, cfg);
  if (path === '/access/callback') return callback(request, url, cfg);
  if (path === '/access/sign-out') return signOut();
  if (path.startsWith('/access/')) return page(404, 'That page isn&rsquo;t here', 'Head back to RenewaBlox AI.', { href: '/', label: 'RenewaBlox AI' });

  const session = await unseal(readCookie(request, SESSION_COOKIE), 'session', cfg);
  if (!session) return signedOut(request, url);

  const res = await context.next();
  const out = new Response(res.body, res);
  for (const [k, v] of Object.entries(headersFor(path))) out.headers.set(k, v);
  for (const [k, v] of Object.entries(GATED_HEADERS)) out.headers.set(k, v);
  return out;
};

// Every request, whatever its spelling (a run of slashes, an encoded character, any case), comes here first.
export const config = { path: '/*', onError: 'fail' };

/* ---- the sign-in round trip ---- */

function signedOut(request, url) {
  if (!isPageRequest(request)) return text(401, 'Sign in first.');
  return redirect(`/access/?r=${encodeURIComponent(safeReturn(url.pathname + url.search))}`);
}

// The sign-in page. A #fragment on the page that sent the visitor here (#scenario-3 on /eunice/, say) survives the
// redirect, so it is kept in sessionStorage and put back on the address once they are in.
function signInPage(url) {
  const r = encodeURIComponent(safeReturn(url.searchParams.get('r')));
  return page(401, 'Sign in to RenewaBlox AI',
    'RenewaBlox&rsquo;s in-house tools are for RenewaBlox staff. Sign in with your <b>@renewablox.com</b> Google account.',
    { href: `/access/start?r=${r}`, label: 'Sign in with Google' },
    `<script>try{sessionStorage.setItem('rbx.ai.hash',location.hash||'')}catch(e){}</script>`);
}

async function start(url, cfg) {
  const verifier = randomToken(48);
  const challenge = b64url(await crypto.subtle.digest('SHA-256', encoder.encode(verifier)));
  const sealed = await seal({ t: 'state', v: verifier, r: safeReturn(url.searchParams.get('r')), x: now() + STATE_SECONDS }, cfg);
  const auth = new URL(`${cfg.supabaseUrl}/auth/v1/authorize`);
  auth.search = new URLSearchParams({
    provider: GOOGLE.provider, redirect_to: `${url.origin}/access/callback`,
    code_challenge: challenge, code_challenge_method: 's256', prompt: GOOGLE.prompt, hd: GOOGLE.hd
  }).toString();
  return redirect(auth.toString(), [cookie(STATE_COOKIE, sealed, '/access', STATE_SECONDS)]);
}

async function callback(request, url, cfg) {
  const q = url.searchParams;
  const clearState = cookie(STATE_COOKIE, '', '/access', 0);
  const retry = { href: '/access/', label: 'Try again' };
  if (q.get('error')) {
    return page(401, 'Sign-in didn&rsquo;t finish', `Google answered: ${esc(q.get('error_description') || q.get('error'))}.`, retry, '', null, [clearState]);
  }
  const st = await unseal(readCookie(request, STATE_COOKIE), 'state', cfg);
  if (!st || !q.get('code')) {
    return page(400, 'That sign-in has expired', 'Sign-ins have ten minutes to finish, in the browser they started in.', retry, '', null, [clearState]);
  }
  const tokens = await supabase(cfg, '/auth/v1/token?grant_type=pkce', { auth_code: q.get('code'), code_verifier: st.v });
  if (!tokens || !tokens.access_token) {
    return page(400, 'That sign-in couldn&rsquo;t be completed', 'It may have expired or been used already. Try again.', retry, '', null, [clearState]);
  }
  const email = verifiedEmail(tokens.user, 'google');
  const other = { href: `/access/start?r=${encodeURIComponent(st.r)}`, label: 'Use a different Google account' };
  if (!email) {
    return page(403, 'Not authorised',
      'That Google account&rsquo;s address isn&rsquo;t one Google has verified, so it can&rsquo;t be used here. ' +
      'Sign in with your @renewablox.com Google account.', other, '', null, [clearState]);
  }
  if (!staff(email, tokens.user)) {
    return page(403, 'Not authorised',
      `You&rsquo;re signed in to Google as <b>${esc(email)}</b>. RenewaBlox AI is for RenewaBlox staff only: ` +
      'sign in with your @renewablox.com Google account instead.', other, '', null, [clearState]);
  }
  const session = { t: 'session', e: email, x: now() + SESSION_SECONDS };
  // a page, not a redirect, so the #fragment kept at the sign-in page can be put back on the address
  return page(200, 'Signed in', 'Opening the page&hellip;', { href: st.r, label: 'Open it' },
    `<script>var h='';try{h=sessionStorage.getItem('rbx.ai.hash')||'';sessionStorage.removeItem('rbx.ai.hash')}catch(e){}` +
    `location.replace(${JSON.stringify(st.r)}+(/^#[\\w\\-.~%=&,;:+\\/?!]*$/.test(h)?h:''))</script>`, null,
    [clearState, cookie(SESSION_COOKIE, await seal(session, cfg), '/', SESSION_SECONDS)]);
}

function signOut() {
  return page(200, 'Signed out', 'You&rsquo;re signed out of RenewaBlox AI on this browser.', { href: '/access/', label: 'Sign in again' }, '', null,
    [cookie(SESSION_COOKIE, '', '/', 0)]);
}

// RenewaBlox staff: an @renewablox.com address (already checked as verified by every identity on the account) whose
// Google identity, when Google says which Workspace it belongs to (the hd claim), belongs to RenewaBlox's.
export function staff(email, user) {
  const at = email.lastIndexOf('@');
  if (at < 1 || email.slice(at + 1) !== DOMAIN) return false;
  const google = ((user && user.identities) || []).filter(i => i && i.provider === 'google');
  return google.length > 0 && google.every(i => {
    const hd = ((i.identity_data || {}).custom_claims || {}).hd;
    return hd === undefined || String(hd).toLowerCase() === DOMAIN;
  });
}

// POST to Supabase. Answers the parsed body, or null on any failure.
async function supabase(cfg, endpoint, body) {
  try {
    const res = await fetch(cfg.supabaseUrl + endpoint, {
      method: 'POST', headers: { 'content-type': 'application/json', apikey: cfg.supabaseKey }, body: JSON.stringify(body),
      signal: AbortSignal.timeout(SUPABASE_TIMEOUT_MS)
    });
    if (!res.ok) { console.error(`RenewaBlox AI sign-in: Supabase ${endpoint.split('?')[0]} answered ${res.status}`); return null; }
    return await res.json();
  } catch (err) {
    console.error(`RenewaBlox AI sign-in: Supabase ${endpoint.split('?')[0]} unreachable:`, err && err.message);
    return null;
  }
}

// The account's address, if it holds an identity of the provider just signed in with and every Google and Microsoft
// identity on it vouches for that address; else ''. (As the Atlas's sign-in: Supabase joins identities that share an
// address into one account, so the check can't rest on one identity.)
const MICROSOFT_CONSUMER_TENANT = '9188040d-6c67-4c5b-b112-36a304b66dad';
export function verifiedEmail(user, provider) {
  const email = String((user && user.email) || '').toLowerCase();
  const ids = ((user && user.identities) || []).filter(i => i && (i.provider === 'google' || i.provider === 'azure'));
  if (!email || !ids.some(i => i.provider === provider)) return '';
  return ids.every(i => vouches(i, email)) ? email : '';
}
function vouches(id, email) {
  const claims = id.identity_data || {};
  const verified = claims.email_verified === true || claims.email_verified === 'true';
  if (!verified || String(claims.email || '').toLowerCase() !== email) return false;
  if (id.provider !== 'azure') return true;
  const custom = claims.custom_claims || {};
  return custom.tid === MICROSOFT_CONSUMER_TENANT || [true, 'true', '1', 1].includes(custom.xms_edov);
}

/* ---- the site's own headers (netlify.toml's [[headers]], via build.py) ---- */

// Netlify's rules: "/x/*" covers everything under /x/, any other rule its own address only; later rules win.
export function headersFor(path) {
  const out = {};
  for (const rule of HEADERS) {
    const hit = rule.for.endsWith('/*') ? path.startsWith(rule.for.slice(0, -1)) : path === rule.for;
    if (hit) for (const [k, v] of Object.entries(rule.values)) out[k.toLowerCase()] = v;
  }
  return out;
}

/* ---- settings ---- */

function settings() {
  const env = k => String((globalThis.Netlify && Netlify.env.get(k)) || '').trim();
  const cfg = { supabaseUrl: env('SUPABASE_URL').replace(/\/+$/, ''), supabaseKey: env('SUPABASE_PUBLISHABLE_KEY'), secret: env('AI_SESSION_SECRET') };
  const missing = [!/^https:\/\/[a-z0-9-]+\.supabase\.co$/.test(cfg.supabaseUrl) && 'SUPABASE_URL', !cfg.supabaseKey && 'SUPABASE_PUBLISHABLE_KEY',
    cfg.secret.length < 32 && 'AI_SESSION_SECRET (32 characters or more)'].filter(Boolean);
  if (missing.length) { console.error('RenewaBlox AI is locked until these are set:', missing.join(', ')); return null; }
  return cfg;
}

// Where to go back to after signing in: an address on this site, with a plain query, never the sign-in itself, so the
// round trip can't be turned into a redirect elsewhere. A path that changes when resolved (dot segments) is refused.
export function safeReturn(r) {
  const fallback = '/';
  if (typeof r !== 'string' || r.length > 400) return fallback;
  const [path, query = '', extra] = r.split('?');
  if (extra !== undefined || !/^\/[A-Za-z0-9._~%\-\/]*$/.test(path) || path.includes('//') || /^\/access(\/|$)/i.test(path)) return fallback;
  if (!/^[A-Za-z0-9._~%\-=&,+]*$/.test(query)) return fallback;
  try { if (new URL(path, 'https://ai.invalid').pathname !== path) return fallback; } catch (e) { return fallback; }
  return query ? `${path}?${query}` : path;
}

/* ---- sealed values: AES-GCM under a key derived from the session secret ---- */

const encoder = new TextEncoder(), decoder = new TextDecoder();
const AAD = encoder.encode('rbx-ai-v1');
const keys = new Map();
function keyFor(cfg) {
  if (!keys.has(cfg.secret)) {
    keys.set(cfg.secret, (async () => {
      const raw = await crypto.subtle.importKey('raw', encoder.encode(cfg.secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
      const derived = await crypto.subtle.sign('HMAC', raw, encoder.encode('ai-sign-in-v1'));
      return crypto.subtle.importKey('raw', derived, { name: 'AES-GCM' }, false, ['encrypt', 'decrypt']);
    })());
  }
  return keys.get(cfg.secret);
}
async function seal(obj, cfg) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = await crypto.subtle.encrypt({ name: 'AES-GCM', iv, additionalData: AAD }, await keyFor(cfg), encoder.encode(JSON.stringify(obj)));
  return `${b64url(iv)}.${b64url(ct)}`;
}
async function unseal(token, purpose, cfg) {
  const [iv, ct, extra] = String(token || '').split('.');
  if (!iv || !ct || extra !== undefined) return null;
  try {
    const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: unb64url(iv), additionalData: AAD }, await keyFor(cfg), unb64url(ct));
    const obj = JSON.parse(decoder.decode(plain));
    if (!obj || obj.t !== purpose || !(Number(obj.x) > now())) return null;
    if (purpose === 'session' && !(typeof obj.e === 'string' && staff(obj.e, { identities: [{ provider: 'google' }] }))) return null;
    return obj;
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
function cookie(name, value, path, maxAge) {
  return `${name}=${value}; Path=${path}; Max-Age=${maxAge}; Secure; SameSite=Lax; HttpOnly`;
}
function isPageRequest(request) {
  return request.method === 'GET' && (request.headers.get('sec-fetch-dest') === 'document' || request.headers.get('sec-fetch-dest') === 'iframe' ||
    (request.headers.get('accept') || '').includes('text/html'));
}
function redirect(location, cookies = [], status = 303) {
  const headers = new Headers({ location, 'cache-control': 'no-store', 'x-robots-tag': 'noindex, nofollow' });
  for (const c of cookies) headers.append('set-cookie', c);
  return new Response(null, { status, headers });
}
function text(status, body) {
  return new Response(body, { status, headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store', 'x-robots-tag': 'noindex, nofollow' } });
}
function esc(s) {
  return String(s).replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
}
// A page of the sign-in: self-contained (inline style, the wordmark as a data image), as nothing else on the site can
// be fetched before signing in.
function page(status, title, textHtml, action, extra = '', secondary = null, cookies = []) {
  const headers = new Headers(PAGE_HEADERS);
  for (const c of cookies) headers.append('set-cookie', c);
  return new Response(`<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>${title.replace(/<[^>]*>/g, '')} · RenewaBlox AI</title>
<style>*{box-sizing:border-box}html,body{height:100%}
body{margin:0;display:grid;place-items:center;padding:24px 16px;background:linear-gradient(128deg,#1B6E94 0%,#156082 46%,#0B3549 100%);
font-family:"Leelawadee UI","Open Sans","Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;color:#0B3549;line-height:1.55}
.card{width:100%;max-width:440px;background:#fff;border-radius:16px;padding:30px 28px 26px;text-align:center;
box-shadow:0 0 0 .5px rgba(8,37,51,.06),0 1px 2px rgba(8,37,51,.05),0 18px 40px -12px rgba(8,37,51,.45)}
.mark{display:block;height:22px;width:auto;margin:0 auto 4px}.app{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#218099;font-weight:700}
h1{font-size:22px;line-height:1.25;margin:18px 0 8px}p{margin:0 0 20px;color:#44596A;font-size:15px}
.btn{display:inline-block;background:#156082;color:#fff;text-decoration:none;font-weight:700;padding:11px 20px;border-radius:999px}
.btn:hover{background:#0B3549}.btn:focus-visible,.sub:focus-visible{outline:2px solid #156082;outline-offset:3px}
.sub{display:block;margin-top:16px;font-size:14px;color:#156082}.foot{margin:22px 0 0;font-size:12px;color:#5F7282}</style></head>
<body><main class="card"><img class="mark" src="${WORDMARK}" alt="RenewaBlox" width="193" height="22"><div class="app">AI</div>
<h1>${title}</h1><p>${textHtml}</p>${extra.startsWith('<script') ? '' : extra}
${[].concat(action || []).map(a => `<a class="btn" href="${esc(a.href)}">${a.label}</a>`).join('<br>')}
${secondary ? `<a class="sub" href="${esc(secondary.href)}">${secondary.label}</a>` : ''}
<p class="foot">no Watt wasted</p></main>${extra.startsWith('<script') ? extra : ''}</body></html>`, { status, headers });
}
