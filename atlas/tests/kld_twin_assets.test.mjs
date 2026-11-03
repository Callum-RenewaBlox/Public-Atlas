// Tests for the KLD twin's signer (netlify/edge-functions/kld-twin-assets.js), against a stand-in Supabase. The twin is
// public at /twins/kld/: the signer answers any visitor, with no session, and the sign-in (atlas-gate.js) never runs
// on /twins/.
// Run:  node atlas/tests/kld_twin_assets.test.mjs   (Node 22 or later; no packages)
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const FN = join(HERE, '..', 'netlify', 'edge-functions');
let n = 0; const ok = s => console.log(`ok ${++n} ${s}`);

let env = {};
globalThis.Netlify = { env: { get: k => env[k] } };
const KEY = 'sb_secret_test_signer_key_value';
const SIGN = 'https://mojwqeqgwyldbghlzgbq.supabase.co/storage/v1/object/sign/site-twins';
const FOLDER = 'kld/08ef398ce6de02ef46118920a71665d1';
const json = (status, obj) => new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });
const sb = { sign: null, calls: [] };
globalThis.fetch = async (url, init) => {
  const u = String(url);
  if (u !== SIGN) throw new Error('unexpected fetch ' + u);
  assert.ok(init.signal instanceof AbortSignal, 'the signing call has a time limit');
  sb.calls.push({ method: init.method, headers: init.headers, body: JSON.parse(init.body) });
  return sb.sign(JSON.parse(init.body));
};
const goodSign = body => json(200, body.paths.map(p => ({ path: p, signedURL: `/object/sign/site-twins/${p}?token=T`, error: null })));
const logged = [];
console.error = (...a) => logged.push(a.map(String).join(' '));

const signer = await import(pathToFileURL(join(FN, 'kld-twin-assets.js')).href);
const gate = await import(pathToFileURL(join(FN, 'atlas-gate.js')).href);
const O = 'https://atlas.renewablox.com';
const req = (path, { cookie = '', method = 'GET' } = {}) => new Request(O + path, { method, headers: { cookie, accept: 'application/json' } });
const reset = () => { env = { KLD_TWIN_SUPABASE_SECRET: KEY }; sb.calls = []; sb.sign = goodSign; };

// where it runs, and where the sign-in doesn't
assert.equal(signer.config.path, '/twins/kld/assets');
ok('the signer answers /twins/kld/assets');
const gated = p => gate.config.pattern.some(re => new RegExp(re).test(p));
for (const p of ['/twins/kld/', '/twins/kld/index.html', '/twins/kld/assets', '//twins/kld/assets', '/TWINS/kld/'])
  assert.equal(gated(p), false, `the sign-in must not run on ${p}`);
for (const p of ['/clients/kld/', '/clients/kld/3d.html', '//clients/kld/', '/team/moray/'])
  assert.equal(gated(p), true, `the sign-in still runs on ${p}`);
