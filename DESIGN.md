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
- **Display Font**: `'Sora'`, sans-serif — Used for bold headers, numbers, and hero titles.
- **Thai & Body Font**: `'Noto Sans Thai'`, `'Inter'`, sans-serif — Used for content blocks, bullets, and labels.
- **Monospace Font**: `'JetBrains Mono'`, monospace — Used for drug doses, levels of evidence, and status counters.

## UI States
1. **Slide Transition**:
   - Slides transition using a smooth `translateX(0)` to `translateX(-60px)` combined with opacity fade over `0.5s` using `cubic-bezier(0.16, 1, 0.3, 1)` easing.
   - Elements with the `.reveal` class inside the active slide animate from `translateY(30px)` to `translateY(0)` with staggered delays.
2. **Interactive Controls**:
   - Navigation buttons use Glassmorphism borders and transition opacity on hover.
   - Edit mode highlights editable text blocks with a dashed blue outline, turning solid green upon focus.

## Accessibility
- High contrast ratios (greater than 4.5:1) for all clinical text against their card backgrounds.
- Standard keyboard fallbacks: Arrow keys and Spacebar for linear progression.
- Responsive scaling: Math.min scale ensures the text is always fully visible within the viewport without cropping.
