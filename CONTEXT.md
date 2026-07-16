# Context and Glossary for ACLS 2025 Presentation

## Glossary
- **ROSC**: Return of Spontaneous Circulation. The resumption of sustained perfusing cardiac activity.
- **PEA**: Pulseless Electrical Activity. A clinical condition characterized by organized cardiac electrical activity on an ECG without a palpable pulse.
- **VF / pVT**: Ventricular Fibrillation and pulseless Ventricular Tachycardia. The two shockable cardiac arrest rhythms.
- **LUD**: Left Lateral Uterine Displacement. A manual maneuver to push the uterus to the left to relieve aortocaval compression in a pregnant patient.
- **Resuscitative Hysterotomy**: Formerly "perimortem cesarean delivery". An emergency cesarean section performed during maternal cardiac arrest to aid in maternal resuscitation.
- **DSD / VC**: Double Sequential Defibrillation and Vector Change. Emerging electrical therapies for shock-refractory ventricular fibrillation.
- **TTM**: Targeted Temperature Management. Active temperature control (32°C - 37.5°C) to prevent secondary brain injury after ROSC.
- **TOR**: Termination of Resuscitation. Guidelines for when to stop CPR in out-of-hospital cardiac arrest.

## Architectural Decision Records (ADR)
### ADR 1: Dynamic Slide Numbering
- **Context**: Adding slides manually changes the total count and index numbers, leading to tedious manual HTML editing and potential errors in headers/footers.
- **Decision**: Slide numbers on the top right are now rendered dynamically at startup by selecting all `.slide` elements and injecting the current index and total count.
- **Implications**: The HTML source code can use placeholder numbers; the script handles correctness dynamically.

### ADR 2: Integration of Controls inside the Scaled Stage
- **Context**: Fixed-position controls outside the scaled 1920x1080 stage collide with the slide contents when the browser window is small.
- **Decision**: Move the control bar and progress bar inside the `.deck-stage` wrapper so that they scale down in proportion to the content on smaller screens.
- **Implications**: Controls remain at the bottom-center of the slides, keeping layout proportions identical.
