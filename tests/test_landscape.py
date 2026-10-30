"""Public rendering and aggregate-data contracts, using synthetic activity only."""
import copy
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import fetch_activity
import generate


SVG = "{http://www.w3.org/2000/svg}"
MONTHS = {"2026-01": 50, "2026-02": 100, "2026-03": 150}
BACKGROUNDS = {"white": "#ffffff", "green": "#101919", "black": "#0e1116"}
INK = {"white": "#111111", "green": "#dbe4ce", "black": "#e3e3e3"}


def synthetic_activity():
    start, end = dt.date(2026, 1, 1), dt.date(2026, 3, 31)
    days = []
    for offset in range((end - start).days + 1):
        date = start + dt.timedelta(days=offset)
        count = MONTHS[str(date)[:7]] if date.day == 15 else 0
        days.append({"date": str(date), "contributions": count})
    return {"sample": True, "metric": "contributions", "user": "example-user",
            "start": str(start), "end": str(end), "days": days}


def paint_colors(root):
    return {value.lower() for node in root.iter()
            for name, value in node.attrib.items()
            if name in {"fill", "stroke", "stop-color"} and value.startswith("#")}


class LandscapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = synthetic_activity()
        # Deliberately reuse the process, including a return to the first theme.
        cls.renders = [generate.render(cls.data, theme)
                       for theme in ("white", "green", "black", "white")]

    def test_sequential_themes_do_not_leak_colors(self):
        for theme, (root, _) in zip(("white", "green", "black", "white"), self.renders):
            with self.subTest(theme=theme):
                self.assertEqual(root.find(SVG + "rect").get("fill"), BACKGROUNDS[theme])
                colors = paint_colors(root)
                self.assertIn(INK[theme], colors)
                for other, color in INK.items():
                    if other != theme:
                        self.assertNotIn(color, colors, f"{other} ink leaked into {theme}")
                month_names = [node for node in root.iter(SVG + "text")
                               if node.text in {"January 2026", "February 2026", "March 2026"}]
                self.assertEqual({node.get("fill") for node in month_names}, {INK[theme]})
        self.assertEqual(ET.tostring(self.renders[0][0]), ET.tostring(self.renders[3][0]))

    def test_monthly_data_and_quadratic_scale_are_identical_across_themes(self):
        expected = self.renders[0][1]
        self.assertEqual({item["month"]: item["contributions"] for item in expected}, MONTHS)
        heights = {item["contributions"]: item["height"] for item in expected}
        self.assertAlmostEqual(heights[100] / heights[50], 4)
        self.assertAlmostEqual(heights[150] / heights[50], 9)
        for _, records in self.renders[1:]:
            self.assertEqual(records, expected)

    def test_clean_labels_and_daily_calendars_travel_with_their_months(self):
        root = self.renders[0][0]
        text = [node.text for node in root.iter(SVG + "text")]
        self.assertCountEqual(text, ["January 2026", "February 2026", "March 2026",
                                     "50", "100", "150", *(["CONTRIBUTIONS"] * 3)])
        tile = next(node for node in root.iter() if node.get("id") == "history-tile")
        mountains = {node.get("data-month"): node for node in root.iter()
                     if node.get("data-month") is not None}
        labels = [node for node in tile.iter() if node.get("data-label-month") is not None]
        self.assertEqual(len(labels), len(MONTHS))
        for label in labels:
            month = label.get("data-label-month")
            mountain = mountains[month]
            self.assertEqual(int(label.get("data-contributions")), MONTHS[month])
            self.assertEqual(label.get("data-contributions"), mountain.get("data-contributions"))
            self.assertEqual(label.get("data-center"), mountain.get("data-center"))
            self.assertEqual(label.get("transform"), f"translate({mountain.get('data-center')} 0)")
            attached = [node for node in tile.iter(SVG + "use")
                        if node.get("href") == "#" + mountain.get("id")
                        and node.get("x") == label.get("data-center")]
            self.assertTrue(attached, f"{month} label and mountain have different anchors")
        daily = [{"date": node.get("data-date"), "contributions": int(node.get("data-contributions"))}
                 for node in tile.iter(SVG + "rect") if node.get("data-date") is not None]
        self.assertEqual(daily, self.data["days"])

    def test_cli_all_writes_six_self_contained_native_svgs(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            input_path = directory / "synthetic.json"
            output_path = directory / "rendered"
            input_path.write_text(json.dumps(self.data))
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/generate.py"), "--theme", "all",
                 "--input", str(input_path), "--output-dir", str(output_path)],
                check=True, capture_output=True, text=True, timeout=60,
            )
            expected = {f"landscape-{theme}{suffix}.svg"
                        for theme in BACKGROUNDS for suffix in ("", "-still")}
            self.assertEqual({path.name for path in output_path.iterdir()}, expected)
            self.assertEqual(set(json.loads(result.stdout)["assets"]), expected)
            for name in expected:
                with self.subTest(asset=name):
                    root = ET.parse(output_path / name).getroot()
                    theme = name.split("-")[1].removesuffix(".svg")
                    self.assertEqual(root.tag, SVG + "svg")
                    self.assertEqual(root.find(SVG + "rect").get("fill"), BACKGROUNDS[theme])
                    self.assertEqual(root.get("role"), "img")
                    self.assertIsNotNone(root.find(SVG + "desc"))
                    for node in root.iter():
                        self.assertNotIn(node.tag, {SVG + "script", SVG + "foreignObject", SVG + "image"})
                        for attribute in ("href", "{http://www.w3.org/1999/xlink}href"):
                            if attribute in node.attrib:
                                self.assertTrue(node.get(attribute).startswith("#"))
                    css = root.find(SVG + "style").text
                    self.assertRegex(css, r"prefers-reduced-motion\s*:\s*reduce")
                    if "-still" in name:
                        self.assertRegex(css, r"\*\s*\{\s*animation\s*:\s*none\s*!important")


