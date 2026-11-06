// Tests for ai.renewablox.com's sign-in (netlify/edge-functions/ai-gate.js), against a stand-in Supabase and Google and
// a test set of header rules. Run:  node ai/tests/gate.test.mjs   (Node 22 or later; no packages)
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
const quiet = console.error; console.error = () => {};   // the gate logs refusals; the assertions say what matters

const ENV = { SUPABASE_URL: 'https://enghoowpiwopsfabfurx.supabase.co', SUPABASE_PUBLISHABLE_KEY: 'sb_publishable_test', AI_SESSION_SECRET: 'y'.repeat(40) };
env = { ...ENV };
// Supabase's token exchange and Google's userinfo, stood in: sb.token answers the exchange, sb.google answers userinfo
const sb = { calls: [], token: null, google: null };
const json = (status, obj) => new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });
globalThis.fetch = async (url, init) => {
  assert.ok(init.signal instanceof AbortSignal, 'every outside call has a time limit');
  sb.calls.push({ url: String(url), init });
  if (String(url) === ENV.SUPABASE_URL + '/auth/v1/token?grant_type=pkce') return sb.token(JSON.parse(init.body));
  if (String(url) === 'https://openidconnect.googleapis.com/v1/userinfo') return sb.google(init.headers.authorization);
  throw new Error('unexpected fetch ' + url);
};

const { default: gate, config, safeReturn, staff, headersFor, canonical, seal } =
  await import(pathToFileURL(join(TMP, 'edge-functions', 'ai-gate.js')).href);

const O = 'https://ai.renewablox.com', HOST = 'ai.renewablox.com';
const SESSION = '__Host-rbx_ai', STATE = '__Host-rbx_ai_signin';
let nexts = 0;
const ctx = { next: async () => { nexts++; return new Response('STATIC', { status: 200, headers: { 'content-type': 'text/html', 'content-security-policy': 'from-origin' } }); } };
const req = (path, { cookie = '', page = true, method = 'GET', origin = O } = {}) =>
  new Request(origin + path, { method, headers: { cookie, ...(page ? { 'sec-fetch-dest': 'document', accept: 'text/html' } : { accept: '*/*' }) } });
const setCookies = res => res.headers.getSetCookie();
const cookieVal = (res, name) => { const c = setCookies(res).find(c => c.startsWith(name + '=')); return c ? c.split(';')[0].slice(name.length + 1) : null; };
const google = (email, verified = true, hd = 'renewablox.com') => ({ provider: 'google', identity_data: { email, email_verified: verified, ...(hd ? { custom_claims: { hd } } : {}) } });
const user = (email, ...identities) => ({ email, identities: identities.length ? identities : [google(email)] });
const userinfo = (email, verified = true, hd = 'renewablox.com') => ({ sub: '1', email, email_verified: verified, ...(hd ? { hd } : {}) });

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

// ---- one spelling for every address, before anything else ----
for (const [given, want] of [['//eunice/', '/eunice/'], ['///oscar/', '/oscar/'], ['/%65unice/', '/eunice/'], ['/EUNICE/', '/eunice/'],
  ['/eunice%2Findex.html', '/eunice/index.html'], ['/%2F%2Feunice/', '/eunice/'], ['/Access/', '/access/'], ['/eunice//index.html', '/eunice/index.html']]) {
  assert.equal(canonical(given), want, `canonical(${given})`);
  const r = await gate(req(given + '?x=1'), ctx);
  assert.equal(r.status, 301, `${given} is sent to its one spelling`); assert.equal(r.headers.get('location'), want + '?x=1');
}
for (const p of ['/eunice/', '/assets/atlas.css', '/a%20b/', '/oscar/%E2%82%AC']) assert.equal(canonical(p), p.replace('%e2', '%E2'));
assert.equal(nexts, 0);
ok('every other spelling of an address is sent to its one spelling, so the checks and headers below always apply');

