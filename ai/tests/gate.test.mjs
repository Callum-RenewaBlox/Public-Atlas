// Tests for ai.renewablox.com's sign-in (netlify/edge-functions/ai-gate.js), against a stand-in Supabase and a test
// set of header rules. Run:  node ai/tests/gate.test.mjs   (Node 22 or later; no packages)
// The gate is copied into a temporary folder beside a test edge-lib/site.js, so the real (built) one isn't needed.
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, copyFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';

const HERE = dirname(fileURLToPath(import.meta.url));
const TMP = mkdtempSync(join(tmpdir(), 'ai-gate-'));
mkdirSync(join(TMP, 'edge-functions')); mkdirSync(join(TMP, 'edge-lib'));
copyFileSync(join(HERE, '..', 'netlify', 'edge-functions', 'ai-gate.js'), join(TMP, 'edge-functions', 'ai-gate.js'));
writeFileSync(join(TMP, 'edge-lib', 'site.js'), `export const HEADERS = [
  {"for": "/oscar/*", "values": {"Content-Security-Policy": "oscar-policy", "Referrer-Policy": "no-referrer"}},
  {"for": "/", "values": {"Content-Security-Policy": "home-policy"}},
  {"for": "/index.html", "values": {"Content-Security-Policy": "home-policy"}},
  {"for": "/eunice/*", "values": {"Content-Security-Policy": "eunice-policy", "X-Robots-Tag": "noindex"}}];
export const WORDMARK = 'data:image/png;base64,iVBORw0KGgo=';
`);
let env = {};
globalThis.Netlify = { env: { get: k => env[k] } };
let n = 0; const ok = s => console.log(`ok ${++n} ${s}`);

const ENV = { SUPABASE_URL: 'https://enghoowpiwopsfabfurx.supabase.co', SUPABASE_PUBLISHABLE_KEY: 'sb_publishable_test', AI_SESSION_SECRET: 'y'.repeat(40) };
env = { ...ENV };
const sb = { calls: [], token: null };
globalThis.fetch = async (url, init) => {
  assert.ok(init.signal instanceof AbortSignal, 'every Supabase call has a time limit');
  const body = JSON.parse(init.body || '{}'); sb.calls.push({ url: String(url), body, headers: init.headers });
  if (String(url) === ENV.SUPABASE_URL + '/auth/v1/token?grant_type=pkce') return sb.token(body);
  throw new Error('unexpected fetch ' + url);
};
const json = (status, obj) => new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });

const { default: gate, config, safeReturn, staff, headersFor } = await import(pathToFileURL(join(TMP, 'edge-functions', 'ai-gate.js')).href);

const O = 'https://ai.renewablox.com';
let nexts = 0;
const ctx = { next: async () => { nexts++; return new Response('STATIC', { status: 200, headers: { 'content-type': 'text/html', 'content-security-policy': 'from-origin' } }); } };
const req = (path, { cookie = '', page = true, method = 'GET', origin = O } = {}) =>
  new Request(origin + path, { method, headers: { cookie, ...(page ? { 'sec-fetch-dest': 'document', accept: 'text/html' } : { accept: '*/*' }) } });
const setCookies = res => res.headers.getSetCookie();
const cookieVal = (res, name) => { const c = setCookies(res).find(c => c.startsWith(name + '=')); return c ? c.split(';')[0].slice(name.length + 1) : null; };
const google = (email, verified = true, hd) => ({ provider: 'google', identity_data: { email, email_verified: verified, ...(hd ? { custom_claims: { hd } } : {}) } });
const user = (email, ...identities) => ({ email, identities: identities.length ? identities : [google(email)] });

// ---- the route: every address, failing closed ----
assert.equal(config.path, '/*'); assert.equal(config.onError, 'fail');
assert.ok(!('excludedPath' in config) && !('pattern' in config) && !('excludedPattern' in config));
ok('the sign-in runs on every address, and fails closed');

for (const bad of [{}, { ...ENV, AI_SESSION_SECRET: 'short' }, { ...ENV, SUPABASE_URL: 'https://evil.example.com' }, { ...ENV, SUPABASE_PUBLISHABLE_KEY: '' }]) {
  env = bad;
  for (const p of ['/', '/eunice/', '/access/', '/access/start', '/access/callback?code=x']) {
    const r = await gate(req(p), ctx); assert.equal(r.status, 503, `${p} locked without settings`);
  }
}
env = { ...ENV }; assert.equal(nexts, 0);
ok('locked, every address included, until all three settings are right');

