# Architecture of ACLS 2025 Presentation Workspace

## Components
1. **Landing Hub (`index.html`)**: The entry portal for the ACLS 2025 educational system. It provides links to the teaching deck and interactive case scenarios, presenting high-level statistics and course structure.
2. **Teaching Presentation Deck (`slides/acls-2025-teaching.html`)**: A zero-dependency, animation-rich slide deck built with HTML, CSS custom properties, and inline JavaScript. Scales uniformly to fit any browser window at a fixed 16:9 ratio.
3. **Interactive Case Scenarios (`cases/acls-2025-cases.html`)**: An interactive application that lets physicians practice ACLS decision-making through 10 clinical scenarios (VF, Asystole, PEA, etc.), providing immediate feedback and detailed rationales.

## Data Flow
1. **User Interaction -> Navigation**: Responding to keyboard events (Arrows, Spacebar, Page Up/Down), touch gestures, or mouse wheel, the Presentation Controller updates the active slide index.
2. **Dynamic Scaling -> Canvas**: The Presentation Controller monitors window resize events, recalculating the uniform scale factor based on a 1920x1080 design canvas, and applies a CSS `transform: translate(x, y) scale(f)` to the stage element.
3. **Slide State -> Animation**: When a slide becomes active, the `.visible` or `.active` class is applied, triggering staggered CSS transitions (`opacity` and `translate`) on elements with the `.reveal` class.

## Decisions
1. **Zero-Dependency Static HTML**: Chosen to enable offline-first usage for ER physicians in clinical environments. All styles and scripts are embedded to ensure instant load times and zero network requirements.
2. **Fixed-Stage scaling (16:9)**: Authoring slides at a static 1920x1080 canvas size and scaling the stage container prevents content reflow bugs, ensuring typography and clinical diagrams retain exact proportions on all screen sizes.
3. **Upper-Screen and Lower-Screen Separation**: Keeping slide indicators and controls within the scaled stage container ensures they scale and move with the slide contents, avoiding collisions and overlap issues seen with viewport-fixed positioning.
