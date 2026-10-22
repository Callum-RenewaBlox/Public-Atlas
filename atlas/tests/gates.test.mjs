// Tests for the two edge functions (netlify/edge-functions/atlas-gate.js and portal-gate.js), against a stand-in
// Supabase and a test list of pages. Run:  node atlas/tests/gates.test.mjs   (Node 22 or later; no packages)
// Each gate is copied into a temporary folder beside a test edge-lib/pages.js, so the real (built) one isn't needed.
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, copyFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const TMP = mkdtempSync(join(tmpdir(), 'atlas-gates-'));
mkdirSync(join(TMP, 'edge-functions')); mkdirSync(join(TMP, 'edge-lib'));
for (const f of ['atlas-gate.js', 'portal-gate.js']) copyFileSync(join(HERE, '..', 'netlify', 'edge-functions', f), join(TMP, 'edge-functions', f));
writeFileSync(join(TMP, 'edge-lib', 'pages.js'), `export const PAGES = {
  '/clients/srv/': { client: 'srv', title: 'SRV Atlas', views: { '3d': '3d.html', siting: 'siting.html' }, list: true },
  '/clients/srv/contractor/': { client: 'srv', title: 'SRV Contractor Atlas', list: true },
  '/clients/bryn/': { client: 'bryn', title: 'Bryn Atlas', views: { '3d': '3d.html' }, list: true },
  '/team/keith-huntly/': { client: '*', title: 'Keith & Huntly', list: true },
};
export const CSP = { '/clients/srv/': "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com", '/team/': "default-src 'self'", '/investors/portal/': "default-src 'self'; script-src 'self' 'unsafe-inline'; frame-src 'self'; frame-ancestors 'self'" };
export const REDIRECTS = { '/clients/srv/3d-sim/': '/clients/srv/?view=3d' };
`);
let env = {};
globalThis.Netlify = { env: { get: k => env[k] } };
let n = 0; const ok = s => console.log(`ok ${++n} ${s}`);