// ---- without a session, nothing of the site is served ----
const GATED = ['/', '/index.html', '/oscar/', '/oscar/index.html', '/oscar', '/eunice', '/eunice/', '/eunice/index.html',
  '/eunice/../oscar/', '/atlas', '/atlas/', '/atlas/clients/srv/', '/investors/x/', '/assets/atlas.css', '/assets/fonts/garet-book.woff2',
  '/assets/logos/renewablox-wordmark-light.png', '/robots.txt', '/404.html', '/favicon.ico', '/nope/', '/accessx', '/access-x/',
  '/.netlify/functions/x', '/eunice/?x=1', '/a%20b/'];
for (const p of GATED) {
  let r = await gate(req(p), ctx);
  assert.equal(r.status, 303, `${p}: a page asks to sign in`);
  assert.match(r.headers.get('location'), /^\/access\/\?r=/, `${p}: to the sign-in`);
  r = await gate(req(p, { page: false }), ctx);
  assert.equal(r.status, 401, `${p}: a file isn't served`);
  r = await gate(req(p, { method: 'POST' }), ctx);
  assert.equal(r.status, 401, `${p}: nor is a POST`);
  r = await gate(req(p, { method: 'HEAD' }), ctx);
  assert.equal(r.status, 401, `${p}: nor a HEAD`);
}
assert.equal(nexts, 0, 'nothing reached the site');
assert.equal((await gate(req('/eunice/?x=1'), ctx)).headers.get('location'), '/access/?r=%2Feunice%2F%3Fx%3D1');
ok(`without a session none of ${GATED.length} addresses (pages, files, assets, the proxied Atlas, odd ones) reaches the site`);

// a cookie that isn't a session of ours: tampered with, empty, the Atlas's, the old name, the sign-in state
for (const cookie of [`${SESSION}=abc.def`, `${SESSION}=`, 'rbx_atlas=abc.def', 'rbx_ai=abc.def', `${SESSION}=a.b.c`]) {
  assert.equal((await gate(req('/eunice/', { cookie }), ctx)).status, 303);
}
const stateOnly = cookieVal(await gate(req('/access/start?r=%2F'), ctx), STATE);
assert.equal((await gate(req('/eunice/', { cookie: `${SESSION}=${stateOnly}` }), ctx)).status, 303, 'the sign-in state is no session');
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
  ['/eunice/?a=<script>', '/'], ['/eunice/?a=1?b', '/'], ['javascript:alert(1)', '/'], ['/' + 'x'.repeat(400), '/']]) {
  assert.equal(safeReturn(given), want, `safeReturn(${JSON.stringify(given)})`);
}
ok('the address to return to stays on this site and never loops back to the sign-in');

// ---- the round trip: start, Google through Supabase, callback ----
// u: the Supabase user the exchange answers with; g: Google's userinfo for this sign-in (null: Google refuses the
// token; NO_TOKEN: Supabase hands back no Google token)
const NO_TOKEN = Symbol('no Google token');
async function signIn(u, g = u && userinfo(u.email.toLowerCase()), { origin = O, back = '%2Feunice%2F' } = {}) {
  const s = await gate(req(`/access/start?r=${back}`, { origin }), ctx);
  assert.equal(s.status, 303);
  const auth = new URL(s.headers.get('location'));
  assert.equal(auth.origin + auth.pathname, ENV.SUPABASE_URL + '/auth/v1/authorize');
  const q = auth.searchParams;
  assert.equal(q.get('provider'), 'google'); assert.equal(q.get('redirect_to'), origin + '/access/callback');
  assert.equal(q.get('code_challenge_method'), 's256'); assert.equal(q.get('hd'), 'renewablox.com'); assert.equal(q.get('prompt'), 'select_account');
  const state = cookieVal(s, STATE), sc = setCookies(s)[0];
  assert.ok(state && sc.includes('Path=/;') && sc.includes('HttpOnly') && sc.includes('Secure') && !/domain=/i.test(sc), 'a __Host- cookie');
  sb.token = body => {
    assert.equal(createHash('sha256').update(body.code_verifier).digest('base64url'), q.get('code_challenge'), 'PKCE: the verifier matches the challenge');
    assert.equal(body.auth_code, 'the-code');
    if (!u) return json(400, { error: 'invalid_grant' });
    return json(200, { access_token: 'at', refresh_token: 'rt', user: u, ...(g === NO_TOKEN ? {} : { provider_token: 'google-token' }) });
  };
  sb.google = auth => { assert.equal(auth, 'Bearer google-token'); return g ? json(200, g) : json(401, { error: 'invalid_token' }); };
  return gate(req('/access/callback?code=the-code', { cookie: `${STATE}=${state}`, origin }), ctx);
}

