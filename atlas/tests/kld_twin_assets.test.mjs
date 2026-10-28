// Tests for the KLD twin's signer (netlify/edge-functions/kld-twin-assets.js) and for the sign-in's open views, with
// sessions made by the real sign-in (atlas-gate.js) against a stand-in Supabase. Two settings are tested, each on its
// own copy of the two functions:
//   * open: the twin listed in OPEN_WITHOUT_SIGN_IN (atlas/pages.py), as now: the twin, its file and its signer open to
//     anyone; everything else (KLD's map and 3D view, other clients) still behind the sign-in;
//   * closed: the entry deleted, as when the client sign-in goes live: the signer checks the session itself.
// Run:  node atlas/tests/kld_twin_assets.test.mjs   (Node 22 or later; no packages)
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, copyFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
let n = 0; const ok = s => console.log(`ok ${++n} ${s}`);
const PAGES = `export const PAGES = {
  '/clients/kld/': { client: 'kld', title: 'KLD Atlas', views: { '3d': '3d.html', twin: 'twin.html' }, list: true },
  '/clients/srv/': { client: 'srv', title: 'SRV Atlas', views: { '3d': '3d.html' }, list: true },
};
export const CSP = { '/clients/kld/': "default-src 'self'", '/clients/kld/twin.html': "default-src 'self'; connect-src 'self' https://twin.test" };
export const REDIRECTS = {};
`;
async function load(open) {
  const dir = mkdtempSync(join(tmpdir(), `atlas-kld-twin-${open ? 'open' : 'closed'}-`));
  mkdirSync(join(dir, 'edge-functions')); mkdirSync(join(dir, 'edge-lib'));
  for (const f of ['atlas-gate.js', 'kld-twin-assets.js']) copyFileSync(join(HERE, '..', 'netlify', 'edge-functions', f), join(dir, 'edge-functions', f));
  writeFileSync(join(dir, 'edge-lib', 'pages.js'), PAGES + (open
    ? `export const OPEN_VIEWS = { '/clients/kld/': ['twin'] };\nexport const OPEN_PATHS = ['/clients/kld/twin-assets', '/clients/kld/twin.html'];\n`
    : `export const OPEN_VIEWS = {};\nexport const OPEN_PATHS = [];\n`));
  const gate = await import(pathToFileURL(join(dir, 'edge-functions', 'atlas-gate.js')).href);
  const signer = await import(pathToFileURL(join(dir, 'edge-functions', 'kld-twin-assets.js')).href);
  return { gate: gate.default, gateConfig: gate.config, signer: signer.default, config: signer.config };
}

let env = {};
globalThis.Netlify = { env: { get: k => env[k] } };
const KEY = 'sb_secret_test_signer_key_value';
const ENV = { SUPABASE_URL: 'https://enghoowpiwopsfabfurx.supabase.co', SUPABASE_PUBLISHABLE_KEY: 'sb_publishable_test',
  ATLAS_SESSION_SECRET: 'x'.repeat(40), KLD_TWIN_SUPABASE_SECRET: KEY };
env = { ...ENV };
const json = (status, obj) => new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });
const sb = { access: [], sign: null, signCalls: [] };
globalThis.fetch = async (url, init) => {
  const u = String(url);
  if (u.includes('grant_type=pkce')) return json(200, { access_token: 'AT', refresh_token: 'RT', user: { email: 'client@example.com',
    identities: [{ provider: 'google', identity_data: { email: 'client@example.com', email_verified: true } }] } });
  if (u.endsWith('/rest/v1/rpc/atlas_my_access')) return json(200, sb.access);
  if (u === 'https://mojwqeqgwyldbghlzgbq.supabase.co/storage/v1/object/sign/site-twins') {
    assert.ok(init.signal instanceof AbortSignal, 'the signing call has a time limit');
    sb.signCalls.push({ headers: init.headers, body: JSON.parse(init.body) });
    return sb.sign(JSON.parse(init.body));
  }
  throw new Error('unexpected fetch ' + u);
};
const O = 'https://atlas.renewablox.com';
const req = (path, { cookie = '', page = false, method = 'GET' } = {}) =>
  new Request(O + path, { method, headers: { cookie, ...(page ? { 'sec-fetch-dest': 'document', accept: 'text/html' } : { accept: 'application/json' }) } });
