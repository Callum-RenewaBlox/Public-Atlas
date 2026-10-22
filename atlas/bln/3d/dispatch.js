/* ===================================================================
   BLN dispatch — a simulated day of the miner rule
   The BLOX cabinet only ever takes what the export limit leaves. The rule
   agreed for BLN is led by the export meter alone: a miner starts each
   minute export sits at the 250 kW limit, and the last one started stops
   each minute export is at or under 245 kW. This module simulates a day of
   that rule against a synthetic river and draws it, so the 3D page can
   light the miners and turn the fans in step with it.
   No imports, no fetches, nothing on the DOM until mountDispatch is called,
   so Node can import it to test the rule on its own.
   =================================================================== */

export const N_MINERS = 20, MINER_KW = 3.4, EXPORT_CAP = 250, BAND_LO = 245, GEN_MAX = 300, MINUTES = 1440;

// Miners start in this order and stop in reverse, so the running set is always ORDER.slice(0, n).
export const ORDER = Object.freeze(Array.from({ length: N_MINERS }, (_, i) => i));

export const SCENARIOS = Object.freeze([
  { id: 'spate', label: 'Spate and recession',
    blurb: 'A low river overnight, under the band, then rain lifts it to the turbine’s 300 kW by about 09:00. It holds into the afternoon and falls away through the evening.' },
  { id: 'wet', label: 'Wet day',
    blurb: 'The river stays at or near 300 kW all day. Three short dips shed a few miners, which start again as the flow comes back.' },
  { id: 'showers', label: 'Showery',
    blurb: 'The river hovers about the band and each shower lifts it for an hour or so, so the miners start and stop through the day, with spells when all are off.' },
].map(Object.freeze));

// "At 250": the limiter holds export a hair under its set point, so a reading within 0.05 kW counts.
// Readings are stored in single precision, so the threshold is too, or 249.95 itself would miss.
const AT_CAP = Math.fround(EXPORT_CAP - 0.05);