// ---- the sign-in (atlas-gate.js) ----
const ENV = { SUPABASE_URL: 'https://enghoowpiwopsfabfurx.supabase.co', SUPABASE_PUBLISHABLE_KEY: 'sb_publishable_test', ATLAS_SESSION_SECRET: 'x'.repeat(40) };
env = { ...ENV };
const sb = { calls: [], token: null, rpc: null, refresh: null };
globalThis.fetch = async (url, init) => {
  assert.ok(init.signal instanceof AbortSignal, 'every Supabase call has a time limit');
  const body = JSON.parse(init.body || '{}'); sb.calls.push({ url: String(url), body, headers: init.headers });
  const json = (status, obj) => new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });
  if (String(url).includes('grant_type=pkce')) return sb.token(body);
  if (String(url).includes('grant_type=refresh_token')) return sb.refresh(body);
  if (String(url).endsWith('/rest/v1/rpc/atlas_my_access')) return sb.rpc(init.headers.authorization);
  throw new Error('unexpected fetch ' + url);
};
const json = (status, obj) => new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });
{
const { default: gate, config } = await import(pathToFileURL(join(TMP, 'edge-functions', 'atlas-gate.js')).href);

const O = 'https://atlas.renewablox.com';
const ctx = { next: async () => new Response('STATIC', { status: 200, headers: { 'content-type': 'text/html', 'content-security-policy': 'from-headers-file' } }) };
const req = (path, { cookie = '', page = true, method = 'GET' } = {}) => new Request(O + path, { method, headers: { cookie, ...(page ? { 'sec-fetch-dest': 'document', accept: 'text/html' } : { accept: '*/*' }) } });
const setCookies = res => res.headers.getSetCookie();
const cookieVal = (res, name) => { const c = setCookies(res).find(c => c.startsWith(name + '=')); return c ? c.split(';')[0].slice(name.length + 1) : null; };
const user = (email, verified = true, provider = 'google') => ({ email, identities: [{ provider, identity_data: { email, email_verified: verified } }] });

// settings
env = {}; let r = await gate(req('/clients/srv/'), ctx); assert.equal(r.status, 503); env = { ...ENV }; ok('locked without settings');
{
  const routes = [].concat(config.pattern).map(p => new RegExp(p));
  const routed = p => routes.some(re => re.test(p));
  for (const p of ['/clients', '/clients/', '/clients/srv/3d.html', '//clients/srv/', '///team/keith-huntly/', '/CLIENTS/srv/', '/Team/',
    '/clients%2Fsrv/', '/access', '/access/callback', '//access/start']) assert.ok(routed(p), p);
  for (const p of ['/', '/market/', '/clientsx/', '/teamwork/', '/accessible/', '/assets/clients/x.png', '/investors/portal/']) assert.ok(!routed(p), p);
}
ok('routes: every spelling of /clients, /team and /access, and nothing else');
for (const [from, to] of [['//clients/srv/', '/clients/srv/'], ['///clients//srv///3d.html', '/clients/srv/3d.html'],
  ['/CLIENTS/SRV/?view=3d', '/clients/srv/?view=3d'], ['/clients%2Fsrv%2F', '/clients/srv/'], ['//team/keith-huntly/', '/team/keith-huntly/'],
  ['//access/start?r=%2Fclients%2F', '/access/start?r=%2Fclients%2F']]) {
  r = await gate(req(from), ctx); assert.equal(r.status, 301, from); assert.equal(r.headers.get('location'), to, from);
}
ok('any other spelling -> 301 to the one spelling, before anything else');

// signed out
r = await gate(req('/clients/srv/?view=3d'), ctx); assert.equal(r.status, 303); assert.equal(r.headers.get('location'), '/access/?r=' + encodeURIComponent('/clients/srv/?view=3d')); ok('signed-out page -> sign-in, keeping ?view');
r = await gate(req('/clients/srv/aerial.jpg', { page: false }), ctx); assert.equal(r.status, 401); ok('signed-out asset -> 401');
r = await gate(req('/access/?r=' + encodeURIComponent('/clients/srv/')), ctx); assert.equal(r.status, 401); let html = await r.text();
assert.match(html, /href="\/access\/start\?r=%2Fclients%2Fsrv%2F"/); assert.match(r.headers.get('content-security-policy'), /frame-ancestors 'none'/); ok('sign-in page');
for (const bad of ['//evil.com/x', 'https://evil.com', '/clients/../oscar', '/clients/%2e%2e/x', '/elsewhere/', '/clients/srv/?x=<b>', '/clients//srv/', '/clients/srv/?a=1?b=2']) {
  r = await gate(req('/access/?r=' + encodeURIComponent(bad)), ctx); html = await r.text();
  assert.match(html, /href="\/access\/start\?r=%2Fclients%2F"/, bad);
}
ok('return address confined to /clients and /team');

// start
r = await gate(req('/access/start?r=' + encodeURIComponent('/clients/srv/?view=3d')), ctx); assert.equal(r.status, 303);
const auth = new URL(r.headers.get('location')); assert.equal(auth.origin + auth.pathname, ENV.SUPABASE_URL + '/auth/v1/authorize');
assert.equal(auth.searchParams.get('provider'), 'google'); assert.equal(auth.searchParams.get('redirect_to'), O + '/access/callback');
assert.equal(auth.searchParams.get('code_challenge_method'), 's256');
const state = cookieVal(r, 'rbx_atlas_signin'); assert.ok(state); assert.match(setCookies(r)[0], /Path=\/access;.*HttpOnly/); ok('start -> Supabase authorize with PKCE');

// callback
r = await gate(req('/access/callback?code=abc'), ctx); assert.equal(r.status, 400); ok('callback without state -> expired');
r = await gate(req('/access/callback?error=access_denied&error_description=%3Cscript%3E'), ctx); html = await r.text(); assert.ok(!html.includes('<script>x'), 'escaped'); assert.match(html, /&lt;script&gt;/); ok('callback error escaped');
sb.token = async body => {
  const digest = Buffer.from(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(body.code_verifier))).toString('base64url');
  assert.equal(digest, auth.searchParams.get('code_challenge')); assert.equal(body.auth_code, 'abc');
  return json(200, { access_token: 'AT1', refresh_token: 'RT1', user: user('Client@Example.com') });
};
sb.rpc = async bearer => { assert.equal(bearer, 'Bearer AT1'); return json(200, ['srv']); };
r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + state }), ctx); assert.equal(r.status, 200);
let session = cookieVal(r, 'rbx_atlas'); assert.ok(session); html = await r.text(); assert.match(html, /location\.replace\("\/clients\/srv\/\?view=3d"/);
{
  // the page's script puts the #fragment kept at the sign-in page back on the address (the outreach page's #/plan among them)
  const script = html.match(/<script>(var h=[\s\S]*?)<\/script>/)[1];
  const run = hash => { let went = null; const store = { 'rbx.atlas.hash': hash };
    new Function('sessionStorage', 'location', script)({ getItem: k => store[k] ?? null, removeItem: k => delete store[k] }, { replace: u => { went = u; } });
    return went; };
  assert.equal(run('#/plan'), '/clients/srv/?view=3d#/plan'); assert.equal(run('#v=hydro&z=5'), '/clients/srv/?view=3d#v=hydro&z=5');
  assert.equal(run('#x"<b>'), '/clients/srv/?view=3d'); assert.equal(run(''), '/clients/srv/?view=3d');
}
assert.ok(!session.includes('RT1') && !Buffer.from(session.split('.')[1], 'base64url').toString().includes('RT1'), 'refresh token encrypted'); ok('callback -> session (encrypted), back to the page');
sb.token = async () => json(200, { access_token: 'AT1', refresh_token: 'RT1', user: user('client@example.com', false) });
r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + state }), ctx); assert.equal(r.status, 403); assert.equal(cookieVal(r, 'rbx_atlas'), null); ok('unverified Google address refused');
sb.token = async () => json(200, { access_token: 'AT1', refresh_token: 'RT1', user: user('client@example.com', true, 'email') });
r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + state }), ctx); assert.equal(r.status, 403); ok('non-Google identity refused');
sb.token = async () => json(200, { access_token: 'AT2', refresh_token: 'RT2', user: user('stranger@example.com') }); sb.rpc = async () => json(200, []);
r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + state }), ctx); assert.equal(r.status, 403); assert.equal(cookieVal(r, 'rbx_atlas'), null); ok('nothing shared -> 403, no session');
sb.token = async () => json(400, { error: 'invalid_grant' });
r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + state }), ctx); assert.equal(r.status, 400); ok('code refused by Supabase');
sb.token = async () => json(200, { access_token: 'AT1', refresh_token: 'RT1', user: user('client@example.com') }); sb.rpc = async () => json(500, {});
r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + state }), ctx); assert.equal(r.status, 503); ok('access unknown -> 503, no session');