const cookieVal = (res, name) => { const c = res.headers.getSetCookie().find(c => c.startsWith(name + '=')); return c ? c.split(';')[0].slice(name.length + 1) : null; };
const ctx = { next: async () => new Response('NEXT', { status: 200, headers: { 'content-type': 'text/html' } }) };
async function sessionWith(gate, access) {
  sb.access = access;
  let r = await gate(req('/access/start?p=google&r=%2Fclients%2Fkld%2F', { page: true }), ctx);
  const state = cookieVal(r, 'rbx_atlas_signin');
  r = await gate(req('/access/callback?code=abc', { cookie: 'rbx_atlas_signin=' + state, page: true }), ctx);
  const s = cookieVal(r, 'rbx_atlas');
  return s ? 'rbx_atlas=' + s : null;
}
const PATH = '/clients/kld/twin-assets';
const goodSign = body => json(200, body.paths.map(p => ({ path: p, signedURL: `/object/sign/site-twins/${p}?token=T`, error: null })));
sb.sign = goodSign;
const checkUrls = body => {
  for (const k of ['splat', 'kit', 'hall']) assert.match(body[k], /^https:\/\/mojwqeqgwyldbghlzgbq\.supabase\.co\/storage\/v1\/object\/sign\/site-twins\/kld\/[0-9a-f]{32}\/kld_(web\.sog|dc_kit\.glb|hall\.glb)\?token=T$/);
  assert.equal(body.expires_in, 300); assert.ok(!JSON.stringify(body).includes(KEY), 'the key never reaches the answer');
};

