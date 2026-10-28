// Tests for the KLD twin's signer (netlify/edge-functions/kld-twin-assets.js), with sessions made by the real sign-in
// (atlas-gate.js) against a stand-in Supabase, so the signer is shown to open the gate's own cookies.
// Run:  node atlas/tests/kld_twin_assets.test.mjs   (Node 22 or later; no packages)
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, copyFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const TMP = mkdtempSync(join(tmpdir(), 'atlas-kld-twin-'));
mkdirSync(join(TMP, 'edge-functions')); mkdirSync(join(TMP, 'edge-lib'));
for (const f of ['atlas-gate.js', 'kld-twin-assets.js']) copyFileSync(join(HERE, '..', 'netlify', 'edge-functions', f), join(TMP, 'edge-functions', f));
writeFileSync(join(TMP, 'edge-lib', 'pages.js'), `export const PAGES = {
  '/clients/kld/': { client: 'kld', title: 'KLD Atlas', views: { '3d': '3d.html', twin: 'twin.html' }, list: true },
  '/clients/srv/': { client: 'srv', title: 'SRV Atlas', views: { '3d': '3d.html' }, list: true },
};
export const CSP = { '/clients/kld/': "default-src 'self'" };
export const REDIRECTS = {};
`);
let env = {};
globalThis.Netlify = { env: { get: k => env[k] } };
let n = 0; const ok = s => console.log(`ok ${++n} ${s}`);

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
const { default: gate, config: gateConfig } = await import(pathToFileURL(join(TMP, 'edge-functions', 'atlas-gate.js')).href);
const { default: signer, config } = await import(pathToFileURL(join(TMP, 'edge-functions', 'kld-twin-assets.js')).href);

const O = 'https://atlas.renewablox.com';
const req = (path, { cookie = '', page = false, method = 'GET' } = {}) =>
  new Request(O + path, { method, headers: { cookie, ...(page ? { 'sec-fetch-dest': 'document', accept: 'text/html' } : { accept: 'application/json' }) } });
const cookieVal = (res, name) => { const c = res.headers.getSetCookie().find(c => c.startsWith(name + '=')); return c ? c.split(';')[0].slice(name.length + 1) : null; };
const ctx = { next: async () => new Response('NEXT', { status: 200 }) };
async function sessionWith(access) {
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

// routing: the signer answers only its own address, and the sign-in covers that address too
assert.equal(config.path, PATH);
assert.ok([].concat(gateConfig.pattern).some(p => new RegExp(p).test(PATH)), 'the gate routes the signer address');
ok('signer address is under /clients/kld/ and routed through the sign-in');

const kld = await sessionWith(['kld']), srv = await sessionWith(['srv']), team = await sessionWith(['*']);
assert.ok(kld && srv && team, 'sessions made by the gate');

// the gate itself: a KLD session reaches the signer, an SRV one doesn't
let r = await gate(req(PATH, { cookie: kld }), ctx); assert.equal(r.status, 200); assert.equal(await r.text(), 'NEXT');
r = await gate(req(PATH, { cookie: srv }), ctx); assert.equal(r.status, 403);
r = await gate(req(PATH), ctx); assert.equal(r.status, 401);
ok('the sign-in passes a KLD session to the signer and stops the others');

// the signer on its own
env = {}; r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 503);
env = { ...ENV, KLD_TWIN_SUPABASE_SECRET: '' }; r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 503);
env = { ...ENV }; ok('locked without its settings');
r = await signer(req(PATH)); assert.equal(r.status, 401);
r = await signer(req(PATH, { cookie: 'rbx_atlas=abc.def' })); assert.equal(r.status, 401);
r = await signer(req(PATH, { cookie: kld.slice(0, -2) + 'AA' })); assert.equal(r.status, 401);
ok('no session, a forged one or a tampered one -> 401');
r = await signer(req(PATH, { cookie: srv })); assert.equal(r.status, 403); ok('a session without KLD -> 403');
assert.equal(sb.signCalls.length, 0, 'nothing signed for a refused visitor');

r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 200);
let body = await r.json(); let text = JSON.stringify(body);
for (const k of ['splat', 'kit', 'hall']) assert.match(body[k], /^https:\/\/mojwqeqgwyldbghlzgbq\.supabase\.co\/storage\/v1\/object\/sign\/site-twins\/kld\/[0-9a-f]{32}\/kld_(web\.sog|dc_kit\.glb|hall\.glb)\?token=T$/);
assert.equal(body.expires_in, 300);
assert.ok(!text.includes(KEY), 'the key never reaches the answer');
assert.match(r.headers.get('cache-control'), /no-store/); assert.match(r.headers.get('cache-control'), /private/);
assert.equal(r.headers.get('x-robots-tag'), 'noindex, nofollow');
const call = sb.signCalls.at(-1);
assert.equal(call.headers.apikey, KEY); assert.equal(call.body.expiresIn, 300); assert.equal(call.body.paths.length, 3);
ok('a KLD session -> three signed URLs for five minutes, not cached, key only sent to Supabase');
r = await signer(req(PATH, { cookie: team })); assert.equal(r.status, 200); ok('the team (*) -> signed URLs');

const realNow = Date.now;
Date.now = () => realNow() + 7 * 3600 * 1000;
r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 401); ok('an access answer over six hours old -> 401 (open the page again)');
Date.now = () => realNow() + 31 * 24 * 3600 * 1000;
r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 401); ok('an expired session -> 401');
Date.now = realNow;

sb.sign = async () => json(500, {}); r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 503);
sb.sign = async body => json(200, body.paths.slice(1).map(p => ({ path: p, signedURL: `/object/sign/site-twins/${p}?token=T` })));
r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 503);
sb.sign = async () => { throw new Error('network'); }; r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 503);
sb.sign = async body => json(200, body.paths.map(p => ({ path: p, signedURL: 'https://elsewhere.example/x' })));
r = await signer(req(PATH, { cookie: kld })); assert.equal(r.status, 503);
sb.sign = goodSign; ok('Supabase failing, unreachable, short or odd -> 503, nothing half-signed');

r = await signer(req(PATH, { cookie: kld, method: 'POST' })); assert.equal(r.status, 405); ok('GET only');

console.log(`all ${n} passed`);
