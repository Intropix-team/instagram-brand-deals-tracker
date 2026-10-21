"""Instagram brand deals tracker: find sponsored posts and rank brands.

Runs the PRO Instagram Posts & Reels Scraper on Apify for a list of creator
accounts, keeps the sponsored posts (Instagram's paid partnership label or a
named sponsor brand), and aggregates them per brand: deal count, creators,
total likes, comments, views and shares.

Writes three files to --out:
    deals.csv    one row per sponsored post
    brands.csv   one row per sponsor brand
    report.md    a short markdown report

Usage:
    export APIFY_TOKEN=your_token_here
    python brand_deals_tracker.py creator_one creator_two --since 2026-10-01
    python brand_deals_tracker.py --file creators.txt --posts-per-creator 50
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

ACTOR = "intropix/instagram-posts-reels-scraper-pro"
UNNAMED = "(unnamed sponsor)"

DEAL_FIELDS = [
    "brand", "creator", "permalink", "post_type", "taken_at",
    "sponsor_usernames", "coauthors", "tagged_usernames", "like_count",
    "comment_count", "view_count", "share_count", "engagement_rate",
    "caption",
]
BRAND_FIELDS = [
    "brand", "deals", "creators", "creator_count", "total_likes",
    "total_comments", "total_views", "total_shares", "first_deal",
    "last_deal", "brand_followers",
]
METRICS = {
    "like_count": "total_likes",
    "comment_count": "total_comments",
    "view_count": "total_views",
    "share_count": "total_shares",
}


# ---------------------------------------------------------------- pure logic


def is_sponsored(post: dict) -> bool:
    """A brand deal: the paid partnership label, or a sponsor brand named."""
    return bool(post.get("is_paid_partnership") or post.get("sponsor_usernames"))


def deal_brands(post: dict) -> list[str]:
    """The brands a sponsored post counts towards.

    Instagram names the brand on the paid partnership label in
    `sponsor_usernames`. A post with the label but no named sponsor is
    grouped under UNNAMED rather than dropped.
    """
    sponsors = [s for s in (post.get("sponsor_usernames") or []) if s]
    return list(dict.fromkeys(sponsors)) or [UNNAMED]


def deal_rows(posts: list[dict]) -> list[dict]:
    """One row per (sponsored post, brand), deduplicated on post_pk."""
    rows = []
    seen: set = set()
    for post in posts:
        if not is_sponsored(post):
            continue
        key = post.get("post_pk") or post.get("permalink")
        if key in seen:
            continue
        seen.add(key)
        for brand in deal_brands(post):
            row = {field: post.get(field) for field in DEAL_FIELDS}
            row["brand"] = brand
            row["creator"] = post.get("username")
            rows.append(row)
    return rows


def _add(total: int | None, value) -> int | None:
    """Null-safe sum: hidden counts (null) are skipped, not read as zero."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return (total or 0) + value
    return total


def aggregate(posts: list[dict]) -> list[dict]:
    """Per-brand summary, most deals first."""
    brands: dict[str, dict] = {}
    followers: dict[str, int] = {}
    for post in posts:
        for partner in post.get("partners") or []:
            if partner.get("username") and partner.get("follower_count") is not None:
                followers[partner["username"]] = partner["follower_count"]

    for row in deal_rows(posts):
        b = brands.setdefault(
            row["brand"],
            {"brand": row["brand"], "deals": 0, "creators": set(),
             "first_deal": None, "last_deal": None,
             **{total: None for total in METRICS.values()}},
        )
        b["deals"] += 1
        if row["creator"]:
            b["creators"].add(row["creator"])
        for field, total in METRICS.items():
            b[total] = _add(b[total], row.get(field))
        day = (row.get("taken_at") or "")[:10] or None
        if day:
            b["first_deal"] = min(filter(None, [b["first_deal"], day]))
            b["last_deal"] = max(filter(None, [b["last_deal"], day]))

    summary = []
    for b in brands.values():
        creators = sorted(b["creators"])
        summary.append({
            **b,
            "creators": " ".join(creators),
            "creator_count": len(creators),
            "brand_followers": followers.get(b["brand"]),
        })
    summary.sort(key=lambda s: (-s["deals"], -(s["total_views"] or 0), s["brand"]))
    return summary


def _fmt(value) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def sponsored_post_count(posts: list[dict]) -> int:
    """Distinct sponsored posts (a post with two sponsors counts once)."""
    return len({p.get("post_pk") or p.get("permalink") for p in posts if is_sponsored(p)})