// ---- without a session, nothing of the site is served ----
const GATED = ['/', '/index.html', '/oscar/', '/oscar/index.html', '/oscar', '/eunice', '/eunice/', '/eunice/index.html', '/EUNICE/',
  '//eunice/', '///oscar/', '/%65unice/', '/eunice/%2e%2e/oscar/', '/eunice/../oscar/', '/atlas', '/atlas/', '/atlas/clients/srv/',
  '/investors/x/', '/assets/atlas.css', '/assets/fonts/garet-book.woff2', '/assets/logos/renewablox-wordmark-light.png',
  '/robots.txt', '/404.html', '/favicon.ico', '/nope/', '/accessx', '/access-x/', '/Access/', '/.netlify/functions/x', '/eunice/?x=1'];
for (const p of GATED) {
  let r = await gate(req(p), ctx);
  assert.equal(r.status, 303, `${p}: a page asks to sign in`);
  assert.match(r.headers.get('location'), /^\/access\/\?r=/, `${p}: to the sign-in`);
  r = await gate(req(p, { page: false }), ctx);
  assert.equal(r.status, 401, `${p}: a file isn't served`);
  r = await gate(req(p, { method: 'POST' }), ctx);
  assert.equal(r.status, 401, `${p}: nor is a POST`);
}
assert.equal(nexts, 0, 'nothing reached the site');
assert.equal((await gate(req('/eunice/?x=1'), ctx)).headers.get('location'), '/access/?r=%2Feunice%2F%3Fx%3D1');
ok(`without a session none of ${GATED.length} addresses (pages, files, assets, proxied Atlas, odd spellings) reaches the site`);

// a cookie that isn't a session of ours: another secret's, tampered with, the Atlas's, empty
for (const cookie of ['rbx_ai=abc.def', 'rbx_ai=', 'rbx_atlas=abc.def', 'rbx_ai=a.b.c']) {
  const r = await gate(req('/eunice/', { cookie }), ctx); assert.equal(r.status, 303);
}
assert.equal(nexts, 0);
ok('a cookie that isn\'t a session of this site\'s opens nothing');

