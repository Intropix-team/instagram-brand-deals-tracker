# Instagram Brand Deals Tracker: find sponsored posts and paid partnerships

Instagram brand deals tracker for influencer marketing research. Give it a list of creator accounts and it finds their sponsored posts (Instagram's paid partnership label and the sponsor brand it names), then ranks the brands behind them: how many deals, with which creators, and how many likes, comments, views and shares those posts got. Output is CSV plus a short markdown report. No Instagram login, no cookies and no Instagram account of your own.

## What you get

- `deals.csv`: one row per sponsored post, with the sponsor brand, creator, link, date, co-authors, tagged accounts, likes, comments, views, shares, engagement rate and caption.
- `brands.csv`: one row per sponsor brand, with deal count, creators, totals, first and last deal date, and the brand's follower count when `--enrich` is on.
- `report.md`: the brand table in markdown, ready to paste into a doc or a pull request.

A post counts as a brand deal when it carries Instagram's paid partnership label or names a sponsor brand. A post with the label but no named sponsor is grouped under `(unnamed sponsor)` rather than dropped. Hidden counts (an owner can hide likes, photos have no view count) are skipped in totals, never read as zero; a total no post had shows as `n/a`.

## Install

Python 3.10 or newer.

```bash
git clone https://github.com/Intropix-team/instagram-brand-deals-tracker.git
cd instagram-brand-deals-tracker
pip install -r requirements.txt
export APIFY_TOKEN=your_token_here
```

Get the token from a free account at [apify.com](https://apify.com): Console > Settings > API & Integrations.

## Usage

```bash
# last 30 posts of each creator
python brand_deals_tracker.py creator_one creator_two

# everything since 1 October, up to 100 posts per creator
python brand_deals_tracker.py --file creators.txt --since 2026-10-01 --posts-per-creator 100

# add follower counts of sponsor brands and co-authors (paid Apify plans)
python brand_deals_tracker.py --file creators.txt --since 2026-10-01 --enrich --out october
```

| Option | Meaning |
| --- | --- |
| `creators` / `--file` | Creator usernames, on the command line or one per line in a file |
| `--posts-per-creator` | Posts read per creator, newest first (default 30) |
| `--since`, `--until` | Date bounds, `YYYY-MM-DD`, UTC |
| `--enrich` | Profile summary of every sponsor brand and co-author ($0.005 per profile) |
| `--out` | Output folder (default `brand_deals`) |

The tracker starts one scraper run per creator. The scraper's `maxPosts` is one total per run, filled account by account in input order, so a single shared run would give the first creator the whole budget.

## Example output

Example output, generated offline from sample items (see [`example_output/`](example_output/)). `report.md`:

| Brand | Deals | Creators | Likes | Comments | Views | Shares | First | Last |
|---|---|---|---|---|---|---|---|---|
| rolex | 1 | redbull | 46,317 | 344 | 1,588,744 | 3,450 | 2026-10-17 | 2026-10-17 |
| (unnamed sponsor) | 1 | redbull | n/a | 344 | n/a | n/a | 2026-10-12 | 2026-10-12 |

## Cost

The PRO scraper is pay per event on Apify: $0.005 per run start, $0.002 per profile scanned and $0.0039 per post delivered ($3.90 per 1,000). Every post read is billed, sponsored or not, so date bounds are the main cost lever. Example: 20 creators, 30 posts each, is 20 x (0.005 + 0.002 + 30 x 0.0039) = about $2.48. `--enrich` adds $0.005 per distinct sponsor or co-author profile per run; because each creator is its own run, a brand that sponsors five of your creators is enriched (and billed) five times. Failed lookups are never charged. Apify free-plan accounts can test with up to 10 results per run and 40 per day; enrichment needs a paid plan.

## Legal and terms

- Use it on public business, creator and brand accounts. Do not target personal accounts of private individuals, and do not use usernames found in the data (co-authors, tagged accounts) to build profiles of individuals.
- You are responsible for a lawful basis for any processing of personal data (for example under GDPR) and for deleting data you no longer need.
- The scraper's own Terms of Use on its Store page apply.
- This is an independent tool. It is not affiliated with, endorsed by, or connected to Instagram or Meta Platforms, Inc.

## Tests

```bash
pip install pytest
pytest tests
```

The tests run offline on the sample item from the scraper's README plus two derived sponsored posts; they make no network calls and need no token.

## Built on

- [PRO Instagram Posts & Reels Scraper](https://apify.com/intropix/instagram-posts-reels-scraper-pro) on the Apify Store (actor id `intropix~instagram-posts-reels-scraper-pro`), which returns `is_paid_partnership`, `sponsor_usernames`, `coauthors`, `tagged_usernames`, share counts and partner profiles in every post.
- If likes, comments, views, dates and the paid partnership flag are all you need, the standard [Instagram Posts & Reels Scraper](https://apify.com/intropix/instagram-posts-reels-scraper) returns those at $1.90 per 1,000 posts. This tracker uses the PRO actor because it ranks by `sponsor_usernames` and partner profiles, which only PRO returns.
- More examples: [instagram-scraper-examples](https://github.com/Intropix-team/instagram-scraper-examples).

## License

MIT, see [LICENSE](LICENSE). Support: team.intropix@gmail.com.
