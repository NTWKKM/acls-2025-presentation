# PLAN — Animation/Visualization Upgrade for ACLS 2025 Teaching Deck

**Repo**: `NTWKKM/acls-2025-presentation`
**Target file (only file to edit)**: `slides/acls-2025-teaching.html`
**Base commit**: `e4aedac` ("Restore Group A slide splits to complete slide layout structure")

## Goal
Increase visual/animated teaching aids so learners see mechanisms (rhythm changes,
compression rate/depth, defib energy, pacing capture) rather than reading static text/SVG.
Requested by owner: more JS animation, 3D allowed, priority = **maximize visual clarity for learners**.

## Baseline (verified on actual file, commit e4aedac)
- `<div>` open/close: **900 / 900** ✓
- `<section>` open/close: **65 / 65** ✓
- File: 3457 lines, 222 KB
- CSS `:root` variables (lines 16–41): `--blue` `--blue-light` `--red` `--red-light`
  `--green` `--green-light` `--amber` `--amber-light` (+ glow variants)
- **`--navy` does NOT exist** — use `--blue` everywhere
- JS insertion point: before `/* === INITIALIZE === */` at **line 3361**
- CSS insertion point: after ECG strip block (~line 596)
- Script ends at line 3455; file ends at line 3458
- `SlidePresentation.goToSlide(index)` at **line 3227** — confirmed lifecycle hook (adds/removes `.active`)