r = await signIn(user('Ann.Smith@RenewaBlox.com', google('ann.smith@renewablox.com')), userinfo('Ann.Smith@renewablox.com'));
assert.equal(r.status, 200);
html = await r.text();
assert.ok(html.includes('location.replace("/eunice/"'), 'back to the page asked for');
assert.ok(html.includes("sessionStorage.getItem('rbx.ai.hash')"), 'with its #fragment put back');
const session = cookieVal(r, SESSION);
assert.ok(session && session.includes('.'));
const ck = setCookies(r).find(c => c.startsWith(SESSION + '='));
assert.ok(ck.includes('Path=/;') && ck.includes('HttpOnly') && ck.includes('Secure') && ck.includes('SameSite=Lax') && ck.includes('Max-Age=43200') && !/domain=/i.test(ck));
assert.ok(setCookies(r).some(c => c.startsWith(STATE + '=;')), 'the sign-in state is cleared');
assert.equal(sb.calls.find(c => c.url.includes('/auth/v1/token')).init.headers.apikey, ENV.SUPABASE_PUBLISHABLE_KEY);
ok('an account of RenewaBlox\'s Workspace, confirmed by Google, signs in for 12 hours and goes back to the page with its #fragment');

// on a deploy preview the round trip comes back to the preview, and its session is the preview's alone
const PREVIEW = 'https://deploy-preview-7--renewablox-ai.netlify.app';
r = await signIn(user('ann@renewablox.com'), userinfo('ann@renewablox.com'), { origin: PREVIEW });
assert.equal(r.status, 200);
const previewSession = cookieVal(r, SESSION);
assert.equal((await gate(req('/eunice/', { cookie: `${SESSION}=${previewSession}`, origin: PREVIEW }), ctx)).status, 200);
assert.equal((await gate(req('/eunice/', { cookie: `${SESSION}=${previewSession}` }), ctx)).status, 303, 'a preview\'s session opens nothing in production');
assert.equal((await gate(req('/eunice/', { cookie: `${SESSION}=${session}`, origin: PREVIEW }), ctx)).status, 303, 'nor production\'s on a preview');
ok('a deploy preview signs in on its own address, and its sessions and production\'s don\'t open each other');

// ---- with a session: the site, with its own headers ----
const before = nexts;
for (const [p, policy] of [['/eunice/', 'eunice-policy'], ['/eunice/index.html', 'eunice-policy'], ['/oscar/', 'oscar-policy'],
  ['/', 'home-policy'], ['/index.html', 'home-policy'], ['/atlas/market/', 'from-origin'], ['/404.html', 'from-origin']]) {
  r = await gate(req(p, { cookie: `${SESSION}=${session}` }), ctx);
  assert.equal(r.status, 200, `${p} served`);
  assert.equal(r.headers.get('content-security-policy'), policy, `${p}: its own policy`);
  assert.equal(r.headers.get('x-robots-tag'), 'noindex, nofollow'); assert.equal(r.headers.get('cache-control'), 'private, no-store');
  assert.equal(r.headers.get('x-frame-options'), 'SAMEORIGIN');
}
assert.equal(nexts, before + 7);
r = await gate(req('/oscar/', { cookie: `${SESSION}=${session}` }), ctx); assert.equal(r.headers.get('referrer-policy'), 'no-referrer');
const css = { next: async () => { nexts++; return new Response('x', { headers: { 'content-type': 'text/css' } }); } };
r = await gate(req('/assets/atlas.css', { cookie: `foo=1; ${SESSION}=${session}`, page: false }), css);
assert.equal(r.status, 200); assert.equal(r.headers.get('cache-control'), 'private, no-cache');
assert.deepEqual(headersFor('/eunice/x'), { 'content-security-policy': 'eunice-policy', 'x-robots-tag': 'noindex' });
ok('signed in, every page and file is served with netlify.toml\'s headers for it, and no page is kept by the browser');