// signed in as a client of srv
const c = 'rbx_atlas=' + session;
r = await gate(req('/clients/srv/', { cookie: c }), ctx); assert.equal(r.status, 200); assert.equal(await r.text(), 'STATIC');
assert.equal(r.headers.get('content-security-policy'), "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com");
assert.equal(r.headers.get('x-robots-tag'), 'noindex, nofollow'); assert.equal(r.headers.get('cache-control'), 'private, no-cache'); assert.equal(r.headers.get('referrer-policy'), 'strict-origin-when-cross-origin'); ok('client opens own page with its policy');
r = await gate(req('/clients/srv/aerial.jpg', { cookie: c, page: false }), ctx); assert.equal(r.status, 200); ok('and its files');
r = await gate(req('/clients/srv/?view=3d', { cookie: c }), ctx); assert.ok(r instanceof URL); assert.equal(r.pathname, '/clients/srv/3d.html'); ok('?view routes to the view file');
r = await gate(req('/clients/srv/?view=nope', { cookie: c }), ctx); assert.equal(await r.text(), 'STATIC'); ok('unknown view -> the page');
r = await gate(req('/clients/srv/?view=constructor', { cookie: c }), ctx); assert.equal(await r.text(), 'STATIC'); ok('prototype keys are not views');
r = await gate(req('/clients/srv/3d.html', { cookie: c }), ctx); assert.match(r.headers.get('content-security-policy'), /cdnjs/); ok('view file takes the folder policy');
r = await gate(req('/clients/bryn/', { cookie: c }), ctx); assert.equal(r.status, 403); ok('another client\'s page refused');
r = await gate(req('/clients/bryn/model.glb', { cookie: c, page: false }), ctx); assert.equal(r.status, 403); ok('and its files');
r = await gate(req('/team/keith-huntly/', { cookie: c }), ctx); assert.equal(r.status, 403); ok('team page refused to a client');
r = await gate(req('/clients/srv', { cookie: c }), ctx); assert.equal(r.status, 301); assert.equal(r.headers.get('location'), '/clients/srv/'); ok('slash added');
r = await gate(req('/clients/srv/index.html?view=3d', { cookie: c }), ctx); assert.equal(r.status, 301); assert.equal(r.headers.get('location'), '/clients/srv/?view=3d'); ok('index.html address goes to the folder, keeping ?view');
r = await gate(req('/clients/srv/3d-sim/', { cookie: c }), ctx); assert.equal(r.status, 301); assert.equal(r.headers.get('location'), '/clients/srv/?view=3d'); ok('moved page');
r = await gate(req('/clients/', { cookie: c }), ctx); html = await r.text(); assert.match(html, /SRV Atlas/); assert.match(html, /SRV Contractor/); assert.ok(!/Bryn|Keith/.test(html)); ok('list shows only what is shared');
r = await gate(req('/clients/srv/', { cookie: 'rbx_atlas=' + session.slice(0, -2) + 'AA' }), ctx); assert.equal(r.status, 303); ok('tampered cookie = signed out');
env = { ...ENV, ATLAS_SESSION_SECRET: 'y'.repeat(40) }; r = await gate(req('/clients/srv/', { cookie: c }), ctx); assert.equal(r.status, 303); env = { ...ENV }; ok('new secret signs everyone out');