## Hard Constraints (do not violate)
1. **Zero-dependency / offline-first** — no external CDN, no npm packages, no fetch calls.
   Everything inline in the single HTML file (matches ARCHITECTURE.md decision #1).
2. **Fixed 1920×1080 design canvas**, scaled via `transform: scale(f)` — do not introduce
   elements that break at non-16:9 aspect or rely on viewport units outside `.deck-stage`.
3. Use existing CSS custom properties for color (`--blue`, `--red`, `--green`/`--green-light`,
   `--amber`, `--blue-light`) — do not hardcode new hex colors. **`--navy` does not exist.**
4. Any "3D" must be CSS `perspective`/`transform-style: preserve-3d` or `<canvas>` 2D context —
   **no WebGL/Three.js** (violates constraint 1 unless vendored inline, which is out of scope).
5. After every edit, re-verify:
   - open/close `<div>` count balanced (baseline 900/900)
   - open/close `<section>` count == 65/65
   - `renderSlideNumbers()` still runs without console errors
   - deck still loads and navigates with keyboard/click in a local static server
6. Do not change slide content/medical text — only add/upgrade visual behavior around
   existing content, unless a task explicitly says to restructure a card.
7. Preserve existing `.reveal` stagger-entrance behavior; new animations layer on top,
   they don't replace slide-transition logic in the `SlidePresentation` class.

## ECG Strip Inventory (verified — do NOT blanket-replace)

| Line | Context | Type | Action |
|------|---------|------|--------|
| 1066 | `bg-ecg-svg` (background decorative) | Decorative | **SKIP** |
| 1223 | Agonal breathing strip (amber) | Respiratory | **SKIP** |
| 1597 | `#ecgSim` Defib simulator (VF) | Cardiac | **Convert → canvas** |
| 1980 | ROSC detection (ETCO₂, green) | Capnography | **SKIP** |
| 2359 | Torsades de Pointes strip | Cardiac | **Convert → canvas** |
| 2488 | TCP slide (no ECG currently) | Cardiac | **Add new canvas** (pacing rhythm) |

## Priority Order (owner-selected: ECG monitor first)

### 1. Live scrolling ECG monitor component (HIGHEST PRIORITY — do this first)
**Problem**: Every ECG on the deck is a static SVG `<path>`. The one interactive element
(`triggerShock()` at line 3369, `resetShockSim()` at line 3399, markup at lines 1593–1604
`#ecgSim` / `#simEcgStrip` / `#ecgPath`) just **swaps** the SVG `d` attribute from a VF-shaped
path to an NSR-shaped path — nothing actually animates/scrolls.

**Fix**: Build one reusable JS component that renders a real scrolling monitor waveform on
`<canvas>`, parameterized by rhythm type, and mount it only on the 3 cardiac strips listed above.

```js
// Insert before "/* === INITIALIZE === */" at line 3361
class ECGMonitor {
  static RHYTHMS = {
    vf:       t => Math.sin(t*0.4)*18 + Math.sin(t*1.1)*9 + (Math.random()-0.5)*14,
    asystole: t => (Math.random()-0.5)*1.5,
    pea:      t => (mod(t,70)<4 ? -25 : mod(t,70)<8 ? 35 : 0) + (Math.random()-0.5)*2,
    nsr:      t => (mod(t,50)<3 ? -35 : mod(t,50)<6 ? 55 : (mod(t,50)>35 && mod(t,50)<42 ? -8 : 0)),
    torsades: t => Math.sin(t*0.3)*20 + Math.sin(t*0.9)*15 + (Math.random()-0.5)*8,
    pacing:   t => (mod(t,45)<2 ? -60 : mod(t,45)<5 ? 45 : 0) // spike + capture beat
  };
  constructor(canvasId, rhythm, colorVar = '--red') {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.t = 0;
    this.rhythm = rhythm;
    this.colorVar = colorVar;
    this.running = false;
    this._resize();
  }
  _resize() {
    const r = this.canvas.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return; // offscreen — skip
    this.canvas.width = r.width * devicePixelRatio;
    this.canvas.height = r.height * devicePixelRatio;
  }
  setRhythm(rhythm, colorVar) { this.rhythm = rhythm; if (colorVar) this.colorVar = colorVar; }
  start() {
    if (this.running) return;
    this.running = true;
    this._resize();
    this._loop();
  }
  stop() { this.running = false; }
  _loop() {
    if (!this.running) return;
    const { ctx, canvas } = this;
    if (!canvas.width) { this._resize(); }
    const gen = ECGMonitor.RHYTHMS[this.rhythm];
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.beginPath();
    const mid = canvas.height / 2;
    const scale = canvas.height / 160;
    for (let x = 0; x < canvas.width; x++) {
      const y = mid - gen(this.t - x) * scale;
      x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue(this.colorVar).trim() || '#C41E3A';
    ctx.lineWidth = 2.5 * devicePixelRatio;
    ctx.stroke();
    this.t++;
    requestAnimationFrame(() => this._loop());
  }
}
function mod(n, m) { return ((n % m) + m) % m; }

class ECGMonitorManager {
  constructor() {
    this.monitors = new Map(); // slide position index → ECGMonitor[]
    this.config = {
      // Key = SlidePresentation.currentSlide position index (NOT data-slide, which has duplicates)
      15: [{ canvasId: 'simEcgCanvas', rhythm: 'vf', colorVar: '--red' }],     // Defib simulator
      35: [{ canvasId: 'torsadesCanvas', rhythm: 'torsades', colorVar: '--red' }], // Torsades
      39: [{ canvasId: 'tcpCanvas', rhythm: 'pacing', colorVar: '--blue' }],   // TCP
    };
  }
  stopAll() {
    this.monitors.forEach(arr => arr.forEach(m => m.stop()));
    this.monitors.clear();
  }
  startForSlide(slideIndex) {
    // Guard: stop existing monitors for this slide before creating new
    if (this.monitors.has(slideIndex)) {
      this.monitors.get(slideIndex).forEach(m => m.stop());
      this.monitors.delete(slideIndex);
    }
    const configs = this.config[slideIndex];
    if (!configs) return;
    // Wait one frame for slide to be visible so getBoundingClientRect works
    requestAnimationFrame(() => {
      const arr = [];
      configs.forEach(c => {
        const m = new ECGMonitor(c.canvasId, c.rhythm, c.colorVar);
        m.start();
        arr.push(m);
      });
      this.monitors.set(slideIndex, arr);
    });
  }
}
const ecgManager = new ECGMonitorManager();
```

**Hook into SlidePresentation.goToSlide()** — at line 3227, modify:
```js
  goToSlide(index) {
    if (index < 0 || index >= this.totalSlides) return;
    ecgManager.stopAll();                                    // ← ADD: stop all monitors
    this.slides[this.currentSlide].classList.remove('active');
    if (index < this.currentSlide) {
      this.slides[this.currentSlide].classList.add('prev');
    } else {
      this.slides[this.currentSlide].classList.remove('prev');
    }
    this.currentSlide = index;
    this.slides.forEach((s, i) => {
      if (i !== this.currentSlide) s.classList.remove('active');
    });
    this.slides[this.currentSlide].classList.remove('prev');
    this.slides[this.currentSlide].classList.add('active');
    this.updateCounter();
    this.updateProgress();
    ecgManager.startForSlide(this.slides[this.currentSlide]); // ← ADD: start monitors for new slide
  }
```

**Integration tasks**:
- Replace the `#ecgSim` SVG (lines 1596–1598) with `<canvas id="simEcgCanvas">`. Keep the
  `.ecg-strip` container, `.ecg-label`, and button markup intact. The ECGMonitorManager
  creates the instance when the slide becomes active — no manual instantiation needed.
- On shock success (`triggerShock()` at line 3369): call `ecgManager.monitors.get(14)?.[0]?.setRhythm('nsr', '--green-light')`
  instead of swapping SVG paths. Keep `flashEffect` keyframe on `.ecg-strip`.
- On reset (`resetShockSim()` at line 3399): call `.setRhythm('vf', '--red')`.
- Replace Torsades SVG (lines 2358–2360) with `<canvas id="torsadesCanvas">`.
- Add `<canvas id="tcpCanvas">` inside the TCP slide `.ecg-strip` (add new `.ecg-strip` block
  after the card-title at line 2492, before the `<ul class="bullets">` at line 2493).
- **Canvas sizing**: `.ecg-strip` is 100% width × 80px height (line 566). Canvas fills it.
  `getBoundingClientRect()` returns screen pixels (post-scale) — correct for `canvas.width/height`.
  But canvas only has valid dimensions when the slide is active. Manager uses `requestAnimationFrame`
  after `.active` is applied to ensure the bounding box is non-zero.

**CSS to add** (after line 596, in the ECG strip section):
```css
.ecg-strip canvas { width: 100%; height: 100%; display: block; }
```

**Acceptance criteria**: opening any slide with an ECG shows a continuously scrolling waveform
matching the labeled rhythm (VF chaotic, Torsades spindle-wave, pacing = spike+capture).
Shock interaction still works (VF→NSR on shock, reset back to VF). No dropped frame rate
warnings in console when 1-2 monitors run concurrently. No monitors running on slides without ECG.

### 2. Defibrillator capacitor charge/discharge animation
On the Defibrillation Energy slide (line 1657, `<section data-slide="16">`) and inside the shock
simulator: before `triggerShock()` fires the flash, animate a charge bar
(`width: 0% → 100%` over ~1.2s, color `--amber` → `--red`) representing capacitor charging to
the selected joules (120J/150J/200J), then trigger discharge (existing `flashEffect`) only
after charge completes. Add a joule selector (120/150/200) if not already present so the charge
duration/label reflects the selection. Disable the "Deliver Shock" button during charging.

### 3. CPR compression rate/depth metronome
On Recognition (slide 5b, line 1213) and High-Quality CPR (slide 7, line 1292) slides: add a
pulsing circle synced to a real 110/min tempo (`animation-duration: ${60000/110}ms` computed
in JS or fixed CSS keyframe at 545ms) labeled "100-120/min", plus a vertical depth bar
oscillating between two marks labeled "5-6 cm" to visually separate rate vs. depth (2025
guideline emphasizes both are independently tracked metrics — see slide's "5 Key Metrics"
card at line 1301).

### 4. Algorithm auto-stepper
On the VF/pVT Algorithm flow slides (flow-box sequences at lines 1255–1272, 1389–1400,
1544–1555) add a "▶ Play" control that sequentially applies a `.step-active` highlight class
(box shadow / border color `--blue`, scale 1.03) to each `.flow-box` in order with ~1.5s
delay between steps, so the sequence CPR→Shock→Epi→Amio is demonstrated rather than read as
a static list. Loop stops at last box; "Reset" clears all highlights.

### 5. (Optional, lowest priority) 3D H's & T's flip upgrade
Existing flip-cards (line 664, `.ht-card`, `rotateY(180deg)`, `perspective: 1000px`,
`transform-style: preserve-3d`) already do a 2-face 3D flip. Only extend this if time remains:
e.g. add a subtle `transform: rotateX(2deg)` idle tilt on hover via `preserve-3d` parent,
purely cosmetic — do not restructure the flip logic itself.

## Verification Checklist (run after each numbered task, not just at the end)
```bash
grep -o '<div' slides/acls-2025-teaching.html | wc -l   # must match close count
grep -o '</div>' slides/acls-2025-teaching.html | wc -l
grep -o '<section' slides/acls-2025-teaching.html | wc -l  # must be 65
grep -o '</section>' slides/acls-2025-teaching.html | wc -l # must be 65
```
Then load the deck in a local static server and manually click through every slide touched
in this plan; confirm no JS console errors and that canvases render at the correct scaled
size inside `.deck-stage` at both full window and a resized (smaller) window.

## Implementation Order
- **Step A**: Task 1 — ECGMonitor + ECGMonitorManager + hook + convert 3 strips
- **Step B**: Verify counts, load, test navigation + monitor rendering
- **Step C**: Task 2 — capacitor charge/discharge + joule selector
- **Step D**: Task 3 — CPR metronome/depth bar
- **Step E**: Task 4 — algorithm stepper
- **Step F**: Task 5 (optional) — flip-card tilt
- **Step G**: Final verification + handoff report

## Handoff Report Format
Follow the existing convention (see prior commit `e4aedac` message / `soul/teacher.md`):
list each numbered task completed, which slide(s)/line ranges it touched, and the final
div/section balance + slide count check results.