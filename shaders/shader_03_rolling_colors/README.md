# Rolling Colors — 2D

Order → disruption → accumulation → overload → reorganization → order.

A 20 × 11 grid of flat swatches fills a dark stage. A blank ball enters,
favors certain colors, rolls slowly, pauses to consider its next step, and bounces at the edges.
The ball fits within one card and absorbs exactly one card at a time, with a
0.8–1.5 second thinking pause after each pickup. Soft sphere shading and a
subtle rolling surface variation give the ball depth. Each pickup smoothly changes the entire ball to that card’s color while
the missing cards reveal its route. At saturation, every card travels into a
new exact grid slot. The ball becomes blank and the cycle restarts.

Every card retains its identity and pigment. The rebuilt grid matches the next
cycle exactly; a new permutation and new motion tendencies generate variety.
The grid stays flat; only the ball receives spherical lighting. No 3D camera,
perspective, printed-screen finale or texture assets.

## Run

Set `ACTIVE_SCENE = "shader_03_rolling_colors"` in `main.py`, then run
`python main.py` with the project's `.venv` activated. R records; Esc exits.

## Tune

`simulation.py` contains the grid dimensions, palette, ball radius, speed,
color preference, pickup chains and phase durations. `scene.py` exposes overall
playback speed. `shader.frag` controls the crisp, antialiased flat shapes.

Default cycle: 3s ordered grid, 2s entrance, 64s play, 4s overload,
6s reorganization, 3s ordered hold (82s total).

`python -m unittest discover -s tests -v` checks fixed-step consistency,
single-card collection and thinking pauses, clean rebuilding, and cycle continuity.