// access asked again after ten minutes
const realNow = Date.now; Date.now = () => realNow() + 11 * 60 * 1000;
sb.refresh = async body => { assert.equal(body.refresh_token, 'RT1'); return json(200, { access_token: 'AT3', refresh_token: 'RT3', user: { email: 'client@example.com' } }); };
sb.rpc = async bearer => { assert.equal(bearer, 'Bearer AT3'); return json(200, ['bryn', 'srv']); };
r = await gate(req('/clients/bryn/', { cookie: c }), ctx); assert.equal(r.status, 200); const s2 = cookieVal(r, 'rbx_atlas'); assert.ok(s2 && s2 !== session); ok('stale access refreshed: newly shared page opens');
r = await gate(req('/clients/bryn/?view=3d', { cookie: c }), ctx); assert.equal(r.status, 303); assert.ok(cookieVal(r, 'rbx_atlas')); ok('refresh before a view rewrite goes back to the browser first');
sb.refresh = async () => json(400, { error: 'invalid_grant' });
r = await gate(req('/clients/srv/', { cookie: c }), ctx); assert.equal(r.status, 303); assert.match(r.headers.get('location'), /^\/access\//); assert.equal(cookieVal(r, 'rbx_atlas'), ''); ok('refused refresh -> signed out');
sb.refresh = async () => json(200, { access_token: 'AT4', refresh_token: 'RT4', user: { email: 'client@example.com' } }); sb.rpc = async () => json(200, []);
r = await gate(req('/clients/srv/', { cookie: c }), ctx); assert.equal(r.status, 303); ok('all access removed -> signed out');
sb.refresh = async () => { throw new Error('network'); };
r = await gate(req('/clients/srv/', { cookie: c }), ctx); assert.equal(r.status, 200); ok('Supabase unreachable: a recent answer still holds');
Date.now = () => realNow() + 25 * 3600 * 1000;
r = await gate(req('/clients/srv/', { cookie: c }), ctx); assert.equal(r.status, 503); ok('... but not a day-old one');
r = await gate(req('/clients/srv/aerial.jpg', { cookie: c, page: false }), ctx); assert.equal(r.status, 401); ok('files refused once the answer is over six hours old');
Date.now = () => realNow() + 5 * 3600 * 1000;
r = await gate(req('/clients/srv/aerial.jpg', { cookie: c, page: false }), ctx); assert.equal(r.status, 200); ok('files served on a recent answer without asking again');
Date.now = () => realNow() + 25 * 3600 * 1000;
Date.now = () => realNow() + 31 * 24 * 3600 * 1000;
r = await gate(req('/clients/srv/', { cookie: c }), ctx); assert.equal(r.status, 303); ok('session expires after 30 days');
Date.now = realNow;

// a team member
sb.token = async () => json(200, { access_token: 'AT5', refresh_token: 'RT5', user: user('callum@renewablox.com') }); sb.rpc = async () => json(200, ['*']);
r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + state }), ctx); const team = 'rbx_atlas=' + cookieVal(r, 'rbx_atlas');
for (const p of ['/team/keith-huntly/', '/clients/bryn/', '/clients/srv/contractor/']) { r = await gate(req(p, { cookie: team }), ctx); assert.equal(r.status, 200, p); }
r = await gate(req('/clients/', { cookie: team }), ctx); html = await r.text(); assert.match(html, /Keith &amp; Huntly/); assert.match(html, /Bryn Atlas/); ok('team opens everything, list shows all');
sb.rpc = async () => json(200, ['srv', '../x', 5, '*']);
r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + state }), ctx); assert.equal(r.status, 200); ok('odd access values filtered');
r = await gate(req('/access/sign-out'), ctx); assert.equal(cookieVal(r, 'rbx_atlas'), ''); ok('sign out clears the session');

}

