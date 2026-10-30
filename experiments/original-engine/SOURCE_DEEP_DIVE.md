# How Lingdong's landscape is actually drawn

This second version is built around the original drawing engine from [Lingdong Huang's `{Shan, Shui}*`](https://github.com/LingDong-/shan-shui-inf), rather than a new renderer imitating its appearance. The reference is pinned to commit [`9f754d2b2e73495db7883d4d4055a7b0903b0454`](https://github.com/LingDong-/shan-shui-inf/tree/9f754d2b2e73495db7883d4d4055a7b0903b0454). Its unmodified HTML and MIT license are in `vendor/`; `vendor/source.json` records the commit and source checksum.

The original is one HTML file containing a small procedural drawing system. Its graphics are strings of SVG polylines and filled outlines. Mountains, trees, buildings, people, boats, and water all use the same brush primitives, which is why they look like parts of one painting.

## Source map

Line numbers below refer to the pinned `vendor/index.html`.

| Part | Original code | What it contributes |
| --- | --- | --- |
| Repeatable variation | [`Prng`, line 2](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L2), [`Noise`, line 90](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L90) | Seeded randomness and layered Perlin noise. |
| Brushwork | [`stroke`, line 516](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L516), [`blob`, line 578](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L578), [`texture`, line 653](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L653) | Tapered, noisy ink marks, leaf shapes, and rock hatching. |
| Vegetation | [`Tree`, line 743](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L743) | Eight tree routines, including clustered leaves, bent trunks, bark, recursive branches, and twigs. |
| Terrain | [`Mount.mountain`, line 1804](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L1804), [`flatMount`, line 2083](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L2083), [`distMount`, line 2369](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L2369), [`rock`, line 2433](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L2433) | Layered mountain faces, flat islands, pale distant ridges, and foreground rocks. |
| Buildings and boats | [`Arch.arch01`, line 3002](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L3002), [`Arch.boat01`, line 3209](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L3209) | Pavilions, roofed buildings, pagodas, rails, and boats with ferrymen. |
| People | [`Man`, line 3324](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L3324), [`Man.man`, line 3522](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L3522) | Posed skeletons clothed with curved ink outlines, plus hats and carried objects. |
| Water and composition | [`water`, line 3667](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L3667), [`mountplanner`, line 3706](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L3706), [`chunkloader`, line 3845](https://github.com/LingDong-/shan-shui-inf/blob/9f754d2b2e73495db7883d4d4055a7b0903b0454/index.html#L3845) | Water strokes, spacing of land and boats, depth order, and continued generation as the view moves. |

## The brush is geometry

`stroke` takes a centerline, computes its local direction, and offsets vertices on both sides. The width varies along the line—by default following a sine taper—and Perlin noise perturbs it. It closes the resulting shape into a filled outline. This produces a brush mark with a changing width rather than an ordinary constant-width SVG line.

`blob` builds an elongated closed shape, perturbs its perimeter with noise, and rotates it. Trees use these small forms as leaves. `texture` works between successive terrain contours: it samples short paths, displaces them with noise, and feeds them back through `stroke`. The mountain's internal marks therefore follow its surface instead of being a generic texture pasted over the silhouette.

## A mountain is a whole little scene

`Mount.mountain(x, y, seed, {hei, wid, tex, veg})` builds ten shrinking contours with fifty samples each. The basic cosine profile is multiplied by Perlin noise. It then paints rim vegetation, an opaque white mountain body, the outer brush contour, foothills, surface texture, and more vegetation. The routine can also generate buildings, a summit pagoda, transmission towers, and rocks.

That distinction matters for the commit mapping: in the original function, `hei` controls the mountain's height envelope, but noise also affects the visible summit. Version 2 now measures the generated terrain contour and scales the complete mountain to an explicit target rise. The original noise still determines the shape, while the final terrain height follows the commit mapping. Decorative trees and pagodas may extend above the measured terrain summit.

`flatMount` makes a low terrain surface and calls `flatDec` to populate it with rocks, different families of trees, and sometimes a pavilion. `distMount` triangulates its shapes into pale grey facets. Keeping these different forms and plenty of water between them is a large part of the original look.

## The people are constructed, not icons

`Man.man` creates nine joints using a parent-child skeleton, limb lengths, and joint angles. It calculates joint positions, then uses curved paths and varying-width envelopes to form sleeves, the body, and the head. White filled clothing hides geometry behind the figure; grey brush outlines define its edges. Hats are transformed into place using the neck-to-head direction. A carried item receives the two hand positions.

`Arch.boat01` already calls `Man.man` with the original pole, wide hat, and a boat-specific set of limb lengths. Reusing that function brings along the ferryman's actual drawing logic. `Arch.arch01` similarly composes a hut roof, platform, and rear/front rails, with zero, one, or two people painted between the rails. Those internal paint orders should be preserved.

## How the original infinite scroll works

`mountplanner` samples noise to choose mountain locations, tracks occupied land, puts flat terrain into gaps, and keeps boats spaced apart. `chunkloader` grows the scene in 512-unit chunks and inserts objects by their vertical coordinate so nearer objects paint over farther ones. Mountain water strokes are deliberately assigned a very low depth value so they paint behind the land.

`chunkrender` includes objects near the current view. Moving the SVG `viewBox` exposes more generated content. This original browser mechanism generates new geography as the user travels; it is different from a finite, repeating SVG image.

For a README, the second version reuses the original drawing functions but supplies a commit-driven layout and a finite, repeating panorama. The seamless animation and mist at the viewport edges are additions. They do not claim to be Lingdong's original scroll implementation. The same recorded activity returns on every lap.

## Fidelity and integration details

- **Keep the original opaque fills.** Mountains, rocks, buildings, boats, and clothing use white to cover earlier objects. Removing those fills makes the painting look like transparent wireframes. The original outer SVG uses `mix-blend-mode:multiply` over a warm paper background; that is how white occlusion shapes can coexist with tinted paper.
- **Keep the grey ink and its alpha values.** Original low-opacity strokes, dense overlapping texture, and pale distant land produce depth. A global dark green recoloring would move the result away from this reference.
- **Seed both sources of variation deliberately.** The original PRNG overrides `Math.random`; Perlin noise also keeps a cached table. Changing the PRNG seed alone does not reset an already constructed noise table. Use short numeric seeds derived from the activity data and control the noise seed too.
- **Preserve the engine's execution environment.** Some original helpers assign undeclared working variables. A non-strict, isolated JavaScript context can execute the original bodies without silently rewriting them.
- **Treat `veg:false` carefully.** It skips the middle and bottom vegetation branches, not every tree or building emitted by `mountain`.
- **Scale boats externally when enlarging them.** In `boat01`, setting `sca` above one can let the hull's sine-based square-root expression receive a negative value. Keeping its original internal scale and scaling the resulting SVG group avoids that artifact.
- **Record commit mappings separately.** Scene placements, amplitude parameters, chosen seeds, and explicitly added figures should be recorded in the scene manifest. The original functions also generate decorative details internally; those incidental trees or people should not be described as exact commit counters.

The original code is preserved under its MIT license. The separate adapter, commit mapping, README framing, and loop wrapper are the new work in this version; the first design remains separate.

## What Version 2 actually executes

The adapter in `scripts/engine.cjs` extracts the original `PRNG`, `PerlinNoise`, `PolyTools`, and `Util` script blocks, then executes the original drawing block up to `mountplanner` in an isolated JavaScript context. It does not rewrite the drawing functions. The browser UI and original infinite chunk loader are omitted because this deliverable is a self-contained README image.

The scene generator calls these original routines directly:

- `Mount.mountain`: 13 principal mountains for the current sample, one per nonzero calendar-month bin. The original function runs at local `(0, 0)` with reference `hei=500`. Its contour is measured using `ret:1` with the same stable seed; the complete original mountain is then uniformly scaled to the target rise. Input width compensates for that scale. Texture count remains `85 + 4 × active days`.
- `Tree.tree01`, `Tree.tree03`, and `Tree.tree07`: explicitly planted groves with `ceil(active days / 7)` trees per month. The original mountains and islands may add other trees internally.
- `Mount.distMount`, `Mount.flatMount`, and `Mount.rock`: distant ridges, decorated islands, shore rocks, and footing for the travellers.
- `Arch.boat01`: 13 ferries, each with its original built-in ferryman, hat, and pole.
- `Arch.arch01`: five explicitly placed pavilions; its original logic may place additional people inside.
- `Arch.arch03`: foreground pagodas. Original mountain decoration may add further architecture.
- `Man.man`, `Man.hat02`, and `Man.stick01`: five explicitly placed robed travellers on the shore.
- `water`: the original tapered water strokes around the banks and boats.

The terrain mapping deliberately exaggerates activity differences:

- For nonzero months, visible terrain rise is `max(6, 350 × (commits / peak-month commits)²)` above a common baseline at y=385.
- Zero-commit months have no mountain.
- Above the six-unit minimum, 150:100:50 commits give terrain-height ratios of **9:4:1**: 150 is 2.25× as tall as 100 and 9× as tall as 50.
- Nominal final width is `130 + 330 × (commits / peak-month commits)^1.1`.
- Height refers to the terrain contour, not the bounding box of trees, buildings, or other decoration. The distant decorative hills are kept low and faint so they do not overwhelm the monthly mountain.

The normalization uses the original returned geometry rather than replacing the original mountain algorithm. Scaling the whole generated mountain keeps its texture, trees, and incidental buildings proportionate. Separately placed travellers and ferries retain their original scene scale.

The same 1,417 sample commits and 269 active days from Version 1 are retained. They occupy 13 calendar-month bins because the first and last October are partial months. Seeds are stable hashes of month and feature identity; commit totals affect rendering parameters rather than reseeding every figure.

The 5,200-unit panorama is wrapped feature by feature before clipping, preserving the original paint order where objects cross the seam. The wrapper repeats those vectors with native CSS translation over 180 seconds. A fixed opacity mask softens the edges. Header text stays still. Each month’s date range and commit total are anchored to that mountain’s recorded horizontal center and share the painting’s animated translation, so labels follow their mountains throughout the loop. The paper grain and README frame are new presentation elements; the landscape geometry comes from the original engine.

`data/scene-manifest.json` records the feature inventory and every explicit parameter set. The generated scene was checked for repeatability, invalid geometry, retained commit totals, and clipped mountain summits. The vendored source checksum matches the pinned upstream file.