def render_report(summary: list[dict], posts: list[dict], creators: list[str]) -> str:
    deals = sponsored_post_count(posts)
    posts_read = len(posts)
    lines = [
        "# Instagram brand deals report",
        "",
        f"Creators scanned: {len(creators)}. Posts read: {posts_read}. "
        f"Sponsored posts: {deals}. Brands: {len(summary)}.",
        "",
        "Totals skip hidden counts, so n/a means no post had that number.",
        "",
        "| Brand | Deals | Creators | Likes | Comments | Views | Shares | First | Last |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for s in summary:
        lines.append(
            f"| {s['brand']} | {s['deals']} | {s['creators'] or 'n/a'} | "
            f"{_fmt(s['total_likes'])} | {_fmt(s['total_comments'])} | "
            f"{_fmt(s['total_views'])} | {_fmt(s['total_shares'])} | "
            f"{_fmt(s['first_deal'])} | {_fmt(s['last_deal'])} |"
        )
    if not summary:
        lines.append("| no sponsored posts found | | | | | | | | |")
    return "\n".join(lines) + "\n"


def defuse(value):
    """Neutralise spreadsheet formula injection in CSV cells.

    Captions and usernames are written by whoever posted; a cell starting
    with = + - @ would run as a formula in Excel or Sheets.
    """
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value


def write_csv(rows: list[dict], fields: list[str], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            flat = {
                k: " ".join(v) if isinstance(v, list) else v for k, v in row.items()
            }
            writer.writerow({k: defuse(v) for k, v in flat.items()})


def write_outputs(posts: list[dict], creators: list[str], out_dir: Path) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = aggregate(posts)
    write_csv(deal_rows(posts), DEAL_FIELDS, out_dir / "deals.csv")
    write_csv(summary, BRAND_FIELDS, out_dir / "brands.csv")
    (out_dir / "report.md").write_text(
        render_report(summary, posts, creators), encoding="utf-8"
    )
    return summary


# ---------------------------------------------------------------- I/O


def fetch_posts(
    creators: list[str],
    posts_per_creator: int,
    since: str | None,
    until: str | None,
    enrich: bool,
) -> list[dict]:
    """One run per creator: maxPosts is one total per run, filled account by
    account in input order, so a shared run would give the first creator
    the whole budget."""
    from apify_client import ApifyClient

    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("APIFY_TOKEN is not set. Export it before running.")
    client = ApifyClient(token)
    posts: list[dict] = []
    for creator in creators:
        run_input: dict = {
            "usernames": [creator],
            "maxPosts": posts_per_creator,
            "enrichPartners": enrich,
        }
        if since:
            run_input["sinceDate"] = since
        if until:
            run_input["untilDate"] = until
        run = client.actor(ACTOR).call(run_input=run_input)
        if run is None or run["status"] != "SUCCEEDED":
            print(f"@{creator}: run did not succeed", file=sys.stderr)
            continue
        output = client.key_value_store(run["defaultKeyValueStoreId"]).get_record("OUTPUT")
        value = (output or {}).get("value") or {}
        if value.get("outcome") == "denied":
            print(f"run refused ({value.get('reason')}): {value.get('message')}", file=sys.stderr)
            break
        for name, why in (value.get("failed_target_reasons") or {}).items():
            print(f"skipped @{name}: {why.get('reason')}", file=sys.stderr)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        print(f"@{creator}: {len(items)} posts", file=sys.stderr)
        posts.extend(items)
    return posts


def read_creators(args: argparse.Namespace) -> list[str]:
    names = list(args.creators)
    if args.file:
        for line in Path(args.file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                names.append(line)
    return list(dict.fromkeys(n.lstrip("@") for n in names))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Track Instagram brand deals per brand.")
    parser.add_argument("creators", nargs="*", help="creator usernames")
    parser.add_argument("--file", help="text file with one username per line")
    parser.add_argument("--posts-per-creator", type=int, default=30,
                        help="posts read per creator, newest first (default 30)")
    parser.add_argument("--since", help="only posts on or after YYYY-MM-DD (UTC)")
    parser.add_argument("--until", help="only posts on or before YYYY-MM-DD (UTC)")
    parser.add_argument("--enrich", action="store_true",
                        help="add follower counts of sponsor brands ($0.005 per profile, paid Apify plans)")
    parser.add_argument("--out", default="brand_deals", help="output folder")
    args = parser.parse_args(argv)
    creators = read_creators(args)
    if not creators:
        parser.error("give at least one creator username or --file")

    posts = fetch_posts(creators, args.posts_per_creator, args.since, args.until, args.enrich)
    summary = write_outputs(posts, creators, Path(args.out))
    deals = sponsored_post_count(posts)
    print(f"{len(posts)} posts read, {deals} sponsored, {len(summary)} brands. "
          f"See {args.out}/report.md")


if __name__ == "__main__":
    main()