// a session from another secret opens nothing; nor does one forged far ahead, or for an address outside RenewaBlox
env = { ...ENV, AI_SESSION_SECRET: 'z'.repeat(40) };
assert.equal((await gate(req('/eunice/', { cookie: `${SESSION}=${session}` }), ctx)).status, 303);
env = { ...ENV };
const cfg = { secret: ENV.AI_SESSION_SECRET }, t = Math.floor(Date.now() / 1000);
for (const [what, obj] of [['dated a year ahead', { t: 'session', e: 'ann@renewablox.com', x: t + 365 * 86400 }],
  ['for another domain', { t: 'session', e: 'eve@example.com', x: t + 3600 }], ['a sign-in state', { t: 'state', v: 'x', r: '/', x: t + 300 }]]) {
  assert.equal((await gate(req('/eunice/', { cookie: `${SESSION}=${await seal(obj, cfg, HOST)}` }), ctx)).status, 303, what);
}
assert.equal((await gate(req('/eunice/', { cookie: `${SESSION}=${await seal({ t: 'session', e: 'ann@renewablox.com', x: t + 3600 }, cfg, HOST)}` }), ctx)).status, 200);
ok('a session sealed under another secret, dated further ahead than a sign-in lasts, or for anyone else opens nothing');

// 12 hours later it has run out
const realNow = Date.now;
Date.now = () => realNow() + 12 * 3600 * 1000 + 5000;
assert.equal((await gate(req('/eunice/', { cookie: `${SESSION}=${session}` }), ctx)).status, 303);
Date.now = realNow;
ok('a session runs out after 12 hours');