class FetchActivityTests(unittest.TestCase):
    @staticmethod
    def response(days=None, total=6):
        if days is None:
            days = [{"date": "2026-01-01", "contributionCount": 2},
                    {"date": "2026-01-02", "contributionCount": 0},
                    {"date": "2026-01-03", "contributionCount": 4}]
        return {"contributionCalendar": {"totalContributions": total,
                                         "weeks": [{"contributionDays": days}]}}

    def test_valid_calendar_publishes_only_daily_aggregates(self):
        response = self.response()
        # Unexpected extra fields must not reach the saved/public snapshot.
        response["privateRepository"] = "synthetic-private-detail-do-not-publish"
        response["contributionCalendar"]["weeks"][0]["contributionDays"][0]["message"] = response["privateRepository"]
        with patch.object(fetch_activity, "graphql", return_value=response) as query:
            result = fetch_activity.fetch("example-user")
        query.assert_called_once_with({"user": "example-user"})
        self.assertFalse(result["sample"])
        self.assertEqual(result["metric"], "contributions")
        self.assertEqual(result["user"], "example-user")
        self.assertEqual((result["start"], result["end"]), ("2026-01-01", "2026-01-03"))
        self.assertEqual(result["days"], [{"date": "2026-01-01", "contributions": 2},
                                          {"date": "2026-01-02", "contributions": 0},
                                          {"date": "2026-01-03", "contributions": 4}])
        self.assertEqual(result["source"]["calendar_total"], 6)
        self.assertEqual(set(result), {"sample", "user", "metric", "description", "source", "start", "end", "days"})
        self.assertEqual(set(result["source"]), {"url", "scope", "api", "calendar_total"})
        self.assertNotIn(response["privateRepository"], json.dumps(result))

    def test_query_does_not_request_private_repository_or_commit_details(self):
        fields = set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", fetch_activity.QUERY))
        self.assertTrue({"contributionCalendar", "totalContributions", "contributionDays"} <= fields)
        self.assertFalse(fields & {"repository", "repositories", "commitContributionsByRepository",
                                   "commit", "commits", "message", "email", "nameWithOwner"})

    def test_invalid_snapshots_are_rejected(self):
        good_days = self.response()["contributionCalendar"]["weeks"][0]["contributionDays"]
        cases = {
            "mismatched total": (good_days, 7),
            "gap": ([good_days[0], good_days[2]], 6),
            # Match the deduplicated sum so a silently discarded duplicate
            # cannot fail only because of the separate total validation.
            "duplicate": (good_days + [good_days[0]], 6),
            "empty": ([], 0),
            "boolean total": ([{"date": "2026-01-01", "contributionCount": 1}], True),
        }
        for name, count in [("negative count", -1), ("boolean count", True), ("floating-point count", 2.0)]:
            days = copy.deepcopy(good_days)
            days[0]["contributionCount"] = count
            # Keep the total valid to exercise the daily-count rejection.
            cases[name] = (days, int(sum(day["contributionCount"] for day in days)))
        for name, (days, total) in cases.items():
            with self.subTest(case=name):
                with patch.object(fetch_activity, "graphql", return_value=self.response(days, total)):
                    with self.assertRaises((RuntimeError, ValueError)):
                        fetch_activity.fetch("example-user")


if __name__ == "__main__":
    unittest.main()