ok('the sign-in never runs on /twins/, and still runs on /clients/ and /team/');
const src = readFileSync(join(FN, 'kld-twin-assets.js'), 'utf8');
assert.ok(!/ATLAS_SESSION_SECRET|rbx_atlas|cookie|edge-lib/.test(src.replace(/\/\*[\s\S]*?\*\//g, '')), 'no session code left in the signer');
ok('the signer has no session check to depend on');

// any visitor, signed in or not, gets four five-minute URLs
for (const cookie of ['', 'rbx_atlas=garbage', 'rbx_atlas=a.b']) {
  reset();
  const res = await signer.default(req('/twins/kld/assets', { cookie }));
  assert.equal(res.status, 200, `status with cookie ${JSON.stringify(cookie)}`);
  const body = await res.json();
  assert.equal(body.expires_in, 300);
  const FILES = [['splat', 'kld_web.sog'], ['kit', 'kld_dc_kit_v5.glb'], ['hall', 'kld_hall_v5.glb'], ['interior', 'kld_interior_v1.sog']];
  assert.deepEqual(Object.keys(body).sort(), ['expires_in', ...FILES.map(([k]) => k)].sort());
  for (const [k, f] of FILES)
    assert.equal(body[k], `https://mojwqeqgwyldbghlzgbq.supabase.co/storage/v1/object/sign/site-twins/${FOLDER}/${f}?token=T`);
  assert.equal(sb.calls.length, 1);
  assert.equal(sb.calls[0].method, 'POST');
  assert.deepEqual(sb.calls[0].body, { expiresIn: 300, paths: FILES.map(([, f]) => `${FOLDER}/${f}`) });
  assert.equal(sb.calls[0].headers.apikey, KEY);
  assert.equal(sb.calls[0].headers.authorization, `Bearer ${KEY}`);
  assert.equal(res.headers.get('cache-control'), 'private, no-store');
  assert.equal(res.headers.get('x-robots-tag'), 'noindex, nofollow');
  assert.ok(!JSON.stringify(body).includes(KEY), 'the key never reaches the visitor');
}
ok('any visitor gets the four signed URLs (5 min), never cached, noindex; the key stays server-side');

// ?set=model is the same answer; ?set=media signs the flythrough, its poster and the stills, for an hour
let res;
reset();
res = await signer.default(req('/twins/kld/assets?set=model'));
assert.equal(res.status, 200);
assert.deepEqual(Object.keys(await res.json()).sort(), ['expires_in', 'hall', 'interior', 'kit', 'splat']);
assert.equal(sb.calls[0].body.expiresIn, 300);
ok('?set=model: the same four five-minute URLs');
const STILLS = ['racks', 'zone', 'taped', 'built', 'detail'];
const MEDIA = [['video', 'kld_flythrough_v1_720p.mp4'], ['poster', 'kld_flythrough_v1_poster.jpg'],
  ...STILLS.flatMap(s => [[s, `kld_still_${s}_v1.jpg`], [`${s}_thumb`, `kld_still_${s}_v1_thumb.jpg`]])];
for (const cookie of ['', 'rbx_atlas=garbage']) {
  reset();
  res = await signer.default(req('/twins/kld/assets?set=media', { cookie }));
  assert.equal(res.status, 200);
  const body = await res.json();
  assert.equal(body.expires_in, 3600);
  assert.deepEqual(Object.keys(body).sort(), ['expires_in', ...MEDIA.map(([k]) => k)].sort());
  for (const [k, f] of MEDIA)
    assert.equal(body[k], `https://mojwqeqgwyldbghlzgbq.supabase.co/storage/v1/object/sign/site-twins/${FOLDER}/${f}?token=T`);
  assert.equal(sb.calls.length, 1);
  assert.deepEqual(sb.calls[0].body, { expiresIn: 3600, paths: MEDIA.map(([, f]) => `${FOLDER}/${f}`) });
  assert.ok(!sb.calls[0].body.paths.some(p => /\.(sog|glb)$/.test(p)), 'the media set signs no model file');
  assert.equal(res.headers.get('cache-control'), 'private, no-store');
  assert.equal(res.headers.get('x-robots-tag'), 'noindex, nofollow');
  assert.ok(!JSON.stringify(body).includes(KEY), 'the key never reaches the visitor');
}
ok('?set=media: any visitor gets the twelve media URLs (1 h), never cached, noindex; no model file among them');
for (const set of ['other', 'MEDIA', '__proto__', 'constructor', 'toString', '']) {
  reset();
  res = await signer.default(req('/twins/kld/assets?set=' + encodeURIComponent(set)));
  if (set === '') { assert.equal(res.status, 200, 'an empty set is the model set'); continue; }
  assert.equal(res.status, 400, `set ${set}`);
  assert.deepEqual(await res.json(), { error: 'unknown set' });
  assert.equal(sb.calls.length, 0, `nothing signed for set ${set}`);
}
ok('any other set: 400, nothing signed');

// only GET
reset();
for (const method of ['POST', 'PUT', 'DELETE']) {
  const res = await signer.default(req('/twins/kld/assets', { method }));
  assert.equal(res.status, 405);
}
assert.equal(sb.calls.length, 0);
ok('anything but GET: 405, nothing signed');

// fails closed without its key, and when Supabase won't sign
reset(); delete env.KLD_TWIN_SUPABASE_SECRET;
res = await signer.default(req('/twins/kld/assets'));
assert.equal(res.status, 503); assert.equal(sb.calls.length, 0);
reset(); env.KLD_TWIN_SUPABASE_SECRET = '   ';
res = await signer.default(req('/twins/kld/assets'));
assert.equal(res.status, 503); assert.equal(sb.calls.length, 0);
reset(); delete env.KLD_TWIN_SUPABASE_SECRET;
res = await signer.default(req('/twins/kld/assets?set=media'));
assert.equal(res.status, 503); assert.equal(sb.calls.length, 0);
ok('no key: 503 for either set, Supabase never asked');

const failures = {
  'Supabase refuses': () => json(400, { error: 'bad' }),
  'Supabase unreachable': () => { throw new TypeError('network'); },
  'Supabase times out': () => { const e = new Error('t'); e.name = 'TimeoutError'; throw e; },
  'not a list': () => json(200, { signedURL: '/object/sign/x' }),
  'a file missing': b => json(200, b.paths.slice(1).map(p => ({ path: p, signedURL: `/object/sign/site-twins/${p}?token=T` }))),
  'a file in error': b => json(200, b.paths.map((p, i) => ({ path: p, signedURL: i ? `/object/sign/site-twins/${p}?token=T` : null, error: i ? null : 'Not found' }))),
  'a URL elsewhere': b => json(200, b.paths.map(p => ({ path: p, signedURL: `https://evil.example/${p}` }))),
};
for (const path of ['/twins/kld/assets', '/twins/kld/assets?set=media']) {
  for (const [what, f] of Object.entries(failures)) {
    reset(); sb.sign = f;
    res = await signer.default(req(path));
    assert.equal(res.status, 503, `${path}: ${what}`);
    const body = await res.json();
    assert.deepEqual(Object.keys(body), ['error'], `${path}: ${what}`);
  }
}
ok('Supabase refusing, unreachable, slow or answering oddly: 503 with no URL, for either set');

assert.ok(logged.length > 0 && logged.every(l => !l.includes(KEY)), 'the key never reaches the log');
ok('the key never reaches the log');
console.log(`all ${n} KLD twin signer tests passed`);
