"""Offline tests: no network, no Apify token."""

import csv
import socket
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import brand_deals_tracker as tracker  # noqa: E402
from samples import ALL, REDBULL_REEL, SPONSORED_REEL  # noqa: E402


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def refuse(*args, **kwargs):
        raise RuntimeError("network access in an offline test")

    monkeypatch.setattr(socket, "socket", refuse)
    monkeypatch.delenv("APIFY_TOKEN", raising=False)


def test_unsponsored_readme_item_is_not_a_deal():
    assert tracker.aggregate([REDBULL_REEL]) == []


def test_aggregate_groups_per_brand_with_null_safe_totals():
    by_brand = {s["brand"]: s for s in tracker.aggregate(ALL)}

    assert set(by_brand) == {"rolex", tracker.UNNAMED}
    rolex = by_brand["rolex"]
    assert (rolex["deals"], rolex["creators"], rolex["total_likes"], rolex["total_views"]) == (
        1, "redbull", 46317, 1588744,
    )
    unnamed = by_brand[tracker.UNNAMED]
    # likes, views and shares hidden: unknown, not zero
    assert (unnamed["deals"], unnamed["total_likes"], unnamed["total_views"],
            unnamed["total_comments"]) == (1, None, None, 344)


def test_same_post_twice_counts_once():
    summary = tracker.aggregate([SPONSORED_REEL, SPONSORED_REEL])
    assert [(s["brand"], s["deals"]) for s in summary] == [("rolex", 1)]


def test_write_outputs_files(tmp_path):
    tracker.write_outputs(ALL, ["redbull"], tmp_path)

    with (tmp_path / "deals.csv").open(encoding="utf-8") as f:
        deals = list(csv.DictReader(f))
    with (tmp_path / "brands.csv").open(encoding="utf-8") as f:
        brands = list(csv.DictReader(f))
    report = (tmp_path / "report.md").read_text(encoding="utf-8")

    assert sorted(d["brand"] for d in deals) == sorted(["rolex", tracker.UNNAMED])
    assert {d["coauthors"] for d in deals if d["brand"] == "rolex"} == {"example_photographer imax"}
    assert {b["brand"] for b in brands} == {"rolex", tracker.UNNAMED}
    assert "Posts read: 3. Sponsored posts: 2. Brands: 2." in report
    assert "| rolex | 1 | redbull | 46,317 |" in report
