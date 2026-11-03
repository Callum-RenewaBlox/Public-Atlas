/* The KLD twin's files: /twins/kld/assets answers any visitor with short-lived signed URLs for the twin's four files
   (the exterior and interior Gaussian splats and two GLBs), which sit in a private Supabase Storage bucket. The page
   (kld_twin.html, served as /twins/kld/) asks here before it loads anything, and again on "Step inside" when its URLs
   are getting old (the interior splat is fetched only then); no URL, token or key is ever written into the page or
   this repository.

   The twin is public: anyone with the link may open it, so this function checks no session, and the sign-in
   (atlas-gate.js, which takes /clients/, /team/ and /access/ only) never runs here. What stays private is the key and
   the bucket: a visitor gets URLs that last five minutes, for these four files only.

   Set in Netlify (renewablox-atlas, Project configuration > Environment variables; a change needs a redeploy):
     KLD_TWIN_SUPABASE_SECRET  a Supabase secret API key of the renewablox-atlas project, made for this function alone
                               (named kld_twin_signer in Supabase > Project Settings > API Keys), so it can be revoked
                               on its own. Never put it in the page, the repository or a log. It must be available to
                               every deploy context (production and drafts alike).
   The files are in the bucket site-twins under kld/<random folder>/; the folder name is not a secret (the bucket is
   private and has no storage policies), it was changed once to retire signed URLs that had been published. The file
   names carry the layout's version (v5 GLBs, interior v1); a new version is uploaded beside the old under a new name. */

const SUPABASE_URL = 'https://mojwqeqgwyldbghlzgbq.supabase.co';   // renewablox-atlas (not the sign-in's project)
const BUCKET = 'site-twins';
const FOLDER = 'kld/08ef398ce6de02ef46118920a71665d1';
const FILES = { splat: 'kld_web.sog', kit: 'kld_dc_kit_v5.glb', hall: 'kld_hall_v5.glb', interior: 'kld_interior_v1.sog' };
const URL_SECONDS = 300;                 // how long a signed URL lasts: long enough to start the downloads, no more
const TIMEOUT_MS = 8000;

export const config = { path: '/twins/kld/assets' };

export default async (request) => {
  if (request.method !== 'GET') return answer(405, { error: 'GET only' });
  const key = String((globalThis.Netlify && Netlify.env.get('KLD_TWIN_SUPABASE_SECRET')) || '').trim();
  if (!key) {
    console.error('kld-twin-assets is locked until KLD_TWIN_SUPABASE_SECRET is set');
    return answer(503, { error: 'not set up' });
  }

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
