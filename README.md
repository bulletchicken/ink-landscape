# Contribution landscape

The ink landscape at the top of the profile README uses **bulletchicken’s GitHub profile contribution calendar**, the same data source as this repository’s 3D contribution graph. It includes the contributions GitHub records on the profile, such as commits, issues, pull requests, and reviews, along with private contribution counts exposed by the profile’s visibility settings.

Only aggregate daily counts are saved and published. The fetch does not query private repository names, commit messages, or activity details.

## Reading the landscape

- Dates and counts come directly from GitHub’s default profile contribution calendar, including any current-day entries or display-week padding. The calendar supplies the window; no separate start or end date is imposed.
- Contributions are grouped into the calendar months touched by that window, usually 13 bins. The first and last months may be partial; their date labels show the included range.
- Main mountain height grows with the square of monthly contributions, with a small minimum height for nonzero months. Above that floor, 150:100:50 contributions gives heights in the ratio 9:4:1. The tallest month sets the scale for the current window.
- Dates, totals, and small daily calendars travel with their mountains. An active day is a day with at least one counted contribution.
- Distant peaks, connected land, trees, clouds, water, and fish are decorative. Their sizes and quantities do not encode additional activity.

The scene loops every 180 seconds with several layers moving at different speeds. Twenty fish positions take turns, with a jump about every 3 seconds and each flight lasting 1.2 seconds. Their pattern repeats every 60 seconds. The artwork uses native SVG animation; reduced-motion preferences select a still image and disable motion inside the animated SVG as well.

The drawing uses black outlines and pale gray washes on white paper. The background stays white to the outer edges, and the landscape softly fades into it at the sides.

## Refresh

The GitHub workflow refreshes the data and both images nightly at **06:23 UTC**, replacing the former Commit City refresh. It can also be run manually from the repository’s Actions tab.

From the repository root:

```sh
python3 landscape/scripts/fetch_activity.py --user bulletchicken
python3 landscape/scripts/generate.py
```

The scripts use the Python standard library. The nightly workflow reuses its existing `GITHUB_TOKEN`; no personal access token setup is needed. To fetch locally, provide `GITHUB_TOKEN` or authenticate with the GitHub CLI (`gh auth login`). Generation uses the saved activity data and requires no network access.

## Files and attribution

- `assets/nocturne.svg`: animated landscape embedded in the profile README.
- `assets/nocturne-still.svg`: reduced-motion alternative.
- `data/activity.json`: aggregate daily profile contribution counts and the calendar’s date range.
- `scripts/fetch_activity.py`: refreshes the profile contribution calendar.
- `scripts/generate.py`: composes the landscape from that data.
- `scripts/palette.py`: black ink, pale gray washes, and the white paper background.
- `scripts/terrain.py`, `scripts/vegetation.py`, and `scripts/ambient.py`: procedural drawing and motion.

The mountain contour and tapered-brush techniques are adapted from [Lingdong Huang’s {Shan, Shui}*](https://github.com/LingDong-/shan-shui-inf), with a monochrome palette, monthly contribution mapping, attached date labels, connected shoreline, parallax, and ambient details. This renderer adapts those techniques rather than running the full original engine. See [attribution and the MIT license](THIRD_PARTY_NOTICES.md).
