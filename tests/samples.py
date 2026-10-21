"""Sample items for offline tests and the README example output.

REDBULL_REEL is the real example item from the PRO Instagram Posts & Reels
Scraper README (Red Bull, 17-10-2026), copied verbatim. The other two are
DERIVED from it for testing: the sponsor and partners block is the brand
deal snippet from the same README, and the post ids are made up.
"""

REDBULL_REEL = {
    "username": "redbull",
    "user_pk": "476322",
    "full_name": "Red Bull",
    "is_verified": True,
    "is_private": False,
    "follower_count": 34172188,
    "following_count": 2147,
    "profile_pic_url": "https://scontent-lax3-1.cdninstagram.com/v/t51.2885-19/...",
    "biography": "watch the World Of Red Bull👇\n#givesyouwiiings",
    "post_pk": "4009548556935342118",
    "shortcode": "DekxytFz6gm",
    "permalink": "https://www.instagram.com/p/DekxytFz6gm/",
    "post_type": "reel",
    "taken_at": "2026-10-17T00:08:53Z",
    "caption": "Race winner with the team @example_rider ...",
    "like_count": 46317,
    "comment_count": 344,
    "view_count": 1588744,
    "is_paid_partnership": False,
    "is_off_grid": False,
    "coauthors": ["example_rider", "redbullbike"],
    "hashtags": ["mtb", "downhill", "givesyouwiiings", "mountainbike"],
    "mentions": ["example_rider"],
    "media": [
        {
            "slide_index": 0,
            "media_type": "video",
            "media_url": "https://scontent-ord5-2.cdninstagram.com/o1/v/t2/f2/m86/...",
            "cover_url": "https://scontent-ord5-1.cdninstagram.com/v/t51.82787-15/...",
            "width": 1080,
            "height": 1920,
            "video_duration": 220.3329925537,
        }
    ],
    "share_count": 3450,
    "repost_count": 937,
    "fb_play_count": None,
    "fb_like_count": None,
    "engagement_rate": 0.001365,
    "audio_title": "Original audio",
    "audio_artist": "redbull",
    "audio_id": "26590578263972833",
    "is_original_audio": True,
    "sponsor_usernames": [],
    "tagged_usernames": ["redbullbike", "example_rider"],
    "partners": [],
    "is_pinned": False,
    "caption_edited": False,
    "has_audio": True,
    "counts_hidden": False,
    "location_name": "Cypress Mountain",
    "location_id": "415790",
    "location_city": None,
    "location_lat": 49.39541,
    "location_lng": -123.20219,
    "owner_category": None,
    "owner_account_type": "business",
    "owner_website": "https://onein.bio/redbull",
    "owner_bio_links": [
        "https://onein.bio/redbull",
        "https://www.redbull.com/int-en/cartoons/booked-for-uni",
        "http://www.redbullwingscup.com",
    ],
    "owner_post_count": 11660,
    "owner_public_email": "info@redbull.com",
    "owner_public_phone": None,
    "owner_city": None,
    "owner_address": None,
}

# DERIVED: a paid partnership post naming a sponsor, with partner enrichment.
SPONSORED_REEL = {
    **REDBULL_REEL,
    "post_pk": "1000000000000000001",
    "permalink": "https://www.instagram.com/p/EXAMPLE1/",
    "is_paid_partnership": True,
    "sponsor_usernames": ["rolex"],
    "coauthors": ["example_photographer", "imax"],
    "partners": [
        {"username": "example_photographer", "full_name": "Chai Vasarhelyi", "follower_count": 63358,
         "is_verified": True, "category": "Film Director", "account_type": "creator"},
        {"username": "imax", "full_name": "IMAX", "follower_count": 1676536,
         "is_verified": True, "category": None, "account_type": "business"},
    ],
}

# DERIVED: the paid partnership label without a named sponsor, a photo
# (no view count) whose owner hid the like count.
UNNAMED_PHOTO = {
    **REDBULL_REEL,
    "post_pk": "1000000000000000002",
    "permalink": "https://www.instagram.com/p/EXAMPLE2/",
    "post_type": "image",
    "taken_at": "2026-10-12T09:00:00Z",
    "is_paid_partnership": True,
    "sponsor_usernames": [],
    "like_count": None,
    "view_count": None,
    "share_count": None,
    "counts_hidden": True,
}

ALL = [REDBULL_REEL, SPONSORED_REEL, UNNAMED_PHOTO]