/* ------------------------------------------------------------- the river */
// mulberry32: small, fast and the same on every machine, so a scenario is the same day for everyone.
function mulberry32(seed){
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function gauss(rand){
  const u = rand() || 1e-12, v = rand();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}
// Mean-reverting noise: a turbine's output wanders minute to minute but never drifts away.
function ar1(rand, sd, phi){
  const e = new Float64Array(MINUTES), k = sd * Math.sqrt(1 - phi * phi);
  e[0] = sd * gauss(rand);
  for (let t = 1; t < MINUTES; t++) e[t] = phi * e[t - 1] + k * gauss(rand);
  return e;
}
const smooth = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const H = (h, m = 0) => h * 60 + m;
// A shower on the hills reaches the intake as a quick rise and a longer fall: a gamma-shaped bump,
// height a at k minutes after it starts.
const pulse = (t, t0, a, k, s = 2.4) => {
  const x = (t - t0) / k;
  return x <= 0 ? 0 : a * Math.pow(x, s) * Math.exp(s * (1 - x));
};

// Each returns what the river could make, kW, before the turbine's 300 kW ceiling.
const RIVER = {
  spate(t){
    const base = 239.2 - 4.6 * smooth(t / MINUTES) + 0.9 * Math.sin(t / 97);
    const rise = 80 * smooth((t - H(5)) / 330);
    return base + (t < H(13) ? rise : 80 * Math.exp(-(t - H(13)) / 180));
  },
  wet(t){
    const dip = (c, d, w) => d * Math.exp(-0.5 * ((t - c) / w) ** 2);
    return 313 + 3 * Math.sin(t / 151) - dip(H(7, 20), 37, 21) - dip(H(13, 50), 29, 15) - dip(H(19, 10), 34, 27);
  },
  showers(t){
    const base = 246.6 + 3.6 * Math.sin(2 * Math.PI * t / 610 + 0.9) + 1.4 * Math.sin(2 * Math.PI * t / 173);
    return base + pulse(t, H(0, 40), 15, 38) + pulse(t, H(4, 10), 31, 52) + pulse(t, H(8, 20), 13, 30)
      + pulse(t, H(11, 10), 38, 48) + pulse(t, H(15, 0), 20, 42) + pulse(t, H(19, 0), 34, 58) + pulse(t, H(22, 20), 11, 28);
  },
};
const SEED = { spate: 7, wet: 11, showers: 23 };
// Own keys only: 'toString' or '__proto__' must not pass for a river.
const known = (id) => typeof id === 'string' && Object.prototype.hasOwnProperty.call(RIVER, id);

function river(id){
  const rand = mulberry32(SEED[id]), noise = ar1(rand, 0.7, 0.95), f = RIVER[id], a = new Float32Array(MINUTES);
  for (let t = 0; t < MINUTES; t++) a[t] = Math.max(0, Math.min(GEN_MAX, f(t) + noise[t]));
  return a;
}

/* ----------------------------------------------------- the rule, a minute at a time */
const ambientAt = (t) => 11 + 3 * Math.sin(2 * Math.PI * (t / 60 - 9) / 24);
// Illustrative thermal figures, not a design: a 450 mm wall fan moves about 4,900 m³/h (1.35 m³/s),
// and the hot-air space leaks a little on its own. Air carries 1.2 kg/m³ × 1005 J/kg·K.
const FAN_M3S = 1.35, LEAK_M3S = 0.15, RHO_CP = 1.2 * 1005, TAU_MIN = 4;
// The thermostat, illustrative too: the lead fan comes on at 24 °C and the second at 32 °C. Each fan
// moves the space by more than a narrow gap between on and off (the second is worth about 13 K with
// 15 miners running), so with one it would switch every few minutes. The second fan therefore waits
// for 21 °C to stop, and a run timer keeps a fan on for a while once started and the second off for a
// while once stopped, as a real controller's would.
const FAN1_ON = 24, FAN1_OFF = 20, FAN2_ON = 32, FAN2_OFF = 21;
const FAN1_RUN = 10, FAN2_RUN = 20, FAN2_REST = 10;   // minutes

function run(id, avail){
  const exp = new Float32Array(MINUTES), spill = new Float32Array(MINUTES), running = new Uint8Array(MINUTES);
  const fan1 = new Uint8Array(MINUTES), fan2 = new Uint8Array(MINUTES), temp = new Float32Array(MINUTES), ambient = new Float32Array(MINUTES);
  const events = [];
  let n = 0;
  for (let t = 0; t < MINUTES; t++) {
    running[t] = n;
    const net = avail[t] - n * MINER_KW;
    // The limiter throttles the turbine rather than let export pass 250; what it holds back is spilt.
    // Decide on the stored (single-precision) reading, so the record and the decision always agree.
    const e = Math.fround(Math.min(EXPORT_CAP, net));
    exp[t] = e;
    spill[t] = Math.max(0, net - EXPORT_CAP);
    if (t === MINUTES - 1) break;   // a decision on the last reading would land tomorrow
    // A change acts from the next minute: an event's t is when the miner starts or stops, and its exp
    // is the reading the minute before that called for it.
    if (e >= AT_CAP && n < N_MINERS) {
      const m = ORDER[n++];
      events.push(Object.freeze({ t: t + 1, type: 'start', miner: m, exp: e, running: n,
        reason: `Export at the 250 kW limit: start miner ${m + 1}` }));
    } else if (e <= BAND_LO && n > 0) {
      const m = ORDER[--n];
      events.push(Object.freeze({ t: t + 1, type: 'stop', miner: m, exp: e, running: n,
        reason: `Export ${e.toFixed(1)} kW, at or under 245: stop miner ${m + 1}` }));
    }
  }

  // The hot-air space, as a first-order lag towards the temperature its airflow would settle at.
  // "1 will turn on initially": the lead fan comes on as the first miners warm the space, then runs for
  // as long as any miner does (a light load would otherwise cycle it, since one fan cools a miner or two
  // well below 20 °C), and once the cabinet is idle it stops at 20 °C. The second fan comes and goes on
  // the thermostat, and never runs without the lead.
  const k = 1 - Math.exp(-1 / TAU_MIN);
  let T = ambientAt(0), f1 = 0, f2 = 0, h1 = 0, h2 = FAN2_REST;   // h: minutes in the present state
  for (let t = 0; t < MINUTES; t++) {
    const amb = ambientAt(t), V = LEAK_M3S + FAN_M3S * (f1 + f2);
    ambient[t] = amb;
    T += (amb + running[t] * MINER_KW * 1000 / (RHO_CP * V) - T) * k;
    temp[t] = T;
    h1++; h2++;
    if (!f1 && T >= FAN1_ON) { f1 = 1; h1 = 0; }
    else if (f1 && T <= FAN1_OFF && !running[t] && h1 >= FAN1_RUN) { f1 = 0; h1 = 0; }
    if (!f2 && f1 && T >= FAN2_ON && h2 >= FAN2_REST) { f2 = 1; h2 = 0; }
    else if (f2 && (!f1 || (T <= FAN2_OFF && h2 >= FAN2_RUN))) { f2 = 0; h2 = 0; }
    fan1[t] = f1; fan2[t] = f2;
  }

  let toMiners = 0, exported = 0, spilled = 0, without = 0, runMin = 0, maxRunning = 0;
  for (let t = 0; t < MINUTES; t++) {
    toMiners += running[t] * MINER_KW; exported += exp[t]; spilled += spill[t];
    without += Math.max(0, avail[t] - EXPORT_CAP); runMin += running[t];
    if (running[t] > maxRunning) maxRunning = running[t];
  }
  const starts = events.filter((e) => e.type === 'start').length;
  return {
    id, avail, exp, running, fan1, fan2, temp, ambient, spill, events: Object.freeze(events),
    totals: Object.freeze({ toMinersKWh: toMiners / 60, exportKWh: exported / 60, spilledKWh: spilled / 60,
      spilledWithoutKWh: without / 60, maxRunning, starts, stops: events.length - starts, runHours: runMin / 60 }),
  };
}

const memo = new Map();
// simulate('spate' | 'wet' | 'showers'); an unknown id falls back to the default. For tests and what-ifs
// it also takes 1440 minutes of available power (kW) in place of an id, which is never memoised.
export function simulate(id = SCENARIOS[0].id){
  if (id && typeof id === 'object' && typeof id.length === 'number') {
    const a = new Float32Array(MINUTES);
    for (let t = 0; t < MINUTES; t++) a[t] = Math.max(0, Math.min(GEN_MAX, +id[Math.min(t, id.length - 1)] || 0));
    return run('custom', a);
  }
  if (!known(id)) id = SCENARIOS[0].id;
  if (!memo.has(id)) memo.set(id, run(id, river(id)));
  return memo.get(id);
}

const pad2 = (v) => String(v).padStart(2, '0');
const clockOf = (t) => pad2(Math.floor(t / 60)) + ':' + pad2(t % 60);

export function stateAt(sim, t){
  t = Math.max(0, Math.min(MINUTES - 1, Math.floor(+t || 0)));
  const n = sim.running[t], on = new Array(N_MINERS).fill(false);
  for (let i = 0; i < n; i++) on[ORDER[i]] = true;
  return { t, clock: clockOf(t), avail: sim.avail[t], exp: sim.exp[t], running: n, on,
    fan1: !!sim.fan1[t], fan2: !!sim.fan2[t], temp: sim.temp[t], cabinetKw: Math.round(n * MINER_KW * 10) / 10 };
}

/* ===================================================================
   The chart: header, readouts, two charts on one time axis, scrubber,
   and behind one switch the day's totals and the table of changes. It
   fills its container's width and takes the height it needs.
   =================================================================== */
const SPEEDS = [2, 10, 30, 120];
const SHORT = { spate: 'Spate', wet: 'Wet day', showers: 'Showery' };
const Y_LO = 230, Y_HI = 304, A_TICKS = [250, 275, 300];
const X_TICKS = [0, 360, 720, 1080, 1440];
const COMPACT_W = 520;
// While playing, the screen reader hears a change only at a reading pace, and never more often than
// this; faster than that it would hear nothing but numbers.
const SAY_SPEED = 10, SAY_GAP_MS = 1800;
let mounts = 0;

const kw1 = (v) => v.toFixed(1);
const kwh = (v) => (v < 1 ? 'under 1' : Math.round(v).toLocaleString('en-GB'));
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
// The fans as one level: 0 off, 1 the lead alone, 2 both. Words for the tile, the narrow tile and speech.
const fanLevel = (s) => (s.fan2 ? 2 : s.fan1 ? 1 : 0);
const FANS_TEXT = ['Off', 'Lead fan', 'Both fans'], FANS_SHORT = ['Off', 'Lead', 'Both'];
const FANS_SAY = ['fans off', 'lead fan on', 'both fans on'];

// Every change in the day, for the table and the read-out: each miner start and stop, and each fan
// switching, in time order. A fan answers a miner in the same minute, so it sorts after it.
const rowsMemo = new WeakMap();
function changes(sim){
  if (rowsMemo.has(sim)) return rowsMemo.get(sim);
  // a miner's change was called for by the reading the minute before; a fan's by its own minute's
  const rows = sim.events.map((e) => ({ t: e.t, at: e.t - 1, up: e.type === 'start', fan: false,
    text: `${e.type === 'start' ? 'Start' : 'Stop'} miner ${e.miner + 1}`, say: e.reason }));
  const fanRow = (t, up, which) => {
    const T = sim.temp[t].toFixed(1);
    const say = up ? `Hot-air space at ${T} °C: ${which.toLowerCase()} fan on`
      : which === 'Lead' ? `Cabinet idle and the space down to ${T} °C: lead fan off`
      : `Hot-air space down to ${T} °C: second fan off`;
    rows.push({ t, at: t, up, fan: true, text: `${which} fan ${up ? 'on' : 'off'}`, say });
  };
  for (let t = 1; t < MINUTES; t++) {
    if (sim.fan1[t] > sim.fan1[t - 1]) fanRow(t, true, 'Lead');
    if (sim.fan2[t] > sim.fan2[t - 1]) fanRow(t, true, 'Second');
    if (sim.fan2[t] < sim.fan2[t - 1]) fanRow(t, false, 'Second');
    if (sim.fan1[t] < sim.fan1[t - 1]) fanRow(t, false, 'Lead');
  }
  rows.sort((a, b) => a.t - b.t);   // a stable sort, so the miners stay ahead of the fans they set off
  rowsMemo.set(sim, rows);
  return rows;
}

// Series colours, checked with the dataviz validator against the glass panel (#fbfdfe): export, miners
// and fans as a categorical set; "available" is a muted dashed line beside them. The fans lane tells the
// lead fan from both by height, half and full, so it needs only the one colour.
// Text never wears them; they mark lines, fills and the small keys beside the labels.
const CSS = `
.dsp-root{--dsp-ink:var(--ink,#0d1b23);--dsp-ink-2:var(--ink-2,#33454f);--dsp-muted:var(--muted,#5a6a73);--dsp-muted-2:var(--muted-2,#93a2aa);
  --dsp-line:var(--line,#dfe8ed);--dsp-line-2:var(--line-2,#edf3f6);--dsp-tint:var(--tint,#f4f8fa);--dsp-tint-2:var(--tint-2,#eaf1f5);
  --dsp-brand:var(--brand,#12475e);--dsp-accent:var(--accent,#1f5f7f);--dsp-accent-l:var(--accent-l,#3a89ae);--dsp-surface:#fbfdfe;
  --dsp-font:var(--font,"Inter",system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif);
  --dsp-exp:#1f6596;--dsp-avail:#7d8d96;--dsp-run:#0f9d77;--dsp-fan:#bf5610;
  position:relative;display:flex;flex-direction:column;gap:8px;min-width:0;max-width:100%;
  font-family:var(--dsp-font);font-size:12px;line-height:1.45;color:var(--dsp-ink-2);-webkit-font-smoothing:antialiased}
.dsp-root *,.dsp-root *::before,.dsp-root *::after{box-sizing:border-box}
.dsp-root :focus{outline:none}
.dsp-root :focus-visible{outline:2px solid var(--dsp-accent-l);outline-offset:2px}
.dsp-root button,.dsp-root select{font-family:inherit}
.dsp-root [hidden]{display:none!important}
.dsp-sr{position:absolute!important;width:1px;height:1px;margin:-1px;padding:0;border:0;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap}
/* the header: the kicker and the rule on lines of their own, kept clear of the top right corner, where a
   host panel may put its close button; then the river chooser, with speed and play to its right */
.dsp-head{display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px}
.dsp-title{flex:1 1 100%;min-width:0;padding-right:var(--dsp-head-inset,28px)}
.dsp-k{font-size:9.6px;line-height:1.4;font-weight:750;letter-spacing:.16em;text-transform:uppercase;color:var(--dsp-accent)}
.dsp-rule{margin:1px 0 0;font-size:11.8px;line-height:1.4;color:var(--dsp-ink-2)}
.dsp-seg{display:inline-flex;gap:2px;padding:2px;background:var(--dsp-tint-2);border:1px solid var(--dsp-line);border-radius:11px;min-width:0}
.dsp-seg button{border:0;background:transparent;font-size:11.6px;font-weight:650;color:var(--dsp-muted);padding:4px 10px;border-radius:9px;cursor:pointer;
  white-space:nowrap;transition:background .16s,color .16s,box-shadow .16s}
.dsp-seg button[aria-pressed="true"]{background:var(--dsp-brand);color:#fff;box-shadow:0 1px 2px rgba(9,26,35,.18),0 3px 10px rgba(18,71,94,.28)}
.dsp-short{display:none}
.dsp-grow{flex:1 1 auto}
.dsp-pl{display:flex;align-items:center;gap:8px;flex:0 0 auto;margin-left:auto}
.dsp-spd{position:relative;display:inline-flex;flex:0 0 auto}
.dsp-spd select{-webkit-appearance:none;appearance:none;margin:0;border:1px solid var(--dsp-line);background:var(--dsp-tint);color:var(--dsp-accent);
  font-size:11.3px;font-weight:650;padding:4px 25px 4px 11px;border-radius:var(--r-pill,999px);cursor:pointer;line-height:1.3}
.dsp-spd::after{content:"";position:absolute;right:11px;top:50%;width:5px;height:5px;border-right:1.6px solid var(--dsp-accent);border-bottom:1.6px solid var(--dsp-accent);
  transform:translateY(-70%) rotate(45deg);pointer-events:none}
.dsp-play{flex:0 0 auto;display:inline-flex;align-items:center;gap:6px;border:0;background:var(--dsp-brand);color:#fff;font-size:11.6px;font-weight:650;
  padding:5px 13px 5px 10px;border-radius:var(--r-pill,999px);cursor:pointer;box-shadow:0 1px 2px rgba(9,26,35,.18),0 3px 10px rgba(18,71,94,.24);transition:background .15s}
.dsp-play svg{width:11px;height:11px;display:block;flex:0 0 auto}
.dsp-tiles{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px}
.dsp-tile{min-width:0;background:rgba(244,248,250,.86);border:1px solid var(--dsp-line-2);border-radius:var(--r-s,8px);padding:3px 8px 4px}
.dsp-tl{font-size:10.2px;line-height:1.3;color:var(--dsp-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
/* the readouts change every simulated minute, so their digits are all one width and the tiles hold still */
.dsp-tv{font-size:14.5px;line-height:1.3;font-weight:700;letter-spacing:-.01em;color:var(--dsp-ink);font-variant-numeric:tabular-nums;white-space:nowrap}
.dsp-tv small{font-size:10.2px;font-weight:600;color:var(--dsp-muted);margin-left:2px;letter-spacing:0}
.dsp-fig{margin:0;min-width:0}
.dsp-plots{position:relative;touch-action:pan-y;cursor:crosshair;-webkit-user-select:none;user-select:none;-webkit-tap-highlight-color:transparent}
.dsp-cap{display:flex;flex-wrap:wrap;align-items:center;gap:2px 11px;font-size:10.8px;line-height:1.35;color:var(--dsp-ink-2);margin:0 0 3px}
.dsp-svg+.dsp-svg{margin-top:5px}
.dsp-leg{display:inline-flex;align-items:center;gap:5px;font-weight:600;white-space:nowrap}
.dsp-leg svg,.dsp-tip svg{display:block;flex:0 0 auto}
.dsp-wash{display:block;flex:0 0 auto;width:10px;height:8px;background:rgba(15,157,119,.16);box-shadow:inset 0 2px 0 var(--dsp-run);border-radius:1px}
.dsp-svg{display:block;width:100%;overflow:visible}
.dsp-svg text{font-family:var(--dsp-font)}
.dsp-grid{stroke:var(--dsp-line);stroke-width:1;fill:none;shape-rendering:crispEdges}
.dsp-vgrid{stroke:var(--dsp-line-2);stroke-width:1;fill:none;shape-rendering:crispEdges}
.dsp-ax{font-size:9.6px;fill:var(--dsp-muted);font-variant-numeric:tabular-nums}
/* the band is chart furniture, so it is a neutral wash: teal means only the miners */
.dsp-band{fill:var(--dsp-ink);fill-opacity:.07}
.dsp-limit{stroke:var(--dsp-muted);stroke-width:1;shape-rendering:crispEdges}
.dsp-l-avail{fill:none;stroke:var(--dsp-avail);stroke-width:2;stroke-dasharray:5 4;stroke-linejoin:round;stroke-linecap:round}
.dsp-l-exp{fill:none;stroke:var(--dsp-exp);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.dsp-a-run{fill:var(--dsp-run);fill-opacity:.12}
.dsp-l-run{fill:none;stroke:var(--dsp-run);stroke-width:2;stroke-linejoin:round}
.dsp-fan{fill:var(--dsp-fan)}
.dsp-lab{font-size:9.8px;font-weight:650;fill:var(--dsp-ink-2);paint-order:stroke;stroke:var(--dsp-surface);stroke-width:3px;stroke-linejoin:round}
.dsp-ph{stroke:var(--dsp-ink);stroke-width:1.5;shape-rendering:crispEdges}
.dsp-xh{stroke:var(--dsp-muted-2);stroke-width:1;shape-rendering:crispEdges}
.dsp-dot-exp{fill:var(--dsp-exp);stroke:var(--dsp-surface);stroke-width:2}
.dsp-dot-run{fill:var(--dsp-run);stroke:var(--dsp-surface);stroke-width:2}
.dsp-tip{position:absolute;left:0;top:0;z-index:3;pointer-events:none;background:rgba(255,255,255,.97);border-radius:var(--r-m,12px);
  box-shadow:var(--sh-2,0 2px 6px rgba(9,26,35,.12),0 14px 44px rgba(9,26,35,.22));padding:7px 10px 8px;font-size:11.2px;line-height:1.35;color:var(--dsp-ink-2);white-space:nowrap}
.dsp-tip-h{font-size:11.6px;font-weight:750;color:var(--dsp-ink);margin-bottom:3px;font-variant-numeric:tabular-nums}
.dsp-tip-g{display:grid;grid-template-columns:auto auto auto;column-gap:7px;row-gap:1px;align-items:center}
.dsp-tip-g b{font-weight:700;color:var(--dsp-ink);text-align:right;font-variant-numeric:tabular-nums}
.dsp-tip-g span{color:var(--dsp-muted)}
.dsp-tip-g i{display:block;width:12px;height:2.5px;border-radius:2px;background:var(--c)}
.dsp-tip-g i.dsp-none{background:none}
.dsp-c-exp{--c:var(--dsp-exp)} .dsp-c-run{--c:var(--dsp-run)}
/* one row under the charts: the time, the scrubber, the two steps between changes and the switch */
.dsp-scrub{display:flex;flex-wrap:wrap;align-items:center;gap:6px}
.dsp-clock{flex:0 0 auto;min-width:36px;font-size:12.4px;font-weight:700;color:var(--dsp-ink);font-variant-numeric:tabular-nums}
.dsp-range{flex:1 1 90px;min-width:0;width:100%;margin:0 4px 0 0;height:20px;accent-color:var(--dsp-brand);cursor:pointer;background:transparent}
.dsp-btn{flex:0 0 auto;border:1px solid var(--dsp-line);background:var(--dsp-tint);color:var(--dsp-accent);font-size:11.3px;font-weight:650;padding:5px 11px;
  border-radius:var(--r-pill,999px);cursor:pointer;white-space:nowrap;transition:background .15s,border-color .15s,color .15s}
.dsp-step{display:inline-flex;align-items:center;justify-content:center;width:30px;height:24px;padding:0}
.dsp-step svg{width:12px;height:12px;display:block}
/* a step with nowhere to go stays focusable, so the keyboard is not thrown back to the page */
.dsp-btn[aria-disabled="true"]{opacity:.45;cursor:default}
/* the rail's switch: the knob is the last flex item and reaches back over the gap and the track */
.dsp-tg{position:relative;margin:-4px 0 -4px 0;flex:0 0 auto;display:flex;align-items:center;gap:9px;border:0;background:transparent;border-radius:10px;
  padding:5px 9px;font-size:12px;font-weight:620;color:var(--dsp-ink-2);cursor:pointer;text-align:left;white-space:nowrap;transition:background .14s,color .14s}
.dsp-tg::after{content:"";order:2;flex:0 0 auto;width:24px;height:14px;border-radius:9px;background:#7d8d96;box-shadow:inset 0 0 0 1px rgba(9,26,35,.06);transition:background .16s}
.dsp-tg::before{content:"";order:3;position:relative;flex:0 0 auto;margin-left:-31px;margin-right:12px;width:10px;height:10px;border-radius:50%;background:#fff;
  box-shadow:0 1px 2px rgba(9,26,35,.3);transition:transform .16s var(--ease,ease)}
.dsp-tg[aria-pressed="true"]::after{background:var(--teal,#0f9d77)}
.dsp-tg[aria-pressed="true"]::before{transform:translateX(10px)}
.dsp-more{display:flex;flex-direction:column;gap:7px}
.dsp-tot{margin:0;font-size:11.4px;line-height:1.5;color:var(--dsp-ink-2)}
.dsp-tot b{font-weight:700;color:var(--dsp-ink)}
.dsp-note{margin:0;font-size:10.4px;line-height:1.45;color:var(--dsp-muted)}
.dsp-tbl{position:relative;max-height:164px;overflow:auto;border:1px solid var(--dsp-line);border-radius:var(--r-m,12px);background:#fff;scrollbar-width:thin;overscroll-behavior:contain}
.dsp-tbl table{width:100%;border-collapse:collapse;font-size:11.4px;font-variant-numeric:tabular-nums}
.dsp-tbl th{position:sticky;top:0;z-index:1;background:var(--dsp-tint);text-align:left;font-size:9.6px;font-weight:750;letter-spacing:.1em;text-transform:uppercase;
  color:var(--dsp-muted);padding:6px 7px;border-bottom:1px solid var(--dsp-line);white-space:nowrap}
/* units keep their case: kW is not KW */
.dsp-tbl .dsp-u{text-transform:none;letter-spacing:0}
.dsp-tbl td{padding:2px 7px;border-bottom:1px solid var(--dsp-line-2);color:var(--dsp-ink-2);white-space:nowrap}
.dsp-tbl .dsp-n{text-align:right}
.dsp-tbl tr.dsp-cur td{background:var(--dsp-tint-2)}
.dsp-tbl tr:last-child td{border-bottom:0}
.dsp-tt{border:0;background:none;padding:1px 0;font:inherit;font-weight:650;color:var(--dsp-accent);cursor:pointer;text-decoration:underline;
  text-decoration-color:rgba(31,95,127,.35);text-underline-offset:2px}
.dsp-chg{display:inline-flex;align-items:center;gap:6px}
.dsp-chg i{display:block;width:0;height:0;border-left:4px solid transparent;border-right:4px solid transparent}
.dsp-chg i.dsp-up{border-bottom:6px solid var(--dsp-run)}
.dsp-chg i.dsp-fup{border-bottom:6px solid var(--dsp-fan)}
.dsp-chg i.dsp-dn{border-top:6px solid var(--dsp-muted)}
/* narrow: the same parts, closer together, with shorter words where a long one would not fit */
.dsp-compact{gap:6px}
.dsp-compact .dsp-rule{font-size:11.2px}
.dsp-compact .dsp-grow{display:none}
.dsp-compact .dsp-full,.dsp-compact .dsp-play span{display:none}
.dsp-compact .dsp-short{display:inline}
.dsp-compact .dsp-play{padding:6px 9px}
.dsp-compact .dsp-seg{flex:1 1 auto}
.dsp-compact .dsp-seg button{flex:1 1 0;padding:4px 5px}
.dsp-compact .dsp-spd select{padding-left:9px;padding-right:22px}
.dsp-compact .dsp-spd::after{right:9px}
/* the readouts become one strip of five, divided by hairlines rather than boxed */
.dsp-compact .dsp-tiles{gap:0}
.dsp-compact .dsp-tile{background:none;border:0;border-left:1px solid var(--dsp-line);border-radius:0;padding:0 3px 0 6px}
.dsp-compact .dsp-tile:first-child{border-left:0;padding-left:0}
.dsp-compact .dsp-tl{font-size:10px}
.dsp-compact .dsp-tv{font-size:13px;letter-spacing:0}
.dsp-compact .dsp-tv small{font-size:9.6px;margin-left:1px}
.dsp-compact .dsp-head{row-gap:5px}
.dsp-compact .dsp-cap{gap:2px 8px;font-size:10.4px;margin-bottom:2px}
.dsp-compact .dsp-svg+.dsp-svg{margin-top:4px}
.dsp-compact .dsp-leg{gap:4px}
/* a narrow table drops the river, which the tooltip and the scrubber's spoken value still give, and puts
   each unit under its heading, so the rest fits without a sideways scroll */
.dsp-compact .dsp-tbl th,.dsp-compact .dsp-tbl td{padding-left:5px;padding-right:5px}
.dsp-compact .dsp-tbl th{letter-spacing:.06em;vertical-align:bottom}
.dsp-compact .dsp-tbl .dsp-u{display:block}
.dsp-compact .dsp-rv{display:none}
/* hover looks only where there is a pointer that hovers, so a tapped control does not stay lit */
@media (hover:hover){
  .dsp-seg button:hover{color:var(--dsp-brand);background:rgba(255,255,255,.7)}
  .dsp-seg button[aria-pressed="true"]:hover{color:#fff;background:var(--dsp-brand)}
  .dsp-spd select:hover{border-color:var(--dsp-accent-l)}
  .dsp-play:hover{background:var(--dsp-accent)}
  .dsp-btn:hover:not([aria-disabled="true"]){background:var(--dsp-accent);border-color:var(--dsp-accent);color:#fff}
  .dsp-tg:hover{background:var(--dsp-tint-2);color:var(--dsp-brand)}
  .dsp-tt:hover{color:var(--dsp-brand);text-decoration-color:currentColor}
}
@media (prefers-reduced-motion:reduce){ .dsp-root *,.dsp-root *::before,.dsp-root *::after{transition:none!important;animation:none!important} }
`;

const ICON_PLAY = '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M3 1.6v8.8l7.2-4.4z" fill="currentColor"/></svg>';
const ICON_PAUSE = '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.6 1.6h2.4v8.8H2.6zM7 1.6h2.4v8.8H7z" fill="currentColor"/></svg>';
const ICON_REPLAY = '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M10 6.2A4 4 0 1 1 8.6 3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M10.2 1.4v2.8H7.4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
// skip back and on, a bar and a chevron: to the change before, or the next one
const ICON_PREV = '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.6 2.2v7.6M9.4 2.2L4.8 6l4.6 3.8" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const ICON_NEXT = '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M9.4 2.2v7.6M2.6 2.2L7.2 6 2.6 9.8" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const KEY_EXP = '<svg width="14" height="4" aria-hidden="true"><line x1="1" y1="2" x2="13" y2="2" stroke="#1f6596" stroke-width="2" stroke-linecap="round"/></svg>';
const KEY_AVAIL = '<svg width="16" height="4" aria-hidden="true"><line x1="1" y1="2" x2="15" y2="2" stroke="#7d8d96" stroke-width="2" stroke-dasharray="5 4" stroke-linecap="round"/></svg>';
// the fans' keys are the lane in small: half height for the lead fan alone, full for both
const KEY_F1 = '<svg width="10" height="8" aria-hidden="true"><rect class="dsp-fan" x="0" y="4" width="10" height="4" rx="1"/></svg>';
const KEY_F2 = '<svg width="10" height="8" aria-hidden="true"><rect class="dsp-fan" x="0" y="0" width="10" height="8" rx="1"/></svg>';

function injectStyle(){
  if (document.getElementById('dsp-style')) return;
  const s = document.createElement('style');
  s.id = 'dsp-style';
  s.textContent = CSS;
  document.head.appendChild(s);
}

// The first item after minute t, by binary search: the lists are in time order.
function eventAfter(list, t){
  let lo = 0, hi = list.length;
  while (lo < hi) { const mid = (lo + hi) >> 1; if (list[mid].t > t) hi = mid; else lo = mid + 1; }
  return lo;
}

export function mountDispatch(el, opts = {}){
  injectStyle();
  const uid = 'dsp' + (++mounts);
  let onState = typeof opts.onState === 'function' ? opts.onState : null;
  let sim = simulate(known(opts.scenario) ? opts.scenario : undefined);
  let t = clamp(Math.floor(+opts.start || 0), 0, MINUTES - 1), pos = t;
  let speed = +opts.speed > 0 ? +opts.speed : 10;
  let playing = false, raf = 0, last = 0, alive = true;
  let width = 0, compact = false, geo = null;
  let hoverT = -1, tipPinned = false, drag = null;
  let sayTimer = 0, lastSay = 0, curRow = -1;

  const root = document.createElement('div');
  root.className = 'dsp-root';
  root.setAttribute('role', 'group');
  root.setAttribute('aria-labelledby', uid + '-k');
  const speedOpts = (v) => {
    const list = SPEEDS.includes(v) ? SPEEDS : [...SPEEDS, v].sort((a, b) => a - b);
    return list.map((s) => `<option value="${s}"${s === v ? ' selected' : ''}>${s} min/s</option>`).join('');
  };
  const both = (full, short) => `<span class="dsp-full">${full}</span><span class="dsp-short">${short}</span>`;
  const tile = (key, full, short, unit = '') =>
    `<div class="dsp-tile"><div class="dsp-tl">${both(full, short)}</div><div class="dsp-tv"><span data-r="${key}">–</span>${unit ? `<small>${unit}</small>` : ''}</div></div>`;
  root.innerHTML = `
<div class="dsp-head">
  <div class="dsp-title">
    <div class="dsp-k" id="${uid}-k">Technical dispatch · simulated day</div>
    <p class="dsp-rule">${both('A miner starts each minute export is at 250 kW, and one stops at or under 245 kW.', 'Export at 250 kW starts a miner; 245 or under stops one.')}</p>
  </div>
  <div class="dsp-seg" role="group" aria-label="River">${SCENARIOS.map((s) =>
    `<button type="button" data-sc="${s.id}" aria-pressed="false" title="${s.blurb}">${both(s.label, SHORT[s.id])}</button>`).join('')}</div>
  <span class="dsp-grow"></span>
  <div class="dsp-pl">
    <label class="dsp-spd"><span class="dsp-sr">Playback speed, simulated minutes a second</span><select data-speed>${speedOpts(speed)}</select></label>
    <button type="button" class="dsp-play" data-play></button>
  </div>
</div>
<div class="dsp-tiles">
  ${tile('exp', 'Export', 'Export', 'kW')}
  ${tile('run', 'Miners running', 'Miners', `of ${N_MINERS}`)}
  ${tile('kw', 'To the cabinet', 'Cabinet', 'kW')}
  ${tile('fans', 'Fans', 'Fans')}
  ${tile('temp', 'Hot-air space', 'Hot air', '°C')}
</div>
<figure class="dsp-fig">
  <figcaption class="dsp-sr">The simulated day: export and the power available from the river, kW, and below them the miners running and the fans. The table under “Show the events” lists every change.</figcaption>
  <div class="dsp-plots" data-plots>
    <div class="dsp-cap" aria-hidden="true">
      <span class="dsp-leg">${KEY_EXP}Export</span><span class="dsp-leg">${KEY_AVAIL}${both('Available from the river', 'Available')}</span>
      <span class="dsp-leg"><i class="dsp-wash"></i>${both('Miners running', 'Miners')}</span>
      <span class="dsp-leg">${KEY_F1}Lead fan</span><span class="dsp-leg">${KEY_F2}${both('Both fans', 'Both')}</span></div>
    <svg class="dsp-svg" data-a role="img"></svg>
    <svg class="dsp-svg" data-b role="img"></svg>
    <div class="dsp-tip" data-tip hidden aria-hidden="true">
      <div class="dsp-tip-h" data-tt></div>
      <div class="dsp-tip-g">
        <i class="dsp-c-exp"></i><b data-tv="exp"></b><span>Export</span>
        <svg width="12" height="4"><line x1="1" y1="2" x2="11" y2="2" stroke="#7d8d96" stroke-width="2" stroke-dasharray="4 3"/></svg><b data-tv="avail"></b><span>Available</span>
        <i class="dsp-c-run"></i><b data-tv="run"></b><span>Miners running</span>
        <svg width="12" height="8"><rect class="dsp-fan" data-tv="fankey" x="1" y="0" width="10" height="8" rx="1"/></svg><b data-tv="fans"></b><span>Fans</span>
        <i class="dsp-none"></i><b data-tv="temp"></b><span>Hot-air space</span>
      </div>
    </div>
  </div>
</figure>
<div class="dsp-scrub">
  <span class="dsp-clock" data-clock aria-hidden="true">00:00</span>
  <label class="dsp-sr" for="${uid}-r">Time of day</label>
  <input class="dsp-range" id="${uid}-r" type="range" min="0" max="${MINUTES - 1}" step="1" value="${t}">
  <button type="button" class="dsp-btn dsp-step" data-go="-1" aria-label="Previous change" title="Previous change: the last miner start or stop">${ICON_PREV}</button>
  <button type="button" class="dsp-btn dsp-step" data-go="1" aria-label="Next change" title="Next change: the next miner start or stop">${ICON_NEXT}</button>
  <button type="button" class="dsp-tg" data-tg aria-pressed="false" aria-controls="${uid}-m">${both('Show the events', 'Events')}</button>
</div>
<div class="dsp-more" id="${uid}-m" data-more hidden>
  <p class="dsp-tot" data-tot></p>
  <div class="dsp-tbl" data-tbl role="region" aria-label="The day's changes" tabindex="0"></div>
  <p class="dsp-note">Simulated river flow and illustrative fan set points; the miner rule is the one agreed for BLN (245–250 kW band).</p>
</div>
<div class="dsp-sr" data-live aria-live="polite" aria-atomic="true"></div>`;
  el.appendChild(root);

  const $ = (sel) => root.querySelector(sel);
  const svgA = $('[data-a]'), svgB = $('[data-b]'), plots = $('[data-plots]'), tip = $('[data-tip]');
  const range = $('.dsp-range'), clockEl = $('[data-clock]'), playBtn = $('[data-play]'), speedSel = $('[data-speed]');
  const tblBtn = $('[data-tg]'), more = $('[data-more]'), tbl = $('[data-tbl]'), totEl = $('[data-tot]'), live = $('[data-live]');
  const prevBtn = $('[data-go="-1"]'), nextBtn = $('[data-go="1"]');
  const R = {}, TV = {};
  root.querySelectorAll('[data-r]').forEach((n) => { R[n.dataset.r] = n; });
  tip.querySelectorAll('[data-tv]').forEach((n) => { TV[n.dataset.tv] = n; });
  const scBtns = [...root.querySelectorAll('[data-sc]')];
  let ph = null;   // the playhead's elements, found again after each draw

  /* ------------------------------------------------------- measuring text */
  // Labels are placed where they clear the lines, so their widths are measured, not guessed.
  const ctx = document.createElement('canvas').getContext('2d');
  const font = () => getComputedStyle(root).fontFamily;
  const textW = (s, size = 9.8, weight = 650) => {
    if (!ctx) return s.length * size * 0.6;
    ctx.font = `${weight} ${size}px ${font()}`;
    return ctx.measureText(s).width;
  };

  /* --------------------------------------------------------------- drawing */
  function layout(){
    const W = Math.max(260, width || 560), c = compact;
    const L = 30, Rt = 10, pw = W - L - Rt;
    const hA = c ? 62 : 82, aT = 5, aB = hA - 3;
    const bT = 4, bH = c ? 20 : 28, bB = bT + bH, fT = bB + 5, fH = 8, xT = fT + fH + 12, hB = xT + 3;
    return { W, L, Rt, pw, hA, aT, aB, bT, bB, fT, fH, xT, hB,
      X: (m) => L + (m / MINUTES) * pw,
      YA: (kw) => aB - ((clamp(kw, Y_LO, Y_HI) - Y_LO) / (Y_HI - Y_LO)) * (aB - aT),
      YB: (n) => bB - (n / N_MINERS) * bH };
  }

  // How many minutes of either line fall in the band of kW from lo to hi over minutes m0..m1? A line
  // that steps right across the band between two minutes counts as in it.
  function hits(m0, m1, lo, hi){
    m0 = clamp(Math.floor(m0) - 1, 0, MINUTES - 1); m1 = clamp(Math.ceil(m1) + 1, 0, MINUTES - 1);
    let n = 0;
    for (const s of [sim.avail, sim.exp]) {
      for (let m = m0; m <= m1; m++) {
        const v = s[m], u = m > m0 ? s[m - 1] : v;
        if ((v >= lo && v <= hi) || (u < lo && v > hi) || (u > hi && v < lo)) n++;
      }
    }
    return n;
  }
  const clear = (m0, m1, lo, hi) => !hits(m0, m1, lo, hi);
  const overlaps = (a, b) => a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;

  // A label in a row of chart A: scan along the row from the preferred end for the first place it
  // clears the lines and the labels already placed; if there is none, wherever the fewest minutes of
  // line cross it, on its halo.
  function placeRow(g, text, yTop, prefer, taken){
    const w = textW(text) + 4, h = 10, kpp = (Y_HI - Y_LO) / (g.aB - g.aT);
    const lo = Y_LO + (g.aB - (yTop + h)) * kpp, hi = Y_LO + (g.aB - yTop) * kpp;
    const xs = [];
    for (let x = g.L + 4; x + w <= g.L + g.pw - 2; x += 6) xs.push(x);
    if (prefer === 'right') xs.reverse();
    let best = null;
    for (const x of xs) {
      const box = { x, y: yTop, w, h };
      if (taken.some((b) => overlaps(b, box))) continue;
      const n = hits(((x - g.L) / g.pw) * MINUTES, ((x + w - g.L) / g.pw) * MINUTES, lo, hi);
      if (!best || n < best.n) best = { ...box, n };
      if (!n) break;
    }
    best = best || { x: xs[0] ?? g.L + 4, y: yTop, w, h };
    taken.push(best);
    return best;
  }

  // "Available" sits beside its own line where that line is furthest from export, so it cannot be
  // read as naming export; under a flat stretch at the ceiling, or over a peak.
  function placeAvail(g, taken){
    const text = 'Available', w = textW(text) + 4, h = 10, kpp = (Y_HI - Y_LO) / (g.aB - g.aT);
    let best = null;
    for (let x = g.L + 4; x + w <= g.L + g.pw - 2; x += 6) {
      const m0 = Math.floor(((x - g.L) / g.pw) * MINUTES), m1 = Math.ceil(((x + w - g.L) / g.pw) * MINUTES);
      let mx = -1e9, mn = 1e9, gap = 1e9;
      for (let m = m0; m <= Math.min(m1, MINUTES - 1); m++) {
        const a = sim.avail[m]; mx = Math.max(mx, a); mn = Math.min(mn, a); gap = Math.min(gap, a - sim.exp[m]);
      }
      const mc = Math.min(MINUTES - 1, (m0 + m1) >> 1), gapC = sim.avail[mc] - sim.exp[mc];
      const tries = [];
      if (mx - mn < 2.5 && gap >= 18) tries.push(g.YA(mn) + 4);   // under a flat stretch, well clear of export
      if (gapC >= 18) tries.push(g.YA(mx) - 4 - h);               // over the highest point, where export is far below
      for (const y of tries) {
        if (y < g.aT - 1 || y + h > g.aB) continue;
        const box = { x, y, w, h };
        if (taken.some((b) => overlaps(b, box))) continue;
        const lo = Y_LO + (g.aB - (y + h)) * kpp, hi = Y_LO + (g.aB - y) * kpp;
        if (!clear(m0, m1, lo, hi)) continue;
        const score = gapC - Math.abs(x + w / 2 - (g.L + g.pw / 2)) * 0.02;
        if (!best || score > best.score) best = { ...box, score };
        break;
      }
    }
    if (best) taken.push(best);
    return best;
  }

  function linePath(g, s){
    let d = '';
    for (let m = 0; m < MINUTES; m++) d += (m ? 'L' : 'M') + g.X(m + 0.5).toFixed(1) + ',' + g.YA(s[m]).toFixed(1);
    return d;
  }

  function draw(){
    const g = geo = layout();
    const { L, pw, X, YA, YB } = g, R1 = L + pw;
    const txt = (x, y, s, cls, anchor = 'start') => `<text class="${cls}" x="${x.toFixed(1)}" y="${y.toFixed(1)}" text-anchor="${anchor}">${s}</text>`;

    /* chart A: power */
    let a = '';
    for (const m of X_TICKS) a += `<line class="dsp-vgrid" x1="${X(m).toFixed(1)}" x2="${X(m).toFixed(1)}" y1="${g.aT}" y2="${g.aB}"/>`;
    // 250 needs no gridline: the export limit is drawn there. The unit sits under it, so the limit reads "250 kW".
    for (const v of A_TICKS) {
      if (v !== EXPORT_CAP) a += `<line class="dsp-grid" x1="${L}" x2="${R1}" y1="${YA(v).toFixed(1)}" y2="${YA(v).toFixed(1)}"/>`;
      a += txt(L - 6, YA(v) + 3.3, v, 'dsp-ax', 'end');
    }
    a += txt(L - 6, YA(EXPORT_CAP) + 13, 'kW', 'dsp-ax', 'end');
    a += `<rect class="dsp-band" x="${L}" width="${pw}" y="${YA(EXPORT_CAP).toFixed(1)}" height="${(YA(BAND_LO) - YA(EXPORT_CAP)).toFixed(1)}"/>`;
    a += `<line class="dsp-limit" x1="${L}" x2="${R1}" y1="${YA(EXPORT_CAP).toFixed(1)}" y2="${YA(EXPORT_CAP).toFixed(1)}"/>`;
    a += `<path class="dsp-l-avail" d="${linePath(g, sim.avail)}"/><path class="dsp-l-exp" d="${linePath(g, sim.exp)}"/>`;
    const taken = [];
    // the axis already reads "250 kW" beside the line, so its label is short enough to find a gap
    const lim = placeRow(g, 'Export limit', YA(EXPORT_CAP) - 3 - 10, 'left', taken);
    const band = placeRow(g, 'Miner band 245–250', YA(BAND_LO) + 3, 'right', taken);
    const av = placeAvail(g, taken);
    a += txt(lim.x + 2, lim.y + 8, 'Export limit', 'dsp-lab') + txt(band.x + 2, band.y + 8, 'Miner band 245–250', 'dsp-lab');
    if (av) a += txt(av.x + 2, av.y + 8, 'Available', 'dsp-lab');
    a += `<line class="dsp-xh" data-xh x1="0" x2="0" y1="${g.aT - 2}" y2="${g.aB}" visibility="hidden"/>`;
    a += `<line class="dsp-ph" data-ph x1="0" x2="0" y1="${g.aT - 2}" y2="${g.aB}"/><circle class="dsp-dot-exp" data-pd r="4" cx="0" cy="0"/>`;
    svgA.setAttribute('viewBox', `0 0 ${g.W} ${g.hA}`);
    svgA.setAttribute('height', g.hA);
    svgA.innerHTML = a;

    /* chart B: miners running, and the fans lane under it */
    let b = '';
    for (const m of X_TICKS) b += `<line class="dsp-vgrid" x1="${X(m).toFixed(1)}" x2="${X(m).toFixed(1)}" y1="${g.bT}" y2="${g.bB}"/>`;
    for (const v of [0, 10, 20]) b += `<line class="dsp-grid" x1="${L}" x2="${R1}" y1="${YB(v).toFixed(1)}" y2="${YB(v).toFixed(1)}"/>` + txt(L - 6, YB(v) + 3.3, v, 'dsp-ax', 'end');
    // a step: the count holds through each minute and changes at the minute's start
    let d = `M${X(0).toFixed(1)},${YB(sim.running[0]).toFixed(1)}`;
    for (let m = 1; m < MINUTES; m++) if (sim.running[m] !== sim.running[m - 1]) d += `H${X(m).toFixed(1)}V${YB(sim.running[m]).toFixed(1)}`;
    d += `H${R1.toFixed(1)}`;
    b += `<path class="dsp-a-run" d="${d}V${g.bB}H${L}Z"/><path class="dsp-l-run" d="${d}"/>`;
    // the most that ran, said once: inside the area along the longest stretch at that count, or over its peak
    const mx = sim.totals.maxRunning;
    if (mx > 0) {
      const lab = `${mx} running`, w = textW(lab) + 6;
      let best = [0, 0];
      for (let m = 0, s = -1; m <= MINUTES; m++) {
        const at = m < MINUTES && sim.running[m] === mx;
        if (at && s < 0) s = m;
        if (!at && s >= 0) { if (m - s > best[1] - best[0]) best = [s, m]; s = -1; }
      }
      const x0 = X(best[0]), x1 = X(best[1]);
      if (x1 - x0 >= w + 6 && g.bB - YB(mx) >= 14) b += txt(x0 + 5, YB(mx) + 11, lab, 'dsp-lab');
      else if (YB(mx) - g.bT >= 6) b += txt(clamp((x0 + x1) / 2, L + w / 2, R1 - w / 2), YB(mx) - 4, lab, 'dsp-lab', 'middle');
    } else {
      b += txt(L + pw / 2, g.bB - 6, 'No miners run on this day', 'dsp-lab', 'middle');
    }
    // the fans lane, a step of its own: half height while the lead fan runs alone and full height with
    // both, so the count reads from the shape and not the colour; a hairline holds the lane when both are off
    let fp = '';
    for (let m = 0; m < MINUTES;) {
      const lvl = sim.fan2[m] ? 2 : sim.fan1[m] ? 1 : 0;
      let e = m + 1;
      while (e < MINUTES && (sim.fan2[e] ? 2 : sim.fan1[e] ? 1 : 0) === lvl) e++;
      if (lvl) {
        const y = lvl === 2 ? g.fT : g.fT + g.fH / 2;
        fp += `M${X(m).toFixed(2)},${y}H${Math.max(X(e), X(m) + 0.6).toFixed(2)}V${g.fT + g.fH}H${X(m).toFixed(2)}Z`;
      }
      m = e;
    }
    b += `<line class="dsp-grid" x1="${L}" x2="${R1}" y1="${g.fT + g.fH}" y2="${g.fT + g.fH}"/>`;
    if (fp) b += `<path class="dsp-fan" d="${fp}"/>`;
    b += txt(L - 6, g.fT + g.fH - 0.5, 'Fans', 'dsp-ax', 'end');
    X_TICKS.forEach((m, i) => {
      b += txt(X(m), g.xT, m === MINUTES ? '24:00' : clockOf(m), 'dsp-ax', i === X_TICKS.length - 1 ? 'end' : 'middle');
    });
    b += `<line class="dsp-xh" data-xh x1="0" x2="0" y1="${g.bT - 2}" y2="${g.fT + g.fH}" visibility="hidden"/>`;
    b += `<line class="dsp-ph" data-ph x1="0" x2="0" y1="${g.bT - 2}" y2="${g.fT + g.fH}"/><circle class="dsp-dot-run" data-pd r="4" cx="0" cy="0"/>`;
    svgB.setAttribute('viewBox', `0 0 ${g.W} ${g.hB}`);
    svgB.setAttribute('height', g.hB);
    svgB.innerHTML = b;

    const sc = SCENARIOS.find((s) => s.id === sim.id) || SCENARIOS[0];
    svgA.setAttribute('aria-label', `${sc.label}: export and the power available from the river over the day, kW. Export holds in the 245 to 250 kW band while miners run.`);
    svgB.setAttribute('aria-label', `Miners running over the day, at most ${mx} of ${N_MINERS}, with the lead fan and both fans marked below.`);
    ph = { lines: root.querySelectorAll('[data-ph]'), dots: root.querySelectorAll('[data-pd]'), xh: root.querySelectorAll('[data-xh]') };
    paintHead();
    if (hoverT >= 0) showTip(hoverT);
  }

  /* --------------------------------------------- the day's text: table and totals */
  function fillText(){
    const sc = SCENARIOS.find((s) => s.id === sim.id) || SCENARIOS[0], T = sim.totals;
    scBtns.forEach((b) => b.setAttribute('aria-pressed', b.dataset.sc === sim.id ? 'true' : 'false'));
    totEl.innerHTML = `<b>${sc.label}:</b> ${kwh(T.toMinersKWh)} kWh to the miners, ${kwh(T.exportKWh)} kWh exported. `
      + `Without the cabinet, <b>${kwh(T.spilledWithoutKWh)} kWh</b> of the river’s power would have gone unused; with it, ${kwh(T.spilledKWh)} kWh.`;
    const u = (s) => ` <span class="dsp-u">${s}</span>`;
    const body = changes(sim).map((r, i) => `<tr data-i="${i}"><td><button type="button" class="dsp-tt" data-seek="${r.t}" aria-label="Go to ${clockOf(r.t)}">${clockOf(r.t)}</button></td>`
      + `<td><span class="dsp-chg"><i class="${r.up ? (r.fan ? 'dsp-fup' : 'dsp-up') : 'dsp-dn'}"></i>${r.text}</span></td>`
      + `<td class="dsp-n dsp-rv">${kw1(sim.avail[r.at])}</td><td class="dsp-n">${kw1(sim.exp[r.at])}</td>`
      + `<td class="dsp-n">${sim.running[r.t]}</td><td class="dsp-n">${sim.temp[r.at].toFixed(1)}</td></tr>`).join('');
    tbl.innerHTML = `<table><caption class="dsp-sr">${sc.label}: each change through the day. A miner’s row gives the readings of the minute before, which called for it; a fan’s row gives its own minute’s, when the air temperature switched it. Miners is the count running after the change.</caption>`
      + `<thead><tr><th scope="col">Time</th><th scope="col">Change</th><th scope="col" class="dsp-n dsp-rv">River${u('kW')}</th><th scope="col" class="dsp-n">Export${u('kW')}</th>`
      + `<th scope="col" class="dsp-n">Miners</th><th scope="col" class="dsp-n">Air${u('°C')}</th></tr></thead>`
      + `<tbody>${body || '<tr><td colspan="6">No changes on this day.</td></tr>'}</tbody></table>`;
    curRow = -1;
  }

  /* ------------------------------------------------ the moving parts, per minute */
  function paintHead(){
    if (!geo || !ph) return;
    const x = geo.X(t + 0.5).toFixed(1);
    ph.lines.forEach((l) => { l.setAttribute('x1', x); l.setAttribute('x2', x); });
    ph.dots[0].setAttribute('cx', x); ph.dots[0].setAttribute('cy', geo.YA(sim.exp[t]).toFixed(1));
    ph.dots[1].setAttribute('cx', x); ph.dots[1].setAttribute('cy', geo.YB(sim.running[t]).toFixed(1));
  }

  const canGo = (b, yes) => b.setAttribute('aria-disabled', yes ? 'false' : 'true');

  function paint(){
    const s = stateAt(sim, t);
    paintHead();
    R.exp.textContent = kw1(s.exp);
    R.run.textContent = s.running;
    R.kw.textContent = kw1(s.cabinetKw);
    R.fans.textContent = (compact ? FANS_SHORT : FANS_TEXT)[fanLevel(s)];
    R.temp.textContent = s.temp.toFixed(1);
    clockEl.textContent = s.clock;
    if (+range.value !== t) range.value = t;
    // a focused slider reads its value text out whenever it changes, so it only changes when the day is still
    if (!playing) valueText(s);
    canGo(prevBtn, sim.events.length && sim.events[0].t < t);
    canGo(nextBtn, eventAfter(sim.events, t) < sim.events.length);
    // the table marks the change in force at this minute, and keeps it in view within its own scroll
    const cur = eventAfter(changes(sim), t) - 1;
    if (cur !== curRow) {
      const old = tbl.querySelector('tr.dsp-cur');
      if (old) old.classList.remove('dsp-cur');
      const row = cur >= 0 ? tbl.querySelector(`tr[data-i="${cur}"]`) : null;
      if (row) {
        row.classList.add('dsp-cur');
        if (!more.hidden) {
          const head = tbl.querySelector('thead')?.offsetHeight || 0;
          if (row.offsetTop < tbl.scrollTop + head || row.offsetTop + row.offsetHeight > tbl.scrollTop + tbl.clientHeight)
            tbl.scrollTop = row.offsetTop - head - tbl.clientHeight / 3;
        }
      }
      curRow = cur;
    }
    if (tipPinned) showTip(t);
    return s;
  }

  // the scrubber's spoken value carries what the chart shows at that minute, so none of it needs a hover
  const valueText = (s) => range.setAttribute('aria-valuetext',
    `${s.clock}: river ${kw1(s.avail)} kW, export ${kw1(s.exp)} kW, ${s.running} of ${N_MINERS} miners running, ${FANS_SAY[fanLevel(s)]}`);

  function setPlayBtn(){
    const end = !playing && t >= MINUTES - 1;
    playBtn.innerHTML = (playing ? ICON_PAUSE : end ? ICON_REPLAY : ICON_PLAY) + `<span>${playing ? 'Pause' : end ? 'Replay' : 'Play'}</span>`;
    playBtn.setAttribute('aria-label', playing ? 'Pause the simulated day' : end ? 'Replay the simulated day' : 'Play the simulated day');
  }

  const summary = (s) => `${s.clock}. Export ${kw1(s.exp)} kW, ${s.running} of ${N_MINERS} miners running, ${FANS_SAY[fanLevel(s)]}, hot-air space ${s.temp.toFixed(0)} °C.`;
  function sayLater(prefix = ''){
    clearTimeout(sayTimer);
    sayTimer = setTimeout(() => { if (alive) live.textContent = prefix + summary(stateAt(sim, t)); }, 450);
  }

  // Move to minute m. 'play' fires onState only on a new minute and may read out a change at a slow
  // pace; a seek, a scenario or the mount always fires, and is read out once it settles.
  function goTo(m, why){
    if (!alive) return;
    m = clamp(Math.floor(m), 0, MINUTES - 1);
    const was = t;
    if (m === t && why === 'play') return;
    if (m === t && why === 'drag') return;
    t = m;
    const s = paint();
    if (why === 'play' && speed <= SAY_SPEED && m > was) {
      const rows = changes(sim), r = rows[eventAfter(rows, m) - 1];
      const now = performance.now();
      if (r && r.t > was && now - lastSay > SAY_GAP_MS) { live.textContent = `${clockOf(r.t)}. ${r.say}.`; lastSay = now; }
    } else if (why !== 'play' && why !== 'mount') sayLater();
    if (playing === false || why !== 'play') setPlayBtn();
    if (onState) onState(s);
  }

  /* --------------------------------------------------------------- playback */
  function frame(now){
    if (!alive || !playing) return;
    const dt = Math.min(0.25, Math.max(0, (now - last) / 1000));
    last = now;
    pos += speed * dt;
    if (pos >= MINUTES - 1) {
      pos = MINUTES - 1;
      playing = false; raf = 0;
      goTo(MINUTES - 1, 'play');
      setPlayBtn();
      valueText(stateAt(sim, t));
      sayLater('The day is over. ');
      return;
    }
    goTo(pos, 'play');
    raf = requestAnimationFrame(frame);
  }
  function play(){
    if (playing || !alive) return;
    if (t >= MINUTES - 1) { pos = 0; goTo(0, 'seek'); }
    playing = true; pos = t; last = performance.now();
    clearTimeout(sayTimer);
    setPlayBtn();
    raf = requestAnimationFrame(frame);
  }
  function pause(){
    if (!playing) return;
    playing = false;
    cancelAnimationFrame(raf); raf = 0;
    setPlayBtn();
    valueText(stateAt(sim, t));
    sayLater('Paused. ');
  }
  const toggle = () => (playing ? pause() : play());
  function seek(m, why = 'seek'){
    if (!alive) return;
    m = clamp(Math.floor(+m || 0), 0, MINUTES - 1);
    pos = m;
    goTo(m, why);
  }
  function setScenario(id){
    if (!alive || !known(id)) return;
    sim = simulate(id);
    fillText();
    draw();
    const sc = SCENARIOS.find((s) => s.id === id);
    goTo(t, 'scenario');
    sayLater(sc.label + '. ');
  }
  function setSpeed(v){
    if (!alive) return;
    v = +v;
    if (!(v > 0)) return;
    speed = v;
    if (!SPEEDS.includes(v) || [...speedSel.options].every((o) => +o.value !== v)) speedSel.innerHTML = speedOpts(v);
    speedSel.value = String(v);
  }

  /* ------------------------------------------------------------ hover and touch */
  function minuteAt(clientX){
    const r = svgA.getBoundingClientRect();
    const x = ((clientX - r.left) / (r.width || 1)) * geo.W;
    return clamp(Math.floor(((x - geo.L) / geo.pw) * MINUTES), 0, MINUTES - 1);
  }
  function showTip(m){
    const s = stateAt(sim, m), x = geo.X(m + 0.5), xs = x.toFixed(1), lvl = fanLevel(s);
    ph.xh.forEach((l) => { l.setAttribute('x1', xs); l.setAttribute('x2', xs); l.setAttribute('visibility', 'visible'); });
    TV.exp.textContent = kw1(s.exp) + ' kW';
    TV.avail.textContent = kw1(s.avail) + ' kW';
    TV.run.textContent = `${s.running} of ${N_MINERS}`;
    TV.fans.textContent = FANS_TEXT[lvl];
    TV.fankey.setAttribute('y', lvl === 2 ? 0 : 4);
    TV.fankey.setAttribute('height', lvl === 2 ? 8 : lvl ? 4 : 0);
    TV.temp.textContent = s.temp.toFixed(1) + ' °C';
    tip.querySelector('[data-tt]').textContent = s.clock;
    tip.hidden = false;
    // beside the crosshair, on whichever side has room, in the plots' own pixels
    const scale = plots.clientWidth / geo.W, px = x * scale, w = tip.offsetWidth;
    let left = px + 12;
    if (left + w > plots.clientWidth) left = px - 12 - w;
    const top = svgA.getBoundingClientRect().top - plots.getBoundingClientRect().top;
    tip.style.transform = `translate(${Math.round(clamp(left, 0, Math.max(0, plots.clientWidth - w)))}px, ${Math.round(top + 2)}px)`;
  }
  function hideTip(){
    if (tipPinned) return;
    hoverT = -1;
    tip.hidden = true;
    ph && ph.xh.forEach((l) => l.setAttribute('visibility', 'hidden'));
  }

  plots.addEventListener('pointerdown', (e) => {
    if (e.button !== 0 || !geo) return;
    // a mouse seeks at once; a finger or pen only once it moves sideways, or on a tap, so a page
    // scroll that starts on the chart does not jump the day
    drag = { id: e.pointerId, x: e.clientX, type: e.pointerType, moved: e.pointerType === 'mouse' };
    try { plots.setPointerCapture(e.pointerId); } catch (_) { /* a synthetic pointer cannot be captured */ }
    if (drag.moved) { seek(minuteAt(e.clientX)); hoverT = t; showTip(t); }
  });
  plots.addEventListener('pointermove', (e) => {
    if (!geo) return;
    if (drag && drag.id === e.pointerId) {
      if (!drag.moved && Math.abs(e.clientX - drag.x) > 5) drag.moved = true;
      if (drag.moved) { const m = minuteAt(e.clientX); seek(m, 'drag'); hoverT = m; showTip(m); }
      return;
    }
    if (e.pointerType === 'mouse') { hoverT = minuteAt(e.clientX); showTip(hoverT); }
  });
  const endDrag = (e, tap) => {
    if (!drag || drag.id !== e.pointerId) return;
    if (tap && !drag.moved) seek(minuteAt(e.clientX));
    const touch = drag.type !== 'mouse';
    drag = null;
    if (touch) hideTip();
  };
  plots.addEventListener('pointerup', (e) => endDrag(e, true));
  plots.addEventListener('pointercancel', (e) => endDrag(e, false));
  plots.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse' && !drag) hideTip(); });

  /* --------------------------------------------------------------- controls */
  playBtn.addEventListener('click', toggle);
  speedSel.addEventListener('change', () => setSpeed(speedSel.value));
  scBtns.forEach((b) => b.addEventListener('click', () => { if (b.dataset.sc !== sim.id) setScenario(b.dataset.sc); }));
  range.addEventListener('input', () => seek(range.value, 'drag'));
  range.addEventListener('change', () => sayLater());
  // the keyboard's way to the tooltip: while the scrubber has keyboard focus, the readout rides the playhead
  range.addEventListener('focus', () => { if (range.matches(':focus-visible')) { tipPinned = true; showTip(t); } });
  range.addEventListener('blur', () => { tipPinned = false; hideTip(); });
  // at the first or last change a step does nothing, and says so, but keeps the focus where it is
  prevBtn.addEventListener('click', () => {
    const i = eventAfter(sim.events, t - 1) - 1;
    if (i >= 0) seek(sim.events[i].t);
  });
  nextBtn.addEventListener('click', () => {
    const i = eventAfter(sim.events, t);
    if (i < sim.events.length) seek(sim.events[i].t);
  });
  tblBtn.addEventListener('click', () => {
    const open = more.hidden;
    more.hidden = !open;
    tblBtn.setAttribute('aria-pressed', open ? 'true' : 'false');
    curRow = -1;
    paint();
  });
  tbl.addEventListener('click', (e) => {
    const b = e.target.closest('[data-seek]');
    if (b) seek(+b.dataset.seek);
  });

  /* ------------------------------------------------------------------ sizing */
  function measure(){
    const w = Math.floor(root.clientWidth);
    if (!w || w === width) return;
    width = w;
    const was = compact;
    compact = w < COMPACT_W;
    root.classList.toggle('dsp-compact', compact);
    draw();
    if (was !== compact) paint();   // the fans tile has shorter words when narrow
  }
  let roRaf = 0;
  const ro = typeof ResizeObserver === 'function'
    ? new ResizeObserver(() => { cancelAnimationFrame(roRaf); roRaf = requestAnimationFrame(() => alive && measure()); })
    : null;
  if (ro) ro.observe(root);
  // Inter may still be on its way: the labels were placed by its widths, so place them again once it is here
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { if (alive && geo) draw(); });

  fillText();
  measure();
  if (!geo) draw();
  setPlayBtn();
  goTo(t, 'mount');

  return {
    play, pause, toggle,
    seek: (m) => seek(m),
    setScenario, setSpeed,
    destroy(){
      if (!alive) return;
      alive = false; playing = false; onState = null;
      cancelAnimationFrame(raf); cancelAnimationFrame(roRaf); clearTimeout(sayTimer);
      if (ro) ro.disconnect();
      root.remove();
    },
    get state(){ return stateAt(sim, t); },
    get playing(){ return playing; },
  };
}