// ---- the investor portal's key (portal-gate.js); KEY is what `python portal_key.py test-code-123` prints ----
env = { PORTAL_PASSCODE: 'test-code-123' };
{
const { default: gate, config } = await import(pathToFileURL(join(TMP, 'edge-functions', 'portal-gate.js')).href);

const KEY = '66d90f43de9bc65bb7c6e35047089052f477011050d1b96b6bc70f8c2c5e750b';
const O = 'https://atlas.renewablox.com';
const LANDING = '<a href="/investors/portal/peaker-plant/">Peaker</a><a href="/investors/portal/hydro/?x=1#top">Hydro</a><a href="/investors/demo/">demo</a><a href="https://www.renewablox.com/">site</a>';
const FRAME = '<iframe src="model.html" title="m"></iframe>';
const ctx = { next: async () => new Response(ctxBody, { status: 200, headers: { 'content-type': 'text/html; charset=utf-8', 'content-length': String(ctxBody.length) } }) };
let ctxBody = LANDING;
const req = (path, { cookie = '', dest = 'document', method = 'GET', body } = {}) => new Request(O + path, { method, body, headers: { cookie, 'sec-fetch-dest': dest, accept: dest === 'image' ? 'image/*' : 'text/html' } });

env = {}; let r = await gate(req('/investors/portal/'), ctx); assert.equal(r.status, 503); env = { PORTAL_PASSCODE: 'test-code-123' }; ok('locked without PORTAL_PASSCODE');
{
  const route = new RegExp(config.pattern);
  for (const p of ['/investors/portal', '/investors/portal/', '/investors/portal/hydro/model.html', '//investors/portal/', '/investors//portal/',
    '/Investors/Portal/', '/investors%2Fportal/', '///investors/portal/atlas/']) assert.ok(route.test(p), p);
  for (const p of ['/', '/investors/', '/investors/demo/', '/investors/portalx/', '/models/peaker-plant/']) assert.ok(!route.test(p), p);
}
ok('routes: every spelling of /investors/portal, and nothing else');
for (const [from, to] of [['//investors/portal/?k=' + KEY, '/investors/portal/?k=' + KEY], ['/investors//portal/hydro/', '/investors/portal/hydro/'],
  ['/Investors/Portal/', '/investors/portal/'], ['/investors%2Fportal%2Fhydro/', '/investors/portal/hydro/'],
  ['/investors/portal', '/investors/portal/'], ['/investors/portal?k=' + KEY + '&view=hydro', '/investors/portal/?k=' + KEY + '&view=hydro']]) {
  r = await gate(req(from), ctx); assert.equal(r.status, 301, from); assert.equal(r.headers.get('location'), to, from);
}
ok('any other spelling -> 301 to the one spelling, the bare /investors/portal included (the cookie\'s path has the slash)');
r = await gate(req('/investors/portal/'), ctx); assert.equal(r.status, 401); let html = await r.text(); assert.match(html, /name="code"/); assert.match(r.headers.get('content-security-policy'), /frame-ancestors 'self' https:\/\/www\.renewablox\.com/); ok('no key -> code prompt, frameable by Wix');
r = await gate(req('/investors/portal/model.glb', { dest: 'image' }), ctx); assert.equal(r.status, 401); ok('no key, a file -> 401');
r = await gate(req('/investors/portal/?k=' + KEY), ctx); assert.equal(r.status, 303); assert.equal(r.headers.get('location'), '/investors/portal/');
let sc = r.headers.get('set-cookie'); assert.match(sc, new RegExp('rbx_portal=' + KEY)); assert.match(sc, /SameSite=Lax/); assert.match(sc, /HttpOnly/); ok('the key python prints opens it: cookie set, key off the address');
r = await gate(req('/investors/portal/hydro/?view=x&k=' + KEY), ctx); assert.equal(r.headers.get('location'), '/investors/portal/hydro/?view=x'); ok('other query kept when the key is taken off');
r = await gate(req('/investors/portal/?k=test-code-123'), ctx); assert.equal(r.status, 303); ok('the code itself works as a key');
r = await gate(req('/investors/portal/?k=' + KEY.slice(0, -1) + '0'), ctx); assert.equal(r.status, 401); ok('a wrong key is refused');
r = await gate(req('/investors/portal/', { cookie: 'rbx_portal=' + KEY }), ctx); assert.equal(r.status, 200); html = await r.text(); assert.equal(html, LANDING);
assert.equal(r.headers.get('x-robots-tag'), 'noindex, nofollow'); assert.match(r.headers.get('content-security-policy'), /frame-src 'self'; frame-ancestors 'self' https:\/\/www\.renewablox\.com/); ok('cookie opens it, links untouched, policy from the build with Wix as framer');
r = await gate(req('/investors/portal/', { cookie: 'rbx_portal=deadbeef' }), ctx); assert.equal(r.status, 401); ok('a wrong cookie is refused');
r = await gate(req('/investors/portal/?k=' + KEY, { dest: 'iframe' }), ctx); assert.equal(r.status, 200); html = await r.text();
assert.ok(html.includes('href="/investors/portal/peaker-plant/?k=' + KEY + '"')); assert.ok(html.includes('href="/investors/portal/hydro/?x=1&k=' + KEY + '#top"'));
assert.ok(html.includes('href="/investors/demo/"') && html.includes('href="https://www.renewablox.com/"')); assert.equal(r.headers.get('content-length'), null);
assert.match(r.headers.get('set-cookie'), /SameSite=None; Partitioned/); ok('inside the Wix frame: key kept, pack links carry it, others untouched, partitioned cookie');
ctxBody = FRAME; r = await gate(req('/investors/portal/peaker-plant/?k=' + KEY, { dest: 'iframe' }), ctx); html = await r.text(); assert.ok(html.includes('src="model.html?k=' + KEY + '"')); ok('the model frame carries it too');
ctxBody = '<a href="/investors/portal/hydro/">x</a>'; r = await gate(req('/investors/portal/peaker-plant/model.html?k=' + KEY, { dest: 'iframe' }), ctx); assert.equal(r.status, 200);
assert.equal(await r.text(), ctxBody); ok('and the model opens with it, not scanned for links');
r = await gate(req('/investors/portal/atlas/?k=' + KEY, { dest: 'iframe' }), ctx); assert.equal(await r.text(), ctxBody); ok('nor is the Investor Atlas');
r = await gate(req('/investors/portal/', { method: 'POST', body: new URLSearchParams({ code: 'test-code-123', r: '/investors/portal/hydro/' }) }), ctx); assert.equal(r.status, 303); assert.equal(r.headers.get('location'), '/investors/portal/hydro/?k=' + KEY); ok('right code typed -> back with the key');
r = await gate(req('/investors/portal/', { method: 'POST', body: new URLSearchParams({ code: 'nope', r: '/investors/portal/' }) }), ctx); assert.equal(r.status, 401); ok('wrong code typed -> prompt again');
for (const bad of ['https://evil.com', '//evil.com', '/investors/portal/../../x', '/elsewhere']) {
  r = await gate(req('/investors/portal/', { method: 'POST', body: new URLSearchParams({ code: 'test-code-123', r: bad }) }), ctx);
  assert.equal(r.headers.get('location'), '/investors/portal/?k=' + KEY, bad);
}
ok('the prompt only returns into the portal');

}
console.log(`all ${n} passed`);
