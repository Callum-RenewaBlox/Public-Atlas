/* The KLD twin's files: /clients/kld/twin-assets answers a signed-in visitor who may open KLD with short-lived signed
   URLs for the twin's three files (the Gaussian splat and two GLBs), which sit in a private Supabase Storage bucket.
   The page (kld_twin.html, served as /clients/kld/?view=twin) asks here before it loads anything; no URL, token or
   key is ever written into the page or this repository.

   The address is under /clients/, so the sign-in (atlas-gate.js) checks it first. This function does not rely on
   that: it opens the session cookie itself, with the gate's scheme (sealed below, which must match atlas-gate.js),
   and answers only an unexpired session whose access includes 'kld' or '*' (the team). Anything missing or wrong
   fails closed.

   Set in Netlify (renewablox-atlas, Project configuration > Environment variables; a change needs a redeploy):
     ATLAS_SESSION_SECRET      the sign-in's cookie secret (already set for the gate)
     KLD_TWIN_SUPABASE_SECRET  a Supabase secret API key of the renewablox-atlas project, made for this function alone
                               (named kld_twin_signer in Supabase > Project Settings > API Keys), so it can be revoked
                               on its own. Never put it in the page, the repository or a log.
   The files are in the bucket site-twins under kld/<random folder>/; the folder name is not a secret (the bucket is
   private and has no storage policies), it was changed once to retire signed URLs that had been published. */

const SUPABASE_URL = 'https://mojwqeqgwyldbghlzgbq.supabase.co';   // renewablox-atlas (not the sign-in's project)
const BUCKET = 'site-twins';
const FOLDER = 'kld/08ef398ce6de02ef46118920a71665d1';
const FILES = { splat: 'kld_web.sog', kit: 'kld_dc_kit.glb', hall: 'kld_hall.glb' };
const URL_SECONDS = 300;                 // how long a signed URL lasts: long enough to start the downloads, no more
const FILE_SECONDS = 6 * 3600;           // as the gate: files are served on an access answer up to this old
const SESSION_COOKIE = 'rbx_atlas';
const CLIENT = 'kld';
const TIMEOUT_MS = 8000;

export const config = { path: '/clients/kld/twin-assets' };

export default async (request) => {
  if (request.method !== 'GET') return answer(405, { error: 'GET only' });
  const env = k => String((globalThis.Netlify && Netlify.env.get(k)) || '').trim();
  const secret = env('ATLAS_SESSION_SECRET'), key = env('KLD_TWIN_SUPABASE_SECRET');
  if (secret.length < 32 || !key) {
    console.error('kld-twin-assets is locked until ATLAS_SESSION_SECRET and KLD_TWIN_SUPABASE_SECRET are set');
    return answer(503, { error: 'not set up' });
  }
  const session = await unseal(readCookie(request, SESSION_COOKIE), secret);
  if (!session) return answer(401, { error: 'sign in again' });
  if (now() - session.c > FILE_SECONDS) return answer(401, { error: 'open the page again' });
  if (!(session.a.includes('*') || session.a.includes(CLIENT))) return answer(403, { error: 'not shared with this account' });

  const paths = Object.values(FILES).map(f => `${FOLDER}/${f}`);
  let signed;
  try {
    const r = await fetch(`${SUPABASE_URL}/storage/v1/object/sign/${BUCKET}`, {
      method: 'POST', signal: AbortSignal.timeout(TIMEOUT_MS),
      headers: { apikey: key, authorization: `Bearer ${key}`, 'content-type': 'application/json' },
      body: JSON.stringify({ expiresIn: URL_SECONDS, paths })
    });
    if (!r.ok) { console.error('kld-twin-assets: Supabase refused to sign', r.status); return answer(503, { error: 'unavailable' }); }
    signed = await r.json();
  } catch (e) {
    console.error('kld-twin-assets: Supabase unreachable', String(e && e.name));
    return answer(503, { error: 'unavailable' });
  }
  const out = { expires_in: URL_SECONDS };
  for (const [name, file] of Object.entries(FILES)) {
    const row = Array.isArray(signed) && signed.find(s => s && s.path === `${FOLDER}/${file}`);
    if (!row || row.error || typeof row.signedURL !== 'string' || !row.signedURL.startsWith('/object/sign/')) {
      console.error('kld-twin-assets: no signed URL for', file);
      return answer(503, { error: 'unavailable' });
    }
    out[name] = `${SUPABASE_URL}/storage/v1${row.signedURL}`;
  }
  return answer(200, out);
};

function answer(status, body) {
  return new Response(JSON.stringify(body), { status, headers: {
    'content-type': 'application/json; charset=utf-8', 'cache-control': 'private, no-store', 'x-robots-tag': 'noindex, nofollow',
    'x-content-type-options': 'nosniff', 'referrer-policy': 'same-origin',
    'content-security-policy': "default-src 'none'; frame-ancestors 'none'" } });
}

/* ---- the session cookie, opened as atlas-gate.js seals it (AES-GCM under a key derived from the session secret) ---- */

const encoder = new TextEncoder(), decoder = new TextDecoder();
const AAD = encoder.encode('rbx-atlas-v1');
const keys = new Map();
function keyFor(secret) {
  if (!keys.has(secret)) {
    keys.set(secret, (async () => {
      const raw = await crypto.subtle.importKey('raw', encoder.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
      const derived = await crypto.subtle.sign('HMAC', raw, encoder.encode('atlas-sign-in-v1'));
      return crypto.subtle.importKey('raw', derived, { name: 'AES-GCM' }, false, ['decrypt']);
    })());
  }
  return keys.get(secret);
}
async function unseal(token, secret) {
  const [iv, ct, extra] = String(token || '').split('.');
  if (!iv || !ct || extra !== undefined) return null;
  try {
    const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: unb64url(iv), additionalData: AAD }, await keyFor(secret), unb64url(ct));
    const obj = JSON.parse(decoder.decode(plain));
    if (!obj || obj.t !== 'session' || !(Number(obj.x) > now())) return null;
    if (!(typeof obj.e === 'string' && Array.isArray(obj.a) && Number.isFinite(obj.c))) return null;
    return obj;
  } catch (e) { return null; }
}
const now = () => Math.floor(Date.now() / 1000);
function unb64url(s) {
  s = s.replace(/-/g, '+').replace(/_/g, '/');
  return Uint8Array.from(atob(s + '='.repeat((4 - s.length % 4) % 4)), c => c.charCodeAt(0));
}
function readCookie(request, name) {
  for (const part of (request.headers.get('cookie') || '').split(';')) {
    const i = part.indexOf('=');
    if (i > 0 && part.slice(0, i).trim() === name) return part.slice(i + 1).trim();
  }
  return '';
}