// ---- anyone else: a clear "not authorised", and no session ----
const NOT = [
  ['a Gmail account', user('bob@gmail.com', google('bob@gmail.com', true, null)), userinfo('bob@gmail.com', true, null)],
  ['a personal Google account on an @renewablox.com address (no Workspace)', user('ann@renewablox.com', google('ann@renewablox.com', true, null)), userinfo('ann@renewablox.com', true, null)],
  ['another Workspace', user('ann@renewablox.com', google('ann@renewablox.com', true, 'other.example')), userinfo('ann@renewablox.com', true, 'other.example')],
  ['Google placing it in no Workspace, whatever Supabase stored', user('ann@renewablox.com'), userinfo('ann@renewablox.com', true, null)],
  ['a look-alike domain', user('ann@renewablox.com.evil.example'), userinfo('ann@renewablox.com.evil.example')],
  ['a subdomain', user('ann@mail.renewablox.com'), userinfo('ann@mail.renewablox.com')],
  ['an unverified address', user('ann@renewablox.com', google('ann@renewablox.com', false)), userinfo('ann@renewablox.com', false)],
  ['Google unverified, whatever Supabase stored', user('ann@renewablox.com'), userinfo('ann@renewablox.com', false)],
  ['an identity for another address', user('ann@renewablox.com', google('bob@renewablox.com')), userinfo('ann@renewablox.com')],
  ['a Microsoft sign-in on an account with a stored Google identity (Google\'s token is for someone else)', user('ann@renewablox.com'), userinfo('eve@outlook.com', true, null)],
  ['no Google token handed back (a sign-in that wasn\'t Google\'s)', user('ann@renewablox.com'), NO_TOKEN],
  ['Google refusing the token', user('ann@renewablox.com'), null],
  ['a Microsoft account only', user('ann@renewablox.com', { provider: 'azure', identity_data: { email: 'ann@renewablox.com', email_verified: true, custom_claims: { tid: '9188040d-6c67-4c5b-b112-36a304b66dad' } } }), userinfo('ann@renewablox.com')],
  ['a second identity that disagrees', user('ann@renewablox.com', google('ann@renewablox.com'), { provider: 'azure', identity_data: { email: 'eve@outlook.com', email_verified: true } }), userinfo('ann@renewablox.com')],
  ['no address', { identities: [google('ann@renewablox.com')] }, userinfo('ann@renewablox.com')],
];
for (const [what, u, g] of NOT) {
  r = await signIn(u, g);
  assert.equal(r.status, 403, what);
  html = await r.text();
  assert.ok(html.includes('<h1>Not authorised</h1>'), `${what}: says so`);
  assert.ok(html.includes('@renewablox.com Google account'), `${what}: says who may`);
  assert.equal(cookieVal(r, SESSION), null, `${what}: no session`);
  assert.ok(html.includes('/access/start?r=%2Feunice%2F'), `${what}: offers another account`);
}
r = await signIn(user('<b>x</b>@gmail.com', google('<b>x</b>@gmail.com', true, null)), userinfo('<b>x</b>@gmail.com', true, null));
assert.ok((await r.text()).includes('&lt;b&gt;x&lt;/b&gt;@gmail.com'), 'the address shown is escaped');
assert.equal(staff('ann@renewablox.com', user('ann@renewablox.com')), true);
assert.equal(staff('ann@renewablox.com', user('ann@renewablox.com', google('ann@renewablox.com', true, null))), false);
ok(`${NOT.length} kinds of account or sign-in that aren't RenewaBlox staff signing in with Google get "Not authorised" and no session`);

// ---- a sign-in that goes wrong ----
assert.equal((await signIn(null)).status, 400);
r = await gate(req('/access/callback?error=access_denied&error_description=Your+RenewaBlox+account+is+locked.+Restore+it+at+evil.example'), ctx);
assert.equal(r.status, 401);
html = await r.text();
assert.ok(html.includes('You cancelled the Google sign-in.') && !html.includes('evil.example'), 'Google\'s error code in our words, never the address\'s text');
r = await gate(req('/access/callback?error=server_error&error_description=Visit+evil.example'), ctx);
assert.ok(!(await r.text()).includes('evil.example'));
assert.equal((await gate(req('/access/callback?code=x'), ctx)).status, 400, 'no state cookie');
assert.equal((await gate(req('/access/callback?code=x', { cookie: `${STATE}=abc.def` }), ctx)).status, 400, 'a state cookie of another secret');
const prevState = cookieVal(await gate(req('/access/start?r=%2F', { origin: PREVIEW }), ctx), STATE);
assert.equal((await gate(req('/access/callback?code=x', { cookie: `${STATE}=${prevState}` }), ctx)).status, 400, 'a preview\'s state in production');
globalThis.fetch = async () => { throw new Error('offline'); };
const s = await gate(req('/access/start?r=%2F'), ctx);
assert.equal((await gate(req('/access/callback?code=x', { cookie: `${STATE}=${cookieVal(s, STATE)}` }), ctx)).status, 400, 'Supabase unreachable');
ok('a refused, cancelled, expired, foreign or unreachable sign-in ends on a page that says so, in our words, with no session');

// ---- the rest of /access/ ----
r = await gate(req('/access/sign-out'), ctx);
assert.ok(setCookies(r).some(c => c.startsWith(SESSION + '=;') && c.includes('Max-Age=0')));
assert.equal(r.headers.get('clear-site-data'), '"cache"');
assert.equal((await gate(req('/access/other'), ctx)).status, 404);
ok('sign-out clears the session and the browser\'s copies of the pages; any other /access/ address is a 404 of the sign-in\'s own');

console.error = quiet;
console.log(`all ${n} groups passed`);
