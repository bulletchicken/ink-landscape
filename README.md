# Commit landscape

The ink landscape at the top of the profile README is generated from **bulletchicken’s real public commit contributions**. It counts commits attributed by GitHub, excluding private contributions, issues, pull requests, and reviews. It is not a count of all GitHub activity.

## Reading the landscape

- The window covers 365 days through the previous UTC day, so the current incomplete day is excluded.
- Commits are grouped into the calendar months touched by that window, usually 13 bins. The first and last months may be partial; their date labels show the included range.
- Main mountain height grows with the square of monthly commits, with a small minimum height for nonzero months. Above that floor, 150:100:50 commits gives heights in the ratio 9:4:1. The tallest month sets the scale for the current window.
- Dates, totals, and small daily calendars travel with their mountains. An active day is a day with at least one counted commit.
- Distant peaks, connected land, trees, clouds, water, and fish are decorative. Their sizes and quantities do not encode additional activity.

The scene loops every 180 seconds with several layers moving at different speeds. Four fish take turns jumping about every 7.5 seconds. The artwork uses native SVG animation; reduced-motion preferences select a still image and disable motion inside the animated SVG as well.

## Refresh

The GitHub workflow refreshes the data and both images nightly at **06:23 UTC**, replacing the former Commit City refresh. It can also be run manually from the repository’s Actions tab.

From the repository root:

```sh
python3 landscape/scripts/fetch_activity.py --user bulletchicken
python3 landscape/scripts/generate.py
```

The scripts use the Python standard library. For fetching, provide `GITHUB_TOKEN` or authenticate with the GitHub CLI (`gh auth login`). Generation uses the saved activity data and requires no network access.

## Files and attribution

- `assets/nocturne.svg`: animated landscape embedded in the profile README.
- `assets/nocturne-still.svg`: reduced-motion alternative.
- `data/activity.json`: fetched public commit counts and date range.
- `scripts/fetch_activity.py`: refreshes the public commit data.
- `scripts/generate.py`: composes the landscape from that data.
- `scripts/terrain.py`, `scripts/vegetation.py`, and `scripts/ambient.py`: procedural drawing and motion.

The mountain contour and tapered-brush techniques are adapted from [Lingdong Huang’s {Shan, Shui}*](https://github.com/LingDong-/shan-shui-inf), with a dark palette, monthly commit mapping, attached date labels, connected shoreline, parallax, and ambient details. This renderer adapts those techniques rather than running the full original engine. See [attribution and the MIT license](THIRD_PARTY_NOTICES.md).