// ================= open: the twin without the sign-in (now) =================
{
  const { gate, gateConfig, signer, config } = await load(true);
  assert.equal(config.path, PATH);
  assert.ok([].concat(gateConfig.pattern).some(p => new RegExp(p).test(PATH)), 'the gate routes the signer address');
  const srv = await sessionWith(gate, ['srv']);

  let r = await gate(req('/clients/kld/?view=twin', { page: true }), ctx);
  assert.ok(r instanceof URL, 'a rewrite'); assert.equal(r.pathname, '/clients/kld/twin.html');
  ok('open: signed out, /clients/kld/?view=twin -> the twin view');
  r = await gate(req('/clients/kld/twin.html', { page: true }), ctx); assert.equal(r.status, 200); assert.equal(await r.text(), 'NEXT');
  assert.equal(r.headers.get('x-robots-tag'), 'noindex, nofollow'); assert.match(r.headers.get('cache-control'), /private/);
  assert.equal(r.headers.get('content-security-policy'), "default-src 'self'; connect-src 'self' https://twin.test");
  ok('open: signed out, the twin file is served with noindex and its own policy');
  r = await gate(req(PATH), ctx); assert.equal(r.status, 200); assert.equal(await r.text(), 'NEXT'); ok('open: signed out, the signer address passes the gate');

  for (const p of ['/clients/kld/', '/clients/kld/?view=3d', '/clients/kld/3d.html', '/clients/kld/?view=twin2', '/clients/kld/?view=TWIN',
    '/clients/kld/twin.htm', '/clients/kld/twin.html.bak', '/clients/kld/twin-assets2', '/clients/kld/x/twin.html', '/clients/', '/clients/srv/', '/clients/srv/?view=twin', '/team/x/']) {
    r = await gate(req(p, { page: true }), ctx); assert.equal(r.status, 303, p); assert.match(r.headers.get('location'), /^\/access\//, p);
  }
  r = await gate(req('/clients/kld/3d.html'), ctx); assert.equal(r.status, 401);
  ok("open: signed out, KLD's map and 3D view, near-miss addresses and every other client page still go to the sign-in");
  r = await gate(req('//clients/kld/twin.html', { page: true }), ctx); assert.equal(r.status, 301); assert.equal(r.headers.get('location'), '/clients/kld/twin.html');
  ok('open: other spellings are sent to the one spelling first');
  r = await gate(req('/clients/kld/', { cookie: srv, page: true }), ctx); assert.equal(r.status, 403); ok("open: an SRV client still can't open KLD's map");

  r = await signer(req(PATH)); assert.equal(r.status, 200); checkUrls(await r.json());
  assert.match(r.headers.get('cache-control'), /no-store/); assert.equal(r.headers.get('x-robots-tag'), 'noindex, nofollow');
  assert.equal(sb.signCalls.at(-1).headers.apikey, KEY); assert.equal(sb.signCalls.at(-1).body.expiresIn, 300);
  ok('open: the signer gives anyone three five-minute URLs, not cached, the key only sent to Supabase');
  r = await signer(req(PATH, { cookie: srv })); assert.equal(r.status, 200); ok('open: any session too');
  env = { ...ENV, ATLAS_SESSION_SECRET: '' }; r = await signer(req(PATH)); assert.equal(r.status, 200); env = { ...ENV };
  env = { ...ENV, KLD_TWIN_SUPABASE_SECRET: '' }; r = await signer(req(PATH)); assert.equal(r.status, 503); env = { ...ENV };
  ok('open: needs only its own key');
  sb.sign = async () => json(500, {}); r = await signer(req(PATH)); assert.equal(r.status, 503); sb.sign = goodSign;
  r = await signer(req(PATH, { method: 'POST' })); assert.equal(r.status, 405);
  ok('open: Supabase failing -> 503; GET only');
}

// ================= closed: the entry deleted, as when the client sign-in goes live =================
{
  const { gate, signer } = await load(false);
  const kld = await sessionWith(gate, ['kld']), srv = await sessionWith(gate, ['srv']), team = await sessionWith(gate, ['*']);
  assert.ok(kld && srv && team, 'sessions made by the gate');
  sb.signCalls.length = 0;

  let r = await gate(req('/clients/kld/?view=twin', { page: true }), ctx); assert.equal(r.status, 303);
  r = await gate(req('/clients/kld/twin.html', { page: true }), ctx); assert.equal(r.status, 303);
  r = await gate(req(PATH, { cookie: kld }), ctx); assert.equal(r.status, 200); assert.equal(await r.text(), 'NEXT');
  r = await gate(req(PATH, { cookie: srv }), ctx); assert.equal(r.status, 403);
  r = await gate(req(PATH), ctx); assert.equal(r.status, 401);
  ok('closed: the twin is behind the sign-in again; a KLD session reaches the signer, the others are stopped');

  env = {}; r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 503);
  env = { ...ENV, ATLAS_SESSION_SECRET: '' }; r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 503);
  env = { ...ENV }; ok('closed: locked without its settings');
  r = await signer(req(PATH)); assert.equal(r.status, 401);
  r = await signer(req(PATH, { cookie: 'rbx_atlas=abc.def' })); assert.equal(r.status, 401);
  r = await signer(req(PATH, { cookie: kld.slice(0, -2) + 'AA' })); assert.equal(r.status, 401);
  ok('closed: no session, a forged one or a tampered one -> 401');
  r = await signer(req(PATH, { cookie: srv })); assert.equal(r.status, 403); ok('closed: a session without KLD -> 403');
  assert.equal(sb.signCalls.length, 0, 'nothing signed for a refused visitor');
  r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 200); checkUrls(await r.json()); ok('closed: a KLD session -> signed URLs');
  r = await signer(req(PATH, { cookie: team })); assert.equal(r.status, 200); ok('closed: the team (*) -> signed URLs');

  const realNow = Date.now;
  Date.now = () => realNow() + 7 * 3600 * 1000;
  r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 401); ok('closed: an access answer over six hours old -> 401');
  Date.now = () => realNow() + 31 * 24 * 3600 * 1000;
  r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 401); ok('closed: an expired session -> 401');
  Date.now = realNow;

  sb.sign = async () => json(500, {}); r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 503);
  sb.sign = async body => json(200, body.paths.slice(1).map(p => ({ path: p, signedURL: `/object/sign/site-twins/${p}?token=T` })));
  r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 503);
  sb.sign = async () => { throw new Error('network'); }; r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 503);
  sb.sign = async body => json(200, body.paths.map(p => ({ path: p, signedURL: 'https://elsewhere.example/x' })));
  r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 503);
  sb.sign = goodSign; ok('closed: Supabase failing, unreachable, short or odd -> 503, nothing half-signed');
}

console.log(`all ${n} passed`);
