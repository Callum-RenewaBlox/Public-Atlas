// Tests for the sign-in's edge function (netlify/edge-functions/atlas-gate.js), against a stand-in
// Supabase and a test list of pages. Run:  node atlas/tests/gates.test.mjs   (Node 22 or later; no packages)
// The gate is copied into a temporary folder beside a test edge-lib/pages.js, so the real (built) one isn't needed.
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, copyFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const TMP = mkdtempSync(join(tmpdir(), 'atlas-gates-'));
mkdirSync(join(TMP, 'edge-functions')); mkdirSync(join(TMP, 'edge-lib'));
for (const f of ['atlas-gate.js']) copyFileSync(join(HERE, '..', 'netlify', 'edge-functions', f), join(TMP, 'edge-functions', f));
writeFileSync(join(TMP, 'edge-lib', 'pages.js'), `export const PAGES = {
  '/clients/srv/': { client: 'srv', title: 'SRV Atlas', views: { '3d': '3d.html', siting: 'siting.html' }, list: true },
  '/clients/srv/contractor/': { client: 'srv', title: 'SRV Contractor Atlas', list: true },
  '/clients/bryn/': { client: 'bryn', title: 'Bryn Atlas', views: { '3d': '3d.html' }, list: true },
  '/team/keith-huntly/': { client: '*', title: 'Keith & Huntly', list: true },
  '/clients/investors/': { client: 'investors', title: 'Investor Atlas', list: true },
};
export const CSP = { '/clients/srv/': "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com", '/team/': "default-src 'self'" };
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
  if (String(url).endsWith('/auth/v1/otp')) return sb.otp(body);
  if (String(url).endsWith('/auth/v1/verify')) return sb.verify(body);
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
const MSA = '9188040d-6c67-4c5b-b112-36a304b66dad';   // Microsoft's tenant for personal accounts
const identity = (provider, email, verified = true, custom = provider === 'azure' ? { tid: MSA } : undefined) =>
  ({ provider, identity_data: { email, email_verified: verified, ...(custom ? { custom_claims: custom } : {}) } });
const user = (email, verified = true, provider = 'google', custom) => ({ email, identities: [identity(provider, email, verified, custom)] });

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
assert.match(html, /href="\/access\/start\?p=google&amp;r=%2Fclients%2Fsrv%2F"/); assert.match(html, /href="\/access\/start\?p=microsoft&amp;r=%2Fclients%2Fsrv%2F"/);
assert.match(r.headers.get('content-security-policy'), /frame-ancestors 'none'/); ok('sign-in page offers Google and Microsoft');
for (const bad of ['//evil.com/x', 'https://evil.com', '/clients/../oscar', '/clients/%2e%2e/x', '/elsewhere/', '/clients/srv/?x=<b>', '/clients//srv/', '/clients/srv/?a=1?b=2']) {
  r = await gate(req('/access/?r=' + encodeURIComponent(bad)), ctx); html = await r.text();
  assert.match(html, /href="\/access\/start\?p=google&amp;r=%2Fclients%2F"/, bad);
}
ok('return address confined to /clients and /team');

// start
r = await gate(req('/access/start?r=' + encodeURIComponent('/clients/srv/?view=3d')), ctx); assert.equal(r.status, 303);
const auth = new URL(r.headers.get('location')); assert.equal(auth.origin + auth.pathname, ENV.SUPABASE_URL + '/auth/v1/authorize');
assert.equal(auth.searchParams.get('provider'), 'google'); assert.equal(auth.searchParams.get('redirect_to'), O + '/access/callback');
assert.equal(auth.searchParams.get('code_challenge_method'), 's256');
const state = cookieVal(r, 'rbx_atlas_signin'); assert.ok(state); assert.match(setCookies(r)[0], /Path=\/access;.*HttpOnly/); ok('start -> Supabase authorize with PKCE');
r = await gate(req('/access/start?p=microsoft&r=' + encodeURIComponent('/clients/srv/')), ctx); assert.equal(r.status, 303);
const authMs = new URL(r.headers.get('location')); assert.equal(authMs.searchParams.get('provider'), 'azure'); assert.equal(authMs.searchParams.get('scopes'), 'email');
const stateMs = cookieVal(r, 'rbx_atlas_signin'); ok('start ?p=microsoft -> Supabase azure provider');
r = await gate(req('/access/start?p=evil&r=%2Fclients%2F'), ctx); assert.equal(new URL(r.headers.get('location')).searchParams.get('provider'), 'google'); ok('unknown provider -> Google');

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
r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + state }), ctx); assert.equal(r.status, 403); ok('identity other than the one signed in with refused');
{
  const saved = sb.token, savedRpc = sb.rpc;
  sb.token = async () => json(200, { access_token: 'AT1', refresh_token: 'RT1', user: user('Client@Hotmail.co.uk', true, 'azure') }); sb.rpc = async () => json(200, ['srv']);
  r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + stateMs }), ctx); assert.equal(r.status, 200); assert.ok(cookieVal(r, 'rbx_atlas')); ok('verified Microsoft address -> session');
  sb.token = async () => json(200, { access_token: 'AT1', refresh_token: 'RT1', user: user('client@contoso.com', false, 'azure') });
  r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + stateMs }), ctx); assert.equal(r.status, 403); assert.equal(cookieVal(r, 'rbx_atlas'), null); ok('unverified Microsoft address refused');
  sb.token = async () => json(200, { access_token: 'AT1', refresh_token: 'RT1', user: user('client@example.com', true, 'google') });
  r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + stateMs }), ctx); assert.equal(r.status, 403); ok('Microsoft sign-in answered by another identity refused');
  const work = { tid: '72f988bf-86f1-41af-91ab-2d7cd011db47' };
  const signIn = async (u, st = stateMs) => { sb.token = async () => json(200, { access_token: 'AT1', refresh_token: 'RT1', user: u });
    return gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + st }), ctx); };
  r = await signIn(user('client@contoso.com', true, 'azure', { ...work, xms_edov: true })); assert.equal(r.status, 200); ok('work Microsoft address with a verified domain (xms_edov) -> session');
  r = await signIn(user('client@contoso.com', true, 'azure', { ...work, xms_edov: false })); assert.equal(r.status, 403);
  r = await signIn(user('client@contoso.com', true, 'azure', work)); assert.equal(r.status, 403); assert.equal(cookieVal(r, 'rbx_atlas'), null);
  r = await signIn(user('client@contoso.com', true, 'azure', {})); assert.equal(r.status, 403);
  ok('work Microsoft address without xms_edov refused, though Supabase counts it verified');
  // one account, several identities: every Google and Microsoft one must vouch for the address, whichever ?p= was used
  const both = (ms) => ({ email: 'client@example.com', identities: [identity('google', 'client@example.com'), ms] });
  r = await signIn(both(identity('azure', 'client@example.com')), state); assert.equal(r.status, 200);
  r = await signIn(both(identity('azure', 'client@example.com')), stateMs); assert.equal(r.status, 200); ok('Google and Microsoft identities that agree -> session either way in');
  r = await signIn(both(identity('azure', 'someone.else@example.com')), state); assert.equal(r.status, 403); assert.equal(cookieVal(r, 'rbx_atlas'), null);
  r = await signIn(both(identity('azure', 'client@example.com', true, { tid: work.tid })), state); assert.equal(r.status, 403);
  ok('a Google sign-in on an account whose Microsoft identity no longer vouches for the address refused');
  r = await signIn({ email: 'client@example.com', identities: [identity('azure', 'client@example.com'), identity('azure', 'old@example.com')] }); assert.equal(r.status, 403);
  ok('two Microsoft identities, one stale -> refused');
  r = await signIn({ email: 'client@example.com', identities: [identity('google', 'client@example.com'), identity('email', 'x@y.z', false)] }, state); assert.equal(r.status, 200);
  ok('an identity of another kind (email) is not consulted');
  sb.token = saved; sb.rpc = savedRpc;
}
sb.token = async () => json(200, { access_token: 'AT2', refresh_token: 'RT2', user: user('stranger@example.com') }); sb.rpc = async () => json(200, []);
r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + state }), ctx); assert.equal(r.status, 403); assert.equal(cookieVal(r, 'rbx_atlas'), null); ok('nothing shared -> 403, no session');
html = await r.text();
for (const p of ['google', 'microsoft']) assert.ok(html.includes(`href="/access/start?p=${p}&amp;r=%2Fclients%2Fsrv%2F%3Fview%3D3d"`), p);
assert.ok(!html.includes('href="/access/?r='), 'not back through /access/, which would overwrite the kept #fragment');
ok('nothing shared: a different account goes straight to each provider');
sb.token = async () => json(400, { error: 'invalid_grant' });
r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + state }), ctx); assert.equal(r.status, 400); ok('code refused by Supabase');
sb.token = async () => json(200, { access_token: 'AT1', refresh_token: 'RT1', user: user('client@example.com') }); sb.rpc = async () => json(500, {});
r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + state }), ctx); assert.equal(r.status, 503); ok('access unknown -> 503, no session');

// the fallback: a one-time code by email
{
  const post = (path, fields, cookie = '') => new Request(O + path, { method: 'POST', headers: { cookie, 'content-type': 'application/x-www-form-urlencoded', 'sec-fetch-dest': 'document', accept: 'text/html' }, body: new URLSearchParams(fields).toString() });
  r = await gate(req('/access/?r=' + encodeURIComponent('/clients/srv/')), ctx); html = await r.text();
  assert.match(html, /href="\/access\/email\?r=%2Fclients%2Fsrv%2F"/); ok('sign-in page offers a code by email');
  r = await gate(req('/access/email?r=' + encodeURIComponent('/clients/srv/')), ctx); assert.equal(r.status, 200); html = await r.text();
  assert.match(html, /<form method="post" action="\/access\/email"/); assert.match(html, /name="r" value="\/clients\/srv\/"/);
  assert.match(r.headers.get('content-security-policy'), /form-action 'self'/); ok('email page: a form that may post to the site');
  sb.otp = async () => { throw new Error('should not be called'); };
  r = await gate(post('/access/email', { email: 'not an address', r: '/clients/srv/' }), ctx); assert.equal(r.status, 400); ok('a non-address is refused before Supabase');
  let sentTo = null; sb.otp = async body => { sentTo = body; return json(200, {}); };
  r = await gate(post('/access/email', { email: ' Client@Contoso.COM ', r: '//evil.com/' }), ctx); assert.equal(r.status, 200);
  assert.deepEqual(sentTo, { email: 'client@contoso.com', create_user: true }); html = await r.text(); assert.match(html, /action="\/access\/email\/code"/);
  const codeState = cookieVal(r, 'rbx_atlas_code'); assert.ok(codeState); assert.match(setCookies(r)[0], /Path=\/access;.*HttpOnly/);
  assert.ok(!Buffer.from(codeState.split('.')[1], 'base64url').toString().includes('contoso'), 'address sealed'); ok('code sent to the address, lower case; sealed state');
  sb.otp = async () => json(429, { msg: 'rate limit' });
  r = await gate(post('/access/email', { email: 'client@contoso.com', r: '/clients/srv/' }), ctx); assert.equal(r.status, 429); assert.match(await r.text(), /can.rsquo;t send another code just yet/); ok('Supabase busy -> wait, not "a code was sent"');
  sb.otp = async () => json(422, { msg: 'Signups not allowed for this instance' });
  r = await gate(post('/access/email', { email: 'stranger@contoso.com', r: '/clients/srv/' }), ctx); assert.equal(r.status, 200);
  html = await r.text(); assert.match(html, /If stranger@contoso.com has been given access, a sign-in code is on its way/); assert.ok(cookieVal(r, 'rbx_atlas_code'));
  ok('an address Supabase turns away reads the same as one sent a code (no telling who has access)');
  let sentApos = null; sb.otp = async body => { sentApos = body; return json(200, {}); };
  r = await gate(post('/access/email', { email: "O'Brien@contoso.com", r: '/clients/srv/' }), ctx); assert.equal(r.status, 200);
  assert.equal(sentApos.email, "o'brien@contoso.com"); assert.ok(!(await r.text()).includes("o'brien"), 'the address is escaped on the page');
  r = await gate(post('/access/email', { email: 'a@b.xn--p1ai', r: '/clients/srv/' }), ctx); assert.equal(r.status, 200);
  ok("addresses with an apostrophe or an IDN domain are accepted, and escaped");
  r = await gate(post('/access/email/code', { code: '123456' }), ctx); assert.equal(r.status, 400); ok('code without its state -> expired');
  let verified = null;
  sb.verify = async body => { verified = body; return json(403, { msg: 'Token has expired or is invalid' }); };
  r = await gate(post('/access/email/code', { code: '123 456' }, 'rbx_atlas_code=' + codeState), ctx); assert.equal(r.status, 401);
  assert.deepEqual(verified, { type: 'email', email: 'client@contoso.com', token: '123456' }); assert.equal(cookieVal(r, 'rbx_atlas'), null); ok('wrong code refused, no session');
  r = await gate(post('/access/email/code', { code: 'abc' }, 'rbx_atlas_code=' + codeState), ctx); assert.equal(r.status, 400); ok('a non-code is refused before Supabase');
  sb.verify = async () => json(429, { msg: 'rate limit' });
  r = await gate(post('/access/email/code', { code: '123456' }, 'rbx_atlas_code=' + codeState), ctx); assert.equal(r.status, 429);
  assert.match(await r.text(), /Too many sign-in attempts/); assert.ok(!setCookies(r).some(c => c.startsWith('rbx_atlas_code=;')), 'the code is kept');
  ok('code checks limited -> try the same code again later, not "that code isn\'t right"');
  sb.verify = async () => json(200, { access_token: 'AT3', refresh_token: 'RT3', user: { email: 'client@contoso.com', email_confirmed_at: '2026-10-24T08:00:00Z', identities: [{ provider: 'email' }] } });
  sb.rpc = async bearer => { assert.equal(bearer, 'Bearer AT3'); return json(200, ['srv']); };
  r = await gate(post('/access/email/code', { code: '123456' }, 'rbx_atlas_code=' + codeState), ctx); assert.equal(r.status, 200);
  assert.ok(cookieVal(r, 'rbx_atlas')); assert.equal(cookieVal(r, 'rbx_atlas_code'), ''); html = await r.text();
  assert.match(html, /location\.replace\("\/clients\/"/, 'an unsafe return address falls back to /clients/'); ok('right code -> session, code state cleared');
  sb.verify = async () => json(200, { access_token: 'AT3', refresh_token: 'RT3', user: { email: 'someone@else.com', email_confirmed_at: '2026-10-24T08:00:00Z' } });
  r = await gate(post('/access/email/code', { code: '123456' }, 'rbx_atlas_code=' + codeState), ctx); assert.equal(r.status, 403); assert.equal(cookieVal(r, 'rbx_atlas'), null); ok('code answered for another address refused');
  sb.verify = async () => json(200, { access_token: 'AT3', refresh_token: 'RT3', user: { email: 'client@contoso.com' } }); sb.rpc = async () => json(200, []);
  r = await gate(post('/access/email/code', { code: '123456' }, 'rbx_atlas_code=' + codeState), ctx); assert.equal(r.status, 403); ok('unconfirmed address refused');
  sb.verify = async () => json(200, { access_token: 'AT3', refresh_token: 'RT3', user: { email: 'client@contoso.com', email_confirmed_at: 'x' } });
  r = await gate(post('/access/email/code', { code: '123456' }, 'rbx_atlas_code=' + codeState), ctx); assert.equal(r.status, 403); assert.match(await r.text(), /Nothing is shared/); ok('code for an address with nothing shared -> 403');
}

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

// the Investor Atlas, for registered investors (code 'investors'); anyone else signed in is sent to register
{
  const INV = '/clients/investors/', PORTAL = 'https://www.renewablox.com/invest';
  const postForm = (path, fields, cookie = '') => new Request(O + path, { method: 'POST', headers: { cookie, 'content-type': 'application/x-www-form-urlencoded', 'sec-fetch-dest': 'document', accept: 'text/html' }, body: new URLSearchParams(fields).toString() });
  r = await gate(req(INV), ctx); assert.equal(r.status, 303); assert.equal(r.headers.get('location'), '/access/?r=' + encodeURIComponent(INV)); ok('investors: signed out -> sign-in');
  r = await gate(req('/access/?r=' + encodeURIComponent(INV)), ctx); html = await r.text();
  assert.match(html, /<h1>Registered investors: sign in<\/h1>/); assert.match(html, /the address you registered with/); assert.ok(html.includes(`href="${PORTAL}"`));
  assert.match(html, /href="\/access\/start\?p=google&amp;r=%2Fclients%2Finvestors%2F"/); assert.match(html, /href="\/access\/start\?p=microsoft&amp;r=%2Fclients%2Finvestors%2F"/);
  r = await gate(req('/access/?r=' + encodeURIComponent('/clients/srv/')), ctx); html = await r.text(); assert.match(html, /<h1>Sign in to open this page<\/h1>/); assert.ok(!html.includes(PORTAL));
  ok("investors: the sign-in speaks to registered investors and links to registration; other pages' sign-in unchanged");
  r = await gate(req('/access/email?r=' + encodeURIComponent(INV)), ctx); assert.match(await r.text(), /Enter the address you registered with\./); ok('investors: the emailed code asks for the address registered with');
  r = await gate(req('/access/start?r=' + encodeURIComponent(INV)), ctx); const invState = 'rbx_atlas_signin=' + cookieVal(r, 'rbx_atlas_signin');
  sb.token = async () => json(200, { access_token: 'AT7', refresh_token: 'RT7', user: user('Stranger@Example.com') }); sb.rpc = async () => json(200, []);
  r = await gate(req('/access/callback?code=abc', { cookie: invState }), ctx); assert.equal(r.status, 403); assert.equal(cookieVal(r, 'rbx_atlas'), null); html = await r.text();
  assert.match(html, /isn&rsquo;t registered as an investor/); assert.match(html, /stranger@example\.com/); assert.ok(html.includes(`href="${PORTAL}"`));
  ok('investors: an unregistered address is sent to register at the Investor Portal, with no session');
  r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + state }), ctx); assert.match(await r.text(), /Nothing is shared with this account/); ok("investors: other pages' refusal unchanged");
  sb.otp = async () => json(200, {});
  r = await gate(postForm('/access/email', { email: 'stranger@example.com', r: INV }), ctx); const invCode = 'rbx_atlas_code=' + cookieVal(r, 'rbx_atlas_code');
  sb.verify = async () => json(200, { access_token: 'AT8', refresh_token: 'RT8', user: { email: 'stranger@example.com', email_confirmed_at: 'x' } });
  r = await gate(postForm('/access/email/code', { code: '123456' }, invCode), ctx); assert.equal(r.status, 403); assert.ok((await r.text()).includes(`href="${PORTAL}"`)); ok('investors: by emailed code too');
  sb.token = async () => json(200, { access_token: 'AT7', refresh_token: 'RT7', user: user('Investor@Example.com') }); sb.rpc = async () => json(200, ['investors']);
  r = await gate(req('/access/callback?code=abc', { cookie: invState }), ctx); assert.equal(r.status, 200); const inv = 'rbx_atlas=' + cookieVal(r, 'rbx_atlas');
  assert.match(await r.text(), /location\.replace\("\/clients\/investors\/"/);
  r = await gate(req(INV, { cookie: inv }), ctx); assert.equal(r.status, 200); assert.equal(await r.text(), 'STATIC');
  r = await gate(req('/clients/srv/', { cookie: inv }), ctx); assert.equal(r.status, 403); assert.match(await r.text(), /isn&rsquo;t shared with you/);
  r = await gate(req('/clients/', { cookie: inv }), ctx); html = await r.text(); assert.match(html, /Investor Atlas/); assert.ok(!html.includes('SRV Atlas'));
  ok('investors: a registered investor opens the Investor Atlas, and only that');
  r = await gate(req(INV, { cookie: c }), ctx); assert.equal(r.status, 403); html = await r.text(); assert.match(html, /registered as an investor/); assert.ok(html.includes(`href="${PORTAL}"`));
  ok('investors: a client of another site is sent to register, not told to ask');
  r = await gate(req(INV, { cookie: team }), ctx); assert.equal(r.status, 200); ok('investors: the team opens it');
}

}

console.log(`all ${n} passed`);
