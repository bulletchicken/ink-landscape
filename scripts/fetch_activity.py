#!/usr/bin/env python3
"""Fetch one completed year of public GitHub commit contributions.

Only daily aggregates from PUBLIC repositories are written to disk. Issues,
reviews, pull requests and private/internal repository activity are excluded.
Uses the standard library with GITHUB_TOKEN/GH_TOKEN, or an authenticated gh CLI.
"""
import argparse
import calendar
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
QUERY = """
query($user: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $user) {
    contributionsCollection(from: $from, to: $to) {
      totalRepositoriesWithContributedCommits
      commitContributionsByRepository(maxRepositories: 100) {
        repository { visibility }
        contributions(first: 100) {
          totalCount
          pageInfo { hasNextPage }
          nodes { occurredAt commitCount }
        }
      }
    }
  }
}
"""


def graphql(variables):
    payload = json.dumps({"query": QUERY, "variables": variables}).encode()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        request = urllib.request.Request(
            "https://api.github.com/graphql", data=payload,
            headers={"Authorization": f"Bearer {token}",
                     "Content-Type": "application/json", "User-Agent": "commit-landscape"},
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.load(response)
        except urllib.error.HTTPError as error:
            raise RuntimeError(f"GitHub returned HTTP {error.code}; check token access.") from None
    else:
        response = subprocess.run(["gh", "api", "graphql", "--input", "-"],
                                  input=payload, capture_output=True, check=False, timeout=60)
        if response.returncode:
            raise RuntimeError("GitHub request failed. Authenticate gh or provide GITHUB_TOKEN.")
        result = json.loads(response.stdout)
    if result.get("errors"):
        messages = "; ".join(error.get("message", "Unknown GraphQL error") for error in result["errors"])
        raise RuntimeError(f"GitHub query failed: {messages}")
    if not result.get("data", {}).get("user"):
        raise RuntimeError("GitHub user was not found.")
    return result["data"]["user"]["contributionsCollection"]


def month_ranges(start, end):
    current = start
    while current <= end:
        last = current.replace(day=calendar.monthrange(current.year, current.month)[1])
        last = min(last, end)
        yield current, last
        current = last + dt.timedelta(days=1)


def fetch(user, end):
    start = end - dt.timedelta(days=364)
    counts = {str(start + dt.timedelta(days=i)): 0 for i in range(365)}
    for first, last in month_ranges(start, end):
        collection = graphql({"user": user, "from": f"{first}T00:00:00Z", "to": f"{last}T23:59:59Z"})
        repositories = collection["commitContributionsByRepository"]
        if collection["totalRepositoriesWithContributedCommits"] > len(repositories):
            raise RuntimeError(f"Repository limit reached for {first:%Y-%m}; refusing an incomplete snapshot.")
        for repository in repositories:
            if repository["repository"]["visibility"] != "PUBLIC":
                continue
            contributions = repository["contributions"]
            # GitHub's totalCount here counts commits, while nodes group days.
            if contributions["pageInfo"]["hasNextPage"] or contributions["totalCount"] != sum(day["commitCount"] for day in contributions["nodes"]):
                raise RuntimeError("Incomplete daily contribution page; refusing a partial snapshot.")
            for day in contributions["nodes"]:
                date = day["occurredAt"][:10]
                count = day["commitCount"]
                if not str(first) <= date <= str(last) or not isinstance(count, int) or count < 0:
                    raise RuntimeError("GitHub returned an unexpected contribution date or count.")
                counts[date] += count
    return {
        "sample": False,
        "user": user,
        "description": "Public GitHub commit contributions, grouped by UTC date. Excludes private/internal repositories and non-commit activity.",
        "source": {"url": f"https://github.com/{user}", "scope": "public commit contributions", "api": "GitHub GraphQL contributionsCollection"},
        "start": str(start), "end": str(end),
        "days": [{"date": date, "commits": count} for date, count in counts.items()],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "bulletchicken"))
    parser.add_argument("--end", type=dt.date.fromisoformat,
                        default=dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=1),
                        help="Last completed UTC date (YYYY-MM-DD); defaults to yesterday.")
    args = parser.parse_args()
    data = fetch(args.user, args.end)
    destination = ROOT / "data/activity.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n")
    temporary.replace(destination)
    total = sum(day["commits"] for day in data["days"])
    active = sum(day["commits"] > 0 for day in data["days"])
    print(f"{args.user}: {total} public commits across {active} active days ({data['start']} through {data['end']}).")


if __name__ == "__main__":
    main()
