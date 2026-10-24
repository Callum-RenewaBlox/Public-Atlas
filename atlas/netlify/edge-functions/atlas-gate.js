/* The Atlas sign-in: every request under /clients/ and /team/ passes through here first, and the sign-in round trip
   runs under /access/.

   A visitor without a session is asked to sign in with Google or Microsoft (a personal Outlook/Hotmail/Live account or a
   work Microsoft 365 one), through RenewaBlox's Supabase project (renewablox-crm), whose Google sign-in the CRM also uses. Supabase sends the browser back to /access/callback with a one-time code that
   only this browser can redeem (PKCE: the verifier sits in a sealed cookie here), and this function redeems it, so no
   Supabase token ever reaches the page. Who may open what is Supabase's to say: public.atlas_my_access(), asked with the
   visitor's own token, answers '*' for an active CRM team member and otherwise the client codes listed for the address
   in public.atlas_access. /clients/<code>/… opens to '*' or <code>; /team/… to '*' only.

   The session is one encrypted cookie: the address, its access, and Supabase's refresh token, so the access is asked
   again at the first page opened after ACCESS_SECONDS (a row removed in Supabase shuts the client out within minutes,
   with no redeploy). Anything missing or wrong fails closed: a client page is never served without a valid session.

   Set in Netlify (Project configuration > Environment variables, scope including Functions; a change needs a redeploy):
     SUPABASE_URL              https://<project ref>.supabase.co (renewablox-crm)
     SUPABASE_PUBLISHABLE_KEY  the project's publishable (public) key
     ATLAS_SESSION_SECRET      a long random secret (32 characters or more) that seals the cookies; changing it signs
                               everyone out
   And in Supabase (Authentication > URL Configuration > Redirect URLs): https://atlas.renewablox.com/access/callback.
   Without it Supabase sends the browser to the CRM instead and the sign-in can't finish.
   Microsoft is Supabase's Azure provider (Authentication > Sign In / Providers > Azure): the Entra app registration
   "RenewaBlox Atlas" (any Entra tenant + personal Microsoft accounts, the email and xms_edov optional claims), its client
   ID and secret value, and the tenant URL left blank. The secret expires; when it does, Microsoft sign-in fails until a
   new one is pasted in.
   The fallback for anyone without either account, or whose organisation blocks the Microsoft app, is a one-time code
   sent by email (/access/email): Supabase's email OTP, typed in on the page, so it works when the email is read on
   another device. It needs, in Supabase: custom SMTP (Authentication > Emails > SMTP Settings; the built-in sender
   only reaches the project's own team), and the Magic Link and Confirm signup templates carrying {{ .Token }}, not a
   link (a first-time address gets the Confirm signup email). Every way in, access is the verified address checked
   against public.atlas_access.

   The pages, their ?view= routes and their security policies come from the build (atlas/build.py writes
   ../edge-lib/pages.js). Netlify's _headers rules don't reach responses that pass through an edge function, so every
   header these pages need is set here. */

import { PAGES, CSP, REDIRECTS } from '../edge-lib/pages.js';

const SESSION_COOKIE = 'rbx_atlas';
const STATE_COOKIE = 'rbx_atlas_signin';
const CODE_COOKIE = 'rbx_atlas_code';
const CODE_SECONDS = 15 * 60;             // how long the code page waits for the code (Supabase's own expiry also applies)
const SESSION_SECONDS = 30 * 24 * 3600;   // how long a sign-in lasts
const ACCESS_SECONDS = 10 * 60;           // how old the access may be before a page asks Supabase again
const STALE_SECONDS = 24 * 3600;          // if Supabase can't be reached, how old an answer may still be trusted
const FILE_SECONDS = 6 * 3600;            // a page's files (models, images) are served on an answer up to this old; only
                                          // pages ask again, so a removed client loses the files too once it runs out
const STATE_SECONDS = 10 * 60;
const SUPABASE_TIMEOUT_MS = 8000;

// The sign-ins offered, by the name the address carries (/access/start?p=…), with Supabase's name for each.
const PROVIDERS = {
  google: { supabase: 'google', label: 'Sign in with Google', params: { prompt: 'select_account' } },
  microsoft: { supabase: 'azure', label: 'Sign in with Microsoft', params: { scopes: 'email', prompt: 'select_account' } }
};

