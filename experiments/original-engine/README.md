# Original drawing engine experiment

This edition executes Lingdong Huang's original mountain, tree, rock, water, people, pavilion, pagoda, and boat drawing functions. The arrangement and sliding README presentation use **fictional 1,417 commits across 269 active days**, from October 26, 2025 through October 24, 2026. It repeats that fixed sample and has no live GitHub connection.

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="assets/lingdong-commit-scroll-still.svg">
  <img src="assets/lingdong-commit-scroll.svg" width="1200" alt="Archived Chinese ink landscape with people, ferries, pavilions, and monthly mountains generated from fictional commit data using Lingdong Huang's original drawing functions.">
</picture>

## Regenerate

From this folder, using Node.js, Python 3, and their standard libraries:

```sh
node scripts/generate-scene.cjs
python3 scripts/build-scroll.py
```

From the repository root:

```sh
node experiments/original-engine/scripts/generate-scene.cjs
python3 experiments/original-engine/scripts/build-scroll.py
```

The first command creates the intermediate `assets/scene.svg` and updates `data/scene-manifest.json`. The second creates the [animated SVG](assets/lingdong-commit-scroll.svg) and [still SVG](assets/lingdong-commit-scroll-still.svg). The reproducible intermediate is omitted from the archive.

The monthly terrain height uses a squared mapping, with exact height measured from the original contour; decorative treetops and buildings can extend higher. Dates and totals move with their mountains. The 180-second animation repeats the same panorama using native SVG/CSS, and respects reduced-motion preferences. Its historical header, date ranges, and warm paper presentation are retained.

## Source and attribution

The unmodified source in `vendor/index.html` comes from [{Shan, Shui}*](https://github.com/LingDong-/shan-shui-inf), pinned to commit [`9f754d2b2e73495db7883d4d4055a7b0903b0454`](https://github.com/LingDong-/shan-shui-inf/tree/9f754d2b2e73495db7883d4d4055a7b0903b0454). The source checksum is recorded in `vendor/source.json`; its MIT license is preserved in `vendor/LICENSE`.

The adapter executes the original drawing routines in an isolated Node.js context. It supplies a finite, repeating composition rather than the original browser's infinite chunk loader. Human figures and incidental architecture are decorative, not contributor or release counts.

[Code deep dive](SOURCE_DEEP_DIVE.md) · [Attribution and MIT notice](THIRD_PARTY_NOTICES.md)
