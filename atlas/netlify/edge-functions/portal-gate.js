/* The investor portal's key: every request under /investors/portal/ passes through here first.

   The Investor Portal pack (and the Investor Atlas inside it) is reached from the members-only area of the Wix investor
   portal, whose button carries the key: ?k=<key>, where the key is the keyed hash of the access code that
   portal_key.py prints. It is the gate the Investor Portal kept when it was a Streamlit app, with the same key, so the
   links investors already have keep working once the button points here. Three ways in:
     * the key on the address. Opened as a page of its own, the key is taken off the address and a cookie remembers
       it; opened inside the Wix portal's frame, where a browser may refuse the cookie, the key stays on the address
       and every link and frame of the pack carries it on;
     * the cookie, on a later visit;
     * the code itself, typed into a prompt, for anyone sent the code by other means.
   Without PORTAL_PASSCODE set (Netlify > Project configuration > Environment variables, scope including Functions)
   the portal stays locked. Changing the code expires every key and cookie. The pack's files are also in the public
   repository: this protects the address, not the files.

   Netlify's _headers rules don't reach responses that pass through an edge function, so the pack's headers are set
   here, from the build's policies (atlas/build.py writes ../edge-lib/pages.js). */

import { CSP } from '../edge-lib/pages.js';

const COOKIE = 'rbx_portal';
const COOKIE_SECONDS = 30 * 24 * 3600;
const PORTAL = '/investors/portal/';
// The Wix site that frames the pack: its pages, its editor and its embed host.
const FRAMERS = "'self' https://www.renewablox.com https://renewablox.com https://*.wixsite.com https://*.wix.com https://*.filesusr.com";
const PACK_HEADERS = {
  'x-robots-tag': 'noindex, nofollow',
  'x-content-type-options': 'nosniff',
  'referrer-policy': 'same-origin',
  'cache-control': 'private, no-cache'
};