const GATED_HEADERS = {
  'x-robots-tag': 'noindex, nofollow',
  'x-content-type-options': 'nosniff',
  'referrer-policy': 'strict-origin-when-cross-origin',
  'permissions-policy': 'camera=(), microphone=(), geolocation=()',
  'x-frame-options': 'SAMEORIGIN',
  'cache-control': 'private, no-cache'
};
const PAGE_HEADERS = {
  'content-type': 'text/html; charset=utf-8',
  'content-security-policy': "default-src 'none'; script-src 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; " +
    "font-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
  'x-robots-tag': 'noindex, nofollow',
  'x-content-type-options': 'nosniff',
  'referrer-policy': 'same-origin',
  'x-frame-options': 'DENY',
  'cache-control': 'no-store'
};

export default async (request, context) => {
  const url = new URL(request.url);
  const clean = canonical(url.pathname);
  if (clean !== url.pathname) return redirect(clean + url.search, [], 301);
  const cfg = settings();
  if (!cfg) {
    return page(503, 'The sign-in isn&rsquo;t set up yet',
      'These pages open once their sign-in has its settings. Until then they stay locked.');
  }
  if (url.pathname === '/access' || url.pathname === '/access/') return signInPage(url);
  if (url.pathname === '/access/start') return start(url, cfg);
  if (url.pathname === '/access/callback') return callback(request, url, cfg);
  if (url.pathname === '/access/sign-out') return signOut();
  if (url.pathname === '/access/email') return request.method === 'POST' ? sendCode(request, cfg) : emailPage(url);
  if (url.pathname === '/access/email/code' && request.method === 'POST') return checkCode(request, cfg);
  if (url.pathname.startsWith('/access/')) return page(404, 'That page isn&rsquo;t here', 'Head back to Atlas.', { href: '/', label: 'Back to Atlas' });

  let session = await unseal(readCookie(request, SESSION_COOKIE), 'session', cfg);
  if (!session) return signedOut(request, url);

  // a page opened with an answer older than ACCESS_SECONDS asks Supabase again
  const cookies = [];
  if (isPageRequest(request) && now() - session.c > ACCESS_SECONDS) {
    const fresh = await refresh(session, cfg);
    if (fresh === 'revoked') return signedOut(request, url, [cookie(SESSION_COOKIE, '', '/', 0)]);
    if (fresh) {
      session = fresh;
      cookies.push(cookie(SESSION_COOKIE, await seal(session, cfg), '/', SESSION_SECONDS));
    } else if (now() - session.c > STALE_SECONDS) {
      return page(503, 'We can&rsquo;t check your access just now',
        'The sign-in service didn&rsquo;t answer. Try again in a minute.', { href: url.pathname + url.search, label: 'Try again' });
    }
  } else if (!isPageRequest(request) && now() - session.c > FILE_SECONDS) {
    return text(401, 'Open the page again to carry on.');
  }

  const path = url.pathname;
  if (path === '/clients' || path === '/clients/' || path === '/team' || path === '/team/') {
    return withCookies(listPage(session), cookies);
  }
  const moved = REDIRECTS[path];
  if (moved) return redirect(moved, cookies, 301);
  // a page's address without its slash (Netlify would add it, but this function answers first), or by its index.html:
  // the folder's address is the page's, where ?view= routing applies
  if (!path.endsWith('/') && PAGES[path + '/']) return redirect(path + '/' + url.search, cookies, 301);
  if (path.endsWith('/index.html') && PAGES[path.slice(0, -'index.html'.length)]) {
    return redirect(path.slice(0, -'index.html'.length) + url.search, cookies, 301);
  }
  const need = path.startsWith('/team/') ? '*' : (path.match(/^\/clients\/([a-z0-9][a-z0-9-]*)\//) || [])[1];
  if (!need || !(session.a.includes('*') || session.a.includes(need))) {
    if (!isPageRequest(request)) return withCookies(text(403, 'This account can’t open this page.'), cookies);
    return withCookies(page(403, 'This page isn&rsquo;t shared with you',
      `${esc(session.e)} can&rsquo;t open it. If it should, ask RenewaBlox to add this address, or sign in with the one it was shared with.`,
      { href: '/clients/', label: 'Pages shared with you' }, '', { href: '/access/sign-out', label: 'Sign out' }), cookies);
  }

  // ?view=<v> on a page opens one of its views, as the Streamlit apps did (the address stays as it is)
  const pg = PAGES[path];
  const view = url.searchParams.get('view');
  if (pg && view && pg.views && Object.prototype.hasOwnProperty.call(pg.views, view)) {
    // a rewrite carries no cookie, so a fresh session goes back to the browser first
    if (cookies.length) return redirect(path + url.search, cookies);
    return new URL(path + pg.views[view], url.origin);
  }

  const res = await context.next();
  const out = new Response(res.body, res);
  for (const [k, v] of Object.entries(GATED_HEADERS)) out.headers.set(k, v);
  out.headers.set('content-security-policy', policyFor(path));
  for (const c of cookies) out.headers.append('set-cookie', c);
  return out;
};

// Netlify picks the edge functions by the address as it was sent, but serves a file after folding a run of slashes,
// so a route of /clients/* alone would let //clients/… reach the files without passing through here. These patterns
// take in every spelling of the three folders (any run of slashes, any case, an encoded slash), and the function sends
// each to its one spelling (canonical) before anything else, where the checks below apply.
export const config = {
  pattern: [
    '^/+[cC][lL][iI][eE][nN][tT][sS](?:[/%].*)?$',
    '^/+[tT][eE][aA][mM](?:[/%].*)?$',
    '^/+[aA][cC][cC][eE][sS][sS](?:[/%].*)?$'
  ]
};

// An address's one spelling: no run of slashes, %2F as the slash it stands for, and the folder (and a client's code)
// in lower case, as the site's files are.
export function canonical(path) {
  const parts = path.replace(/%2f/gi, '/').replace(/\/{2,}/g, '/').split('/');
  parts[1] = (parts[1] || '').toLowerCase();
  if (parts[1] === 'clients' && parts.length > 2) parts[2] = parts[2].toLowerCase();
  return parts.join('/');
}

/* ---- the sign-in round trip ---- */

function signedOut(request, url, cookies = []) {
  if (!isPageRequest(request)) {
    const res = text(401, 'Sign in first.');
    for (const c of cookies) res.headers.append('set-cookie', c);
    return res;
  }
  return redirect(`/access/?r=${encodeURIComponent(safeReturn(url.pathname + url.search))}`, cookies);
}

// The sign-in page. A #fragment on the page that sent the visitor here (a view, a camera) survives the redirect, so it
// is kept in sessionStorage and put back once they are in.
function signInPage(url) {
  const r = encodeURIComponent(safeReturn(url.searchParams.get('r')));
  return page(401, 'Sign in to open this page',
    'This page is shared privately. Sign in with the account for the address it was shared with: Google for Gmail or ' +
    'Google Workspace, Microsoft for Outlook, Hotmail, Live or Microsoft&nbsp;365.',
    Object.entries(PROVIDERS).map(([p, v]) => ({ href: `/access/start?p=${p}&r=${r}`, label: v.label })),
    `<script>try{sessionStorage.setItem('rbx.atlas.hash',location.hash||'')}catch(e){}</script>`,
    { href: `/access/email?r=${r}`, label: 'No Google or Microsoft account, or can&rsquo;t sign in? Get a code by email' });
}

async function start(url, cfg) {
  const p = Object.prototype.hasOwnProperty.call(PROVIDERS, url.searchParams.get('p')) ? url.searchParams.get('p') : 'google';
  const verifier = randomToken(48);
  const challenge = b64url(await crypto.subtle.digest('SHA-256', encoder.encode(verifier)));
  const sealed = await seal({ t: 'state', v: verifier, p, r: safeReturn(url.searchParams.get('r')), x: now() + STATE_SECONDS }, cfg);
  const auth = new URL(`${cfg.supabaseUrl}/auth/v1/authorize`);
  auth.search = new URLSearchParams({
    provider: PROVIDERS[p].supabase, redirect_to: `${url.origin}/access/callback`,
    code_challenge: challenge, code_challenge_method: 's256', ...PROVIDERS[p].params
  }).toString();
  return redirect(auth.toString(), [cookie(STATE_COOKIE, sealed, '/access', STATE_SECONDS)]);
}

async function callback(request, url, cfg) {
  const q = url.searchParams;
  const clearState = cookie(STATE_COOKIE, '', '/access', 0);
  const retry = { href: '/access/', label: 'Try again' };
  if (q.get('error')) {
    return page(401, 'Sign-in didn&rsquo;t finish', `The sign-in answered: ${esc(q.get('error_description') || q.get('error'))}.`, retry, '', null, [clearState]);
  }
  const st = await unseal(readCookie(request, STATE_COOKIE), 'state', cfg);
  if (!st || !q.get('code')) {
    return page(400, 'That sign-in has expired', 'Sign-ins have ten minutes to finish, in the browser they started in.', retry, '', null, [clearState]);
  }
  const tokens = await supabase(cfg, '/auth/v1/token?grant_type=pkce', { auth_code: q.get('code'), code_verifier: st.v });
  if (!tokens || !tokens.access_token || !tokens.refresh_token) {
    return page(400, 'That sign-in couldn&rsquo;t be completed', 'It may have expired or been used already. Try again.', retry, '', null, [clearState]);
  }
  const email = verifiedEmail(tokens.user, PROVIDERS[st.p] ? PROVIDERS[st.p].supabase : 'google');
  if (!email) {
    return page(403, 'That account can&rsquo;t be used here',
      'Sign in with a Google or Microsoft account whose address the provider has verified.', retry, '', null, [clearState]);
  }
  return finish(tokens, email, st.r, cfg, clearState);
}

// Signed in as a verified address: Supabase says what it may open, and the session starts (or not).
async function finish(tokens, email, r, cfg, clearState) {
  const retry = { href: '/access/?r=' + encodeURIComponent(r), label: 'Try again' };
  const access = await myAccess(tokens.access_token, cfg);
  if (!access) {
    return page(503, 'We can&rsquo;t check your access just now', 'The sign-in service didn&rsquo;t answer. Try again in a minute.', retry, '', null, [clearState]);
  }
  if (!access.length) {
    return page(403, 'Nothing is shared with this account',
      `No page on Atlas is shared with ${esc(email)}. Sign in with the address RenewaBlox shared the page with, or ask for this one to be added.`,
      { href: '/access/?r=' + encodeURIComponent(r), label: 'Use a different account' }, '', null, [clearState]);
  }
  const session = { t: 'session', e: email, a: access, r: tokens.refresh_token, c: now(), x: now() + SESSION_SECONDS };
  // a page, not a redirect, so the #fragment kept at the sign-in page can be put back on the address
  return page(200, 'Signed in', 'Opening the page&hellip;', { href: r, label: 'Open it' },
    `<script>var h='';try{h=sessionStorage.getItem('rbx.atlas.hash')||'';sessionStorage.removeItem('rbx.atlas.hash')}catch(e){}` +
    `location.replace(${JSON.stringify(r)}+(/^#[\\w\\-.~%=&,;:+\\/?!]*$/.test(h)?h:''))</script>`, null,
    [clearState, cookie(SESSION_COOKIE, await seal(session, cfg), '/', SESSION_SECONDS)]);
}

/* ---- the fallback: a one-time code by email ---- */

const EMAIL_RE = /^[^\s@<>"']{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,}$/;

function emailForm(r, value = '') {
  return `<form method="post" action="/access/email" style="margin:0 auto 18px;max-width:340px;display:grid;gap:10px">
<input type="hidden" name="r" value="${esc(r)}"><input name="email" type="email" autocomplete="email" required maxlength="254"
value="${esc(value)}" placeholder="Your email address" aria-label="Your email address" class="field">
<button class="btn btn--primary" type="submit">Email me a code</button></form>`;
}
function codeForm() {
  return `<form method="post" action="/access/email/code" style="margin:0 auto 18px;max-width:340px;display:grid;gap:10px">
<input name="code" inputmode="numeric" autocomplete="one-time-code" required pattern="[0-9 ]{6,12}" maxlength="12"
placeholder="Code from the email" aria-label="Code from the email" class="field">
<button class="btn btn--primary" type="submit">Sign in</button></form>`;
}

function emailPage(url) {
  const r = safeReturn(url.searchParams.get('r'));
  return page(200, 'Get a sign-in code by email',
    'Enter the address the page was shared with. We&rsquo;ll email you a one-time code to type in here.',
    null, emailForm(r), { href: '/access/?r=' + encodeURIComponent(r), label: 'Back to Google or Microsoft sign-in' });
}

async function sendCode(request, cfg) {
  const form = await request.formData().catch(() => null);
  const r = safeReturn(String((form && form.get('r')) || ''));
  const email = String((form && form.get('email')) || '').trim().toLowerCase();
  const back = { href: '/access/?r=' + encodeURIComponent(r), label: 'Back to Google or Microsoft sign-in' };
  if (email.length > 254 || !EMAIL_RE.test(email)) {
    return page(400, 'Check the address', 'That doesn&rsquo;t look like an email address. Try again.', null, emailForm(r, email), back);
  }
  const sent = await supabase(cfg, '/auth/v1/otp', { email, create_user: true }, true);
  if (sent === 'busy') {
    return page(429, 'A code was sent a moment ago',
      'Check your inbox (and spam) for it, or wait a minute and ask for another.', null, emailForm(r, email), back);
  }
  if (!sent || sent === 'refused') {
    return page(503, 'We couldn&rsquo;t send the code just now', 'Try again in a minute, or use Google or Microsoft sign-in.', null, emailForm(r, email), back);
  }
  const st = await seal({ t: 'code', e: email, r, x: now() + CODE_SECONDS }, cfg);
  return page(200, 'Check your email',
    `We&rsquo;ve sent a sign-in code to ${esc(email)}. It can take a minute to arrive; check spam if it doesn&rsquo;t. Type it in below.`,
    null, codeForm(), { href: '/access/email?r=' + encodeURIComponent(r), label: 'Send a new code, or use a different address' },
    [cookie(CODE_COOKIE, st, '/access', CODE_SECONDS)]);
}

async function checkCode(request, cfg) {
  const clearCode = cookie(CODE_COOKIE, '', '/access', 0);
  const st = await unseal(readCookie(request, CODE_COOKIE), 'code', cfg);
  if (!st || typeof st.e !== 'string') {
    return page(400, 'That code has expired', 'Ask for a new code and use it within fifteen minutes, in this browser.', null,
      emailForm('/clients/'), null, [clearCode]);
  }
  const form = await request.formData().catch(() => null);
  const code = String((form && form.get('code')) || '').replace(/\s+/g, '');
  const again = { href: '/access/email?r=' + encodeURIComponent(st.r), label: 'Send a new code' };
  if (!/^[0-9]{6,10}$/.test(code)) {
    return page(400, 'Check the code', 'The code is the number in the email. Type it in again.', null, codeForm(), again);
  }
  const tokens = await supabase(cfg, '/auth/v1/verify', { type: 'email', email: st.e, token: code }, true);
  if (tokens === 'refused' || tokens === 'busy') {
    return page(401, 'That code isn&rsquo;t right', 'It may be mistyped or expired. Try again, or ask for a new one.', null, codeForm(), again);
  }
  if (!tokens || !tokens.access_token || !tokens.refresh_token) {
    return page(503, 'We can&rsquo;t check the code just now', 'The sign-in service didn&rsquo;t answer. Try again in a minute.', null, codeForm(), again);
  }
  const u = tokens.user || {};
  const email = String(u.email || '').toLowerCase();
  // the code proves the address; Supabase also marks it confirmed
  if (email !== st.e || !(u.email_confirmed_at || u.confirmed_at)) {
    return page(403, 'That code can&rsquo;t be used here', 'Ask for a new code and try again.', again, '', null, [clearCode]);
  }
  return finish(tokens, email, st.r, cfg, clearCode);
}

function signOut() {
  return page(200, 'Signed out', 'You&rsquo;re signed out of Atlas on this browser.', { href: '/', label: 'Back to Atlas' }, '', null,
    [cookie(SESSION_COOKIE, '', '/', 0)]);
}

// Supabase's answer for the session: 'revoked' when the refresh token is refused (sign in again), null when Supabase
// can't be reached (the caller decides), else the session with fresh access.
async function refresh(session, cfg) {
  const tokens = await supabase(cfg, '/auth/v1/token?grant_type=refresh_token', { refresh_token: session.r }, true);
  if (tokens === 'refused') return 'revoked';
  if (!tokens || !tokens.access_token || !tokens.refresh_token) return null;
  const email = String((tokens.user && tokens.user.email) || '').toLowerCase();
  if (email !== session.e) return 'revoked';
  const access = await myAccess(tokens.access_token, cfg);
  if (!access) return null;
  if (!access.length) return 'revoked';
  return { ...session, a: access, r: tokens.refresh_token, c: now() };
}

async function myAccess(accessToken, cfg) {
  const access = await supabase(cfg, '/rest/v1/rpc/atlas_my_access', {}, false, accessToken);
  return Array.isArray(access) ? access.filter(a => typeof a === 'string' && /^(\*|[a-z0-9][a-z0-9-]{0,40})$/.test(a)) : null;
}

// POST to Supabase. Answers the parsed body, null on any failure, or 'refused' (with refusals) for a 400/401/403.
async function supabase(cfg, endpoint, body, refusals = false, bearer = '') {
  try {
    const headers = { 'content-type': 'application/json', apikey: cfg.supabaseKey };
    if (bearer) headers.authorization = `Bearer ${bearer}`;
    // a Supabase that doesn't answer counts as unreachable, so a signed-in visitor is served on a recent answer (STALE_SECONDS)
    // rather than kept waiting until Netlify gives up on the page
    const res = await fetch(cfg.supabaseUrl + endpoint, { method: 'POST', headers, body: JSON.stringify(body),
      signal: AbortSignal.timeout(SUPABASE_TIMEOUT_MS) });
    if (!res.ok) {
      console.error(`Atlas sign-in: Supabase ${endpoint.split('?')[0]} answered ${res.status}`);
      if (refusals && res.status === 429) return 'busy';
      return refusals && [400, 401, 403, 422].includes(res.status) ? 'refused' : null;
    }
    return await res.json();
  } catch (err) {
    console.error(`Atlas sign-in: Supabase ${endpoint.split('?')[0]} unreachable:`, err && err.message);
    return null;
  }
}

// The address of the identity just signed in with ('google' or 'azure'), if that provider verified it and it is the
// user's own; else ''. For Microsoft, Supabase marks the address verified for a personal account, and for a work
// account only when Microsoft says the address's domain is verified (the xms_edov claim), so an unverified Microsoft
// 365 address can't stand in for a client's.
function verifiedEmail(user, provider) {
  const id = user && (user.identities || []).find(i => i && i.provider === provider);
  const claims = (id && id.identity_data) || {};
  const email = String(claims.email || '').toLowerCase();
  const verified = claims.email_verified === true || claims.email_verified === 'true';
  return id && email && verified && email === String(user.email || '').toLowerCase() ? email : '';
}

/* ---- what the visitor can open ---- */

function listPage(session) {
  const all = session.a.includes('*');
  const rows = Object.entries(PAGES)
    .filter(([path, p]) => p.list && (all || (p.client !== '*' && session.a.includes(p.client))))
    .map(([path, p]) => `<li><a href="${esc(path)}">${esc(p.title)}</a></li>`);
  const body = rows.length
    ? `<ul class="list">${rows.join('')}</ul>`
    : '<p>Nothing is shared with this address yet.</p>';
  return page(200, 'Pages shared with you', `Signed in as ${esc(session.e)}.`, null, body, { href: '/access/sign-out', label: 'Sign out' });
}

// The page's policy: the longest folder in CSP that holds the path.
function policyFor(path) {
  let best = '';
  for (const prefix of Object.keys(CSP)) if (path.startsWith(prefix) && prefix.length > best.length) best = prefix;
  return best ? CSP[best] : "default-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'";
}

/* ---- settings ---- */

function settings() {
  const env = k => String((globalThis.Netlify && Netlify.env.get(k)) || '').trim();
  const cfg = { supabaseUrl: env('SUPABASE_URL').replace(/\/+$/, ''), supabaseKey: env('SUPABASE_PUBLISHABLE_KEY'), secret: env('ATLAS_SESSION_SECRET') };
  const missing = [!/^https:\/\/[a-z0-9-]+\.supabase\.co$/.test(cfg.supabaseUrl) && 'SUPABASE_URL', !cfg.supabaseKey && 'SUPABASE_PUBLISHABLE_KEY',
    cfg.secret.length < 32 && 'ATLAS_SESSION_SECRET (32 characters or more)'].filter(Boolean);
  if (missing.length) { console.error('The Atlas sign-in is locked until these are set:', missing.join(', ')); return null; }
  return cfg;
}

// Only addresses under /clients/ or /team/, with a plain query, so the round trip can't be turned into a redirect
// elsewhere. A path that changes when resolved (dot segments, %2e%2e) is refused rather than trusted.
function safeReturn(r) {
  const fallback = '/clients/';
  if (typeof r !== 'string' || r.length > 400) return fallback;
  const [path, query = '', extra] = r.split('?');
  if (extra !== undefined || !/^\/(clients|team)(\/[A-Za-z0-9._~%\-\/]*)?$/.test(path) || path.includes('//')) return fallback;
  if (!/^[A-Za-z0-9._~%\-=&,+]*$/.test(query)) return fallback;
  try { if (new URL(path, 'https://atlas.invalid').pathname !== path) return fallback; } catch (e) { return fallback; }
  return query ? `${path}?${query}` : path;
}

/* ---- sealed values: AES-GCM under a key derived from the session secret, so the refresh token inside stays private ---- */

const encoder = new TextEncoder(), decoder = new TextDecoder();
const AAD = encoder.encode('rbx-atlas-v1');
const keys = new Map();
function keyFor(cfg) {
  if (!keys.has(cfg.secret)) {
    keys.set(cfg.secret, (async () => {
      const raw = await crypto.subtle.importKey('raw', encoder.encode(cfg.secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
      const derived = await crypto.subtle.sign('HMAC', raw, encoder.encode('atlas-sign-in-v1'));
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
    if (purpose === 'session' && !(typeof obj.e === 'string' && Array.isArray(obj.a) && typeof obj.r === 'string' && Number.isFinite(obj.c))) return null;
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
  const headers = new Headers({ location, 'cache-control': 'no-store' });
  for (const c of cookies) headers.append('set-cookie', c);
  return new Response(null, { status, headers });
}
function withCookies(res, cookies) {
  for (const c of cookies) res.headers.append('set-cookie', c);
  return res;
}
function text(status, body) {
  return new Response(body, { status, headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store', 'x-robots-tag': 'noindex, nofollow' } });
}
function esc(s) {
  return String(s).replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
}
// A page in the Atlas's own look (atlas.css's guard card, as on the 404 page).
function page(status, title, textHtml, action, extra = '', secondary = null, cookies = []) {
  const headers = new Headers(PAGE_HEADERS);
  for (const c of cookies) headers.append('set-cookie', c);
  return new Response(`<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>${title.replace(/<[^>]*>/g, '')} · RenewaBlox Atlas</title><link rel="icon" href="/favicon.ico" sizes="any">
<link rel="stylesheet" href="/assets/atlas.css?v=6a0e7230">
<style>.guard .list{list-style:none;margin:18px 0 0;padding:0;text-align:left}.guard .list li{margin:0 0 8px}
.guard .list a{display:block;padding:12px 16px;border:1px solid rgba(18,71,94,.18);border-radius:12px;text-decoration:none;font-weight:600}
.guard .sub{display:block;margin-top:14px;font-size:14px}.guard .btn+br+.btn{margin-top:10px}
.guard .field{font:inherit;padding:12px 14px;border:1px solid rgba(255,255,255,.28);border-radius:12px;background:#fff;color:#0d1b23}</style></head>
<body><div class="guard"><div><img src="/assets/logos/renewablox-wordmark-dark.png" alt="RenewaBlox" width="175" height="20" style="margin:0 auto">
<h1>${title}</h1><p>${textHtml}</p>${extra.startsWith('<script') ? '' : extra}
${[].concat(action || []).map(a => `<a class="btn btn--primary" href="${esc(a.href)}">${a.label}</a>`).join('<br>')}
${secondary ? `<a class="sub" href="${esc(secondary.href)}">${secondary.label}</a>` : ''}</div></div>
${extra.startsWith('<script') ? extra : ''}</body></html>`, { status, headers });
}