// ---- the sign-in page keeps the #fragment ----
let r = await gate(req('/access/?r=%2Feunice%2F'), ctx);
assert.equal(r.status, 401);
let html = await r.text();
assert.ok(html.includes('href="/access/start?r=%2Feunice%2F"'));
assert.ok(html.includes("sessionStorage.setItem('rbx.ai.hash',location.hash"));
assert.ok(html.includes('@renewablox.com'));
assert.match(r.headers.get('content-security-policy'), /frame-ancestors 'none'/);
assert.equal(r.headers.get('cache-control'), 'no-store');
assert.ok(!html.match(/(src|href)="(https?:)?\/\//), 'the page loads nothing from elsewhere');
assert.ok(!html.match(/(src|href)="\/(?!access)/), 'nor anything from this site beyond the sign-in');
ok('the sign-in page offers Google, keeps the #fragment, and loads nothing gated');

// ---- where to go back to: only this site, never the sign-in ----
for (const [given, want] of [['/eunice/', '/eunice/'], ['/oscar/?s=abc', '/oscar/?s=abc'], ['/', '/'],
  ['//evil.example.com', '/'], ['/\\evil.example.com', '/'], ['https://evil.example.com/', '/'], ['evil', '/'], ['', '/'], [null, '/'],
  ['/access/', '/'], ['/access/callback', '/'], ['/ACCESS/start', '/'], ['/./eunice/', '/'], ['/a/../eunice/', '/'],
  ['/eunice/?a=<script>', '/'], ['/eunice/?a=1?b', '/'], ['/' + 'x'.repeat(400), '/']]) {
  assert.equal(safeReturn(given), want, `safeReturn(${JSON.stringify(given)})`);
}
ok('the address to return to stays on this site and never loops back to the sign-in');

// ---- the round trip: start, Google through Supabase, callback ----
async function signIn(u, { origin = O, back = '%2Feunice%2F' } = {}) {
  const s = await gate(req(`/access/start?r=${back}`, { origin }), ctx);
  assert.equal(s.status, 303);
  const auth = new URL(s.headers.get('location'));
  assert.equal(auth.origin + auth.pathname, ENV.SUPABASE_URL + '/auth/v1/authorize');
  const q = auth.searchParams;
  assert.equal(q.get('provider'), 'google'); assert.equal(q.get('redirect_to'), origin + '/access/callback');
  assert.equal(q.get('code_challenge_method'), 's256'); assert.equal(q.get('hd'), 'renewablox.com'); assert.equal(q.get('prompt'), 'select_account');
  const state = cookieVal(s, 'rbx_ai_signin');
  assert.ok(state && setCookies(s)[0].includes('Path=/access') && setCookies(s)[0].includes('HttpOnly') && setCookies(s)[0].includes('Secure'));
  sb.token = body => {
    assert.equal(createHash('sha256').update(body.code_verifier).digest('base64url'), q.get('code_challenge'), 'PKCE: the verifier matches the challenge');
    assert.equal(body.auth_code, 'the-code');
    return u ? json(200, { access_token: 'at', refresh_token: 'rt', user: u }) : json(400, { error: 'invalid_grant' });
  };
  return gate(req('/access/callback?code=the-code', { cookie: `rbx_ai_signin=${state}`, origin }), ctx);
}

r = await signIn(user('Ann.Smith@RenewaBlox.com', google('ann.smith@renewablox.com', true, 'renewablox.com')));
assert.equal(r.status, 200);
html = await r.text();
assert.ok(html.includes('location.replace("/eunice/"'), 'back to the page asked for');
assert.ok(html.includes("sessionStorage.getItem('rbx.ai.hash')"), 'with its #fragment put back');
const session = cookieVal(r, 'rbx_ai');
assert.ok(session && session.includes('.'));
const sc = setCookies(r).find(c => c.startsWith('rbx_ai='));
assert.ok(sc.includes('Path=/') && sc.includes('HttpOnly') && sc.includes('Secure') && sc.includes('SameSite=Lax') && sc.includes('Max-Age=604800'));
assert.ok(setCookies(r).some(c => c.startsWith('rbx_ai_signin=;')), 'the sign-in state is cleared');
assert.equal(sb.calls.at(-1).headers.apikey, ENV.SUPABASE_PUBLISHABLE_KEY);
ok('a verified @renewablox.com Google account signs in, for a week, and goes back to the page with its #fragment');

// on a deploy preview the round trip comes back to the preview, not to ai.renewablox.com
const PREVIEW = 'https://deploy-preview-7--renewablox-ai.netlify.app';
assert.equal((await signIn(user('ann@renewablox.com'), { origin: PREVIEW })).status, 200);
ok('a deploy preview signs in on its own address');

// ---- with a session: the site, with its own headers ----
for (const [p, policy] of [['/eunice/', 'eunice-policy'], ['/eunice/index.html', 'eunice-policy'], ['/oscar/', 'oscar-policy'],
  ['/', 'home-policy'], ['/index.html', 'home-policy'], ['/atlas/market/', 'from-origin'], ['/404.html', 'from-origin']]) {
  const before = nexts;
  r = await gate(req(p, { cookie: `rbx_ai=${session}` }), ctx);
  assert.equal(nexts, before + 1, `${p} served`); assert.equal(r.status, 200);
  assert.equal(r.headers.get('content-security-policy'), policy, `${p}: its own policy`);
  assert.equal(r.headers.get('x-robots-tag'), 'noindex, nofollow'); assert.equal(r.headers.get('cache-control'), 'private, no-cache');
}
r = await gate(req('/oscar/', { cookie: `rbx_ai=${session}` }), ctx); assert.equal(r.headers.get('referrer-policy'), 'no-referrer');
r = await gate(req('/assets/atlas.css', { cookie: `foo=1; rbx_ai=${session}`, page: false }), ctx); assert.equal(r.status, 200);
assert.deepEqual(headersFor('/eunice/x'), { 'content-security-policy': 'eunice-policy', 'x-robots-tag': 'noindex' });
ok('signed in, every page and file is served with netlify.toml\'s headers for it');

// a session from another secret (the Atlas's, a changed one) opens nothing
env = { ...ENV, AI_SESSION_SECRET: 'z'.repeat(40) };
assert.equal((await gate(req('/eunice/', { cookie: `rbx_ai=${session}` }), ctx)).status, 303);
env = { ...ENV };
ok('a session sealed under another secret opens nothing (changing the secret signs everyone out)');

// a week later it has run out
const realNow = Date.now;
Date.now = () => realNow() + 7 * 24 * 3600 * 1000 + 5000;
assert.equal((await gate(req('/eunice/', { cookie: `rbx_ai=${session}` }), ctx)).status, 303);
Date.now = realNow;
ok('a session runs out after a week');

// ---- anyone else: a clear "not authorised", and no session ----
const NOT = [
  ['a Gmail account', user('bob@gmail.com')],
  ['a look-alike domain', user('ann@renewablox.com.evil.example')],
  ['a subdomain', user('ann@mail.renewablox.com')],
  ['another TLD', user('ann@renewablox.co')],
  ['an unverified address', user('ann@renewablox.com', google('ann@renewablox.com', false))],
  ['another Workspace (hd)', user('ann@renewablox.com', google('ann@renewablox.com', true, 'other.example'))],
  ['an identity for another address', user('ann@renewablox.com', google('bob@renewablox.com'))],
  ['a Microsoft account only', user('ann@renewablox.com', { provider: 'azure', identity_data: { email: 'ann@renewablox.com', email_verified: true, custom_claims: { tid: '9188040d-6c67-4c5b-b112-36a304b66dad' } } })],
  ['a second identity that disagrees', user('ann@renewablox.com', google('ann@renewablox.com'), { provider: 'azure', identity_data: { email: 'eve@outlook.com', email_verified: true } })],
  ['no address', { identities: [google('ann@renewablox.com')] }],
];
for (const [what, u] of NOT) {
  r = await signIn(u);
  assert.equal(r.status, 403, what);
  html = await r.text();
  assert.ok(html.includes('<h1>Not authorised</h1>'), `${what}: says so`);
  assert.ok(html.includes('@renewablox.com Google account'), `${what}: says who may`);
  assert.equal(cookieVal(r, 'rbx_ai'), null, `${what}: no session`);
  assert.ok(html.includes('/access/start?r=%2Feunice%2F'), `${what}: offers another account`);
}
r = await signIn(user('<b>x</b>@gmail.com', google('<b>x</b>@gmail.com')));
assert.ok((await r.text()).includes('&lt;b&gt;x&lt;/b&gt;@gmail.com'), 'the address shown is escaped');
assert.equal(staff('ann@renewablox.com', user('ann@renewablox.com')), true);
ok(`${NOT.length} kinds of account that aren't RenewaBlox staff get "Not authorised" and no session`);

// ---- a sign-in that goes wrong ----
assert.equal((await signIn(null)).status, 400);
r = await gate(req('/access/callback?error=access_denied&error_description=The+user+denied+access'), ctx);
assert.equal(r.status, 401); assert.ok((await r.text()).includes('The user denied access'));
assert.equal((await gate(req('/access/callback?code=x'), ctx)).status, 400, 'no state cookie');
assert.equal((await gate(req('/access/callback?code=x', { cookie: 'rbx_ai_signin=abc.def' }), ctx)).status, 400, 'a state cookie of another secret');
globalThis.fetch = async () => { throw new Error('offline'); };
const s = await gate(req('/access/start?r=%2F'), ctx);
assert.equal((await gate(req('/access/callback?code=x', { cookie: `rbx_ai_signin=${cookieVal(s, 'rbx_ai_signin')}` }), ctx)).status, 400, 'Supabase unreachable');
ok('a refused, expired, foreign or unreachable sign-in ends on a page that says so, with no session');

// ---- the rest of /access/ ----
r = await gate(req('/access/sign-out'), ctx);
assert.ok(setCookies(r).some(c => c.startsWith('rbx_ai=;') && c.includes('Max-Age=0')));
assert.equal((await gate(req('/access/other'), ctx)).status, 404);
assert.equal(nexts, 9, 'only the signed-in requests above reached the site');
ok('sign-out clears the session; any other /access/ address is a 404 of the sign-in\'s own');

console.log(`all ${n} groups passed`);