export default async (request, context) => {
  const url = new URL(request.url);
  const clean = canonical(url.pathname);
  if (clean !== url.pathname) return redirect(clean + url.search, [], 301);
  const code = String((globalThis.Netlify && Netlify.env.get('PORTAL_PASSCODE')) || '').trim();
  if (!code) {
    console.error('The investor portal is locked until PORTAL_PASSCODE is set.');
    return prompt(503, 'The portal isn&rsquo;t open yet', 'Its access code hasn&rsquo;t been set. Try again later.', null);
  }
  const token = await keyFor(code);
  const framed = request.headers.get('sec-fetch-dest') === 'iframe';

  if (request.method === 'POST') {
    // the code prompt: on the right code, back to the page with the key, which the rest of the gate then takes
    const form = await request.formData().catch(() => null);
    const entered = String((form && form.get('code')) || '').trim();
    const back = safeReturn(String((form && form.get('r')) || PORTAL));
    if (entered && (await same(entered, code))) return redirect(`${back}${back.includes('?') ? '&' : '?'}k=${token}`);
    return prompt(401, 'That code isn&rsquo;t right', 'Check the code in your portal invitation and try again.', back);
  }

  const key = url.searchParams.get('k') || '';
  const byKey = !!key && ((await same(key, token)) || (await same(key, code)));
  const byCookie = !byKey && (await same(readCookie(request, COOKIE), token));

  if (byKey && !framed && isPageRequest(request)) {
    // a page of its own: remember the key in a cookie and take it off the address
    url.searchParams.delete('k');
    return redirect(url.pathname + (url.search ? url.search : '') + url.hash, [cookie(token, false)]);
  }
  if (!byKey && !byCookie) {
    if (!isPageRequest(request)) return new Response('The investor portal needs its key.', { status: 401, headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' } });
    return prompt(401, 'RenewaBlox project pack', 'Enter the access code from your portal invitation to open the models.', safeReturn(url.pathname + url.search));
  }

  const res = await context.next();
  let out = new Response(res.body, res);
  // only the pack's own pages carry links; the models (model.html, megabytes each) and the Investor Atlas have none
  // to rewrite, and scanning them would spend the edge function's CPU budget for nothing
  if (byKey && (res.headers.get('content-type') || '').includes('text/html') && !/\/model\.html$/.test(url.pathname) &&
      !url.pathname.startsWith('/investors/portal/atlas/')) {
    // inside the portal's frame the cookie may be refused, so the pack's own links and frames carry the key on
    const html = await res.text();
    out = new Response(carryKey(html, token), res);
    out.headers.delete('content-length');
  }
  for (const [k, v] of Object.entries(PACK_HEADERS)) out.headers.set(k, v);
  out.headers.set('content-security-policy', policyFor(url.pathname));
  out.headers.delete('x-frame-options');
  if (byKey) out.headers.append('set-cookie', cookie(token, true));
  return out;
};

// Netlify picks the edge functions by the address as it was sent, but serves a file after folding a run of slashes,
// so a route of /investors/portal/* alone would let //investors/portal/… reach the pack without its key. The pattern
// takes in every spelling (any run of slashes, any case, an encoded slash), and the function sends each to its one
// spelling (canonical) first.
export const config = {
  pattern: '^/+[iI][nN][vV][eE][sS][tT][oO][rR][sS](?:/+|%2[fF])[pP][oO][rR][tT][aA][lL](?:[/%].*)?$'
};

// An address's one spelling: no run of slashes, %2F as the slash it stands for, /investors/portal in lower case, and
// the pack's own address with its slash (the cookie's path, so a return to /investors/portal finds the cookie).
export function canonical(path) {
  const parts = path.replace(/%2f/gi, '/').replace(/\/{2,}/g, '/').split('/');
  parts[1] = (parts[1] || '').toLowerCase();
  parts[2] = (parts[2] || '').toLowerCase();
  const p = parts.join('/');
  return p === PORTAL.slice(0, -1) ? PORTAL : p;
}

// Every address in the pack's markup that stays inside the portal (absolute under /investors/portal/, or a relative
// model.html / index.html) gets ?k= added; anything else is left as it is.
function carryKey(html, token) {
  return html.replace(/\b(href|src)="((?:\/investors\/portal\/[^"#?]*|(?:\.\/)?[a-z0-9_-]+\.html))(\?[^"#]*)?(#[^"]*)?"/gi,
    (m, attr, path, query, hash) => {
      if (/[?&]k=/.test(query || '')) return m;
      return `${attr}="${path}${query ? query + '&' : '?'}k=${token}${hash || ''}"`;
    });
}

function policyFor(path) {
  let best = '';
  for (const prefix of Object.keys(CSP)) if (path.startsWith(prefix) && prefix.length > best.length) best = prefix;
  const policy = best ? CSP[best] : "default-src 'self'; base-uri 'self'; form-action 'self'";
  return policy.replace(/;?\s*frame-ancestors[^;]*/g, '') + `; frame-ancestors ${FRAMERS}`;
}

// The portal's own pages only, with a plain query, so the prompt can't be turned into a redirect elsewhere.
function safeReturn(r) {
  const [path, query = '', extra] = String(r || '').split('?');
  if (extra !== undefined || !/^\/investors\/portal(\/[A-Za-z0-9._~%\-\/]*)?$/.test(path) || path.includes('//')) return PORTAL;
  const q = new URLSearchParams(query); q.delete('k');
  const qs = q.toString();
  if (!/^[A-Za-z0-9._~%\-=&,+]*$/.test(qs)) return PORTAL;
  try { if (new URL(path, 'https://atlas.invalid').pathname !== path) return PORTAL; } catch (e) { return PORTAL; }
  return qs ? `${path}?${qs}` : path;
}

/* ---- the key: hex HMAC-SHA-256 of "rbx-portal" under the code, as portal_key.py prints it ---- */

const encoder = new TextEncoder();
async function keyFor(code) {
  const k = await crypto.subtle.importKey('raw', encoder.encode(code), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = new Uint8Array(await crypto.subtle.sign('HMAC', k, encoder.encode('rbx-portal')));
  return Array.from(sig, b => b.toString(16).padStart(2, '0')).join('');
}
// Constant-time comparison of two strings (by their SHA-256, so the lengths don't show either).
async function same(a, b) {
  if (!a || !b) return false;
  const [x, y] = await Promise.all([a, b].map(s => crypto.subtle.digest('SHA-256', encoder.encode(String(s)))));
  const u = new Uint8Array(x), v = new Uint8Array(y);
  let diff = 0;
  for (let i = 0; i < u.length; i++) diff |= u[i] ^ v[i];
  return diff === 0;
}

/* ---- small things ---- */

function readCookie(request, name) {
  for (const part of (request.headers.get('cookie') || '').split(';')) {
    const i = part.indexOf('=');
    if (i > 0 && part.slice(0, i).trim() === name) return part.slice(i + 1).trim();
  }
  return '';
}
// A page of its own takes a first-party cookie; inside the portal's frame it can only be a partitioned one.
function cookie(token, framed) {
  return `${COOKIE}=${token}; Path=${PORTAL}; Max-Age=${COOKIE_SECONDS}; Secure; HttpOnly; ` + (framed ? 'SameSite=None; Partitioned' : 'SameSite=Lax');
}
function isPageRequest(request) {
  const dest = request.headers.get('sec-fetch-dest');
  return request.method === 'GET' && (dest === 'document' || dest === 'iframe' || (request.headers.get('accept') || '').includes('text/html'));
}
function redirect(location, cookies = [], status = 303) {
  const headers = new Headers({ location, 'cache-control': 'no-store' });
  for (const c of cookies) headers.append('set-cookie', c);
  return new Response(null, { status, headers });
}
function esc(s) {
  return String(s).replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
}
// The code prompt, in the Atlas's own look (atlas.css's guard card).
function prompt(status, title, text, back) {
  const form = back ? `<form method="post" action="${esc(PORTAL)}" style="margin-top:18px;display:grid;gap:10px">
<input type="hidden" name="r" value="${esc(back)}"><input name="code" type="password" autocomplete="current-password" required
placeholder="Access code" aria-label="Access code" style="font:inherit;padding:12px 14px;border:1px solid rgba(18,71,94,.25);border-radius:12px">
<button class="btn btn--primary" type="submit">Open the pack</button></form>` : '';
  return new Response(`<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>Investor portal · RenewaBlox Atlas</title><link rel="icon" href="/favicon.ico" sizes="any">
<link rel="stylesheet" href="/assets/atlas.css?v=6a0e7230"></head>
<body><div class="guard"><div><img src="/assets/logos/renewablox-wordmark-dark.png" alt="RenewaBlox" width="175" height="20" style="margin:0 auto">
<h1>${title}</h1><p>${text}</p>${form}</div></div></body></html>`, { status, headers: {
    'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'x-robots-tag': 'noindex, nofollow', 'x-content-type-options': 'nosniff',
    'content-security-policy': `default-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors ${FRAMERS}`
  } });
}
