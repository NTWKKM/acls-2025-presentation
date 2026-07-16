# Design System for ACLS 2025 Presentation

## Design Tokens

### Colors
- **Primary Navy (`--navy`)**: `#0f1e3d` — Main container background and text color.
- **Deep Navy (`--navy-deep`)**: `#0a1628` — Slide divider backgrounds.
- **Soft Light Background (`--smokewhite`)**: `#f4f4f6` — Landing page and viewport background.
- **Vibrant Blue (`--blue`)**: `#2563eb` — Theme accent color and standard links.
- **Vibrant Red (`--red`)**: `#dc2626` — Critical alerts (Class 3 / Shockable).
- **Emerald Green (`--green`)**: `#16a34a` — Success indicators (ROSC / Class 1).
- **Amber Orange (`--amber`)**: `#d97706` — Warnings and Class 2b recommendations.

### Typography
- **Root Scale**: `html { font-size: 21px; }` — Scales all `rem`-based typography and spacing elements up by ~31.25% to maximize readability on the 1920x1080 canvas.
- **Display Font**: `'Sora'`, sans-serif — Used for bold headers (`3.2rem`), numbers, and hero titles.
- **Thai & Body Font**: `'Noto Sans Thai'`, `'Inter'`, sans-serif — Used for content blocks, bullets (`1.15rem`), and labels.
- **Monospace Font**: `'JetBrains Mono'`, monospace — Used for drug doses, levels of evidence, and status counters.

## UI States
1. **Slide Transition**:
   - Slides transition using a smooth `translateX(0)` to `translateX(-80px)` combined with opacity fade over `0.5s` using `cubic-bezier(0.16, 1, 0.3, 1)` easing.
   - Elements with the `.reveal` class inside the active slide animate from `translateY(30px)` to `translateY(0)` with staggered delays.
2. **Interactive Controls**:
   - Navigation buttons use Glassmorphism borders and transition opacity on hover.
   - Edit mode highlights editable text blocks with a dashed blue outline, turning solid green upon focus.
3. **Interactive & Educational Animations**:
   - **H's and T's Flashcards**: Clicking an H or T card triggers a smooth Y-axis rotation (`transform: rotateY(180deg)`) over `0.6s` to flip the card, revealing the treatment details on the backface.
   - **Defibrillation ECG Simulator**: Clicking the "Deliver Shock" button triggers a visual flash animation (`@keyframes flashEffect`) on the ECG card, converting the fibrillation line (`#ef4444`) to a normal sinus rhythm (`var(--green-light)`) dynamically.
   - **ACLS Drug Quick-Reference overlay**: Floating drug reference panel pops up from the bottom-right corner using a spring-like scaling pop transition (`0.3s cubic-bezier(0.16, 1, 0.3, 1)`) and supports interactive tab switching.

## Accessibility
- High contrast ratios (greater than 4.5:1) for all clinical text against their card backgrounds.
- Standard keyboard fallbacks: Arrow keys and Spacebar for linear progression.
- Responsive scaling: Math.min scale ensures the text is always fully visible within the viewport without cropping.
- Scaled Typography: Large body size (24px equivalent) makes clinical tables and guidelines highly legible from the back of the training room.
