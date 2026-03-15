"""Algorithm Intelligence — Platform-specific optimization rules.

Each platform's algorithm has specific signals it rewards.
This module encodes those signals so content can be optimized BEFORE publishing.

Sources: Official platform docs, creator program guidelines, 
         algorithm analysis papers, and community testing data.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Platform(Enum):
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REELS = "instagram_reels"
    TWITTER_VIDEO = "twitter_video"


@dataclass
class AlgorithmProfile:
    """What a specific platform's algorithm rewards."""
    platform: Platform
    
    # Completion / Watch Time
    completion_rate_target: float = 0.0  # Target % who watch to end
    avg_watch_time_target: float = 0.0  # Target average % watched
    
    # Engagement Signals (weighted by importance)
    like_weight: float = 1.0
    comment_weight: float = 1.0
    share_weight: float = 1.0
    save_weight: float = 1.0
    follow_weight: float = 1.0
    rewatch_weight: float = 1.0
    
    # Timing
    hook_window_seconds: float = 3.0  # How long to grab attention
    ideal_duration_seconds: tuple = (15, 60)  # Sweet spot range
    max_duration_seconds: int = 180
    
    # Discovery
    hashtag_count: tuple = (3, 8)
    hashtags_in_caption: bool = True
    keywords_in_caption: bool = True
    trending_audio_boost: float = 1.0  # Multiplier for using trending sounds
    
    # Penalty Triggers
    watermarks_from_other_platforms: float = -0.5  # Penalty
    low_quality_first_frame: float = -0.3
    too_long: float = -0.2
    no_hook: float = -0.4
    
    # Content Patterns That Work
    proven_formats: list = field(default_factory=list)
    hook_templates: list = field(default_factory=list)


# ==================== PLATFORM PROFILES ====================

TIKTOK = AlgorithmProfile(
    platform=Platform.TIKTOK,
    completion_rate_target=0.80,
    avg_watch_time_target=0.75,
    like_weight=1.0,
    comment_weight=3.0,      # Comments weighted heavily
    share_weight=4.0,        # Shares are king
    save_weight=2.5,
    follow_weight=2.0,
    rewatch_weight=3.5,      # Rewatches signal high value
    hook_window_seconds=0.5,  # Brutal attention economy
    ideal_duration_seconds=(21, 34),
    max_duration_seconds=180,
    hashtag_count=(3, 5),
    hashtags_in_caption=True,
    trending_audio_boost=2.0,
    proven_formats=[
        "POV: [scenario]",
        "Things that just make sense",
        "Nobody talks about [topic] but...",
        "Wait for it",
        "Story time (part 1)",
        "Rating [things] in [category]",
        "Day in my life as [persona]",
        "Unpopular opinion: [take]",
        "Things I wish I knew about [topic]",
        "Replying to @[comment]",
        "This or that",
        "Get ready with me + info",
        "Green screen + commentary",
        "Duet/stitch with reaction",
    ],
    hook_templates=[
        "Nobody is talking about this but...",
        "This changed everything for me",
        "Stop doing [common thing] wrong",
        "I tested this so you don't have to",
        "The [topic] industry isn't ready for this",
        "Here's what [authority] doesn't want you to know",
        "3 things about [topic] that will blow your mind",
        "I spent [time] doing [thing] — here's what happened",
        "POV: you just discovered [thing]",
        "This is your sign to [action]",
        "If you [do thing], watch this",
        "The algorithm doesn't want you to see this",
    ],
)

YOUTUBE_SHORTS = AlgorithmProfile(
    platform=Platform.YOUTUBE_SHORTS,
    completion_rate_target=0.85,
    avg_watch_time_target=0.80,
    like_weight=1.0,
    comment_weight=2.0,
    share_weight=2.5,
    save_weight=1.5,
    follow_weight=3.0,       # Subscribers valued highly
    rewatch_weight=3.0,
    hook_window_seconds=1.0,
    ideal_duration_seconds=(25, 45),
    max_duration_seconds=60,
    hashtag_count=(3, 5),
    keywords_in_caption=True,
    proven_formats=[
        "How to [achieve outcome] in [time]",
        "[Number] [things] you didn't know about [topic]",
        "The truth about [controversial topic]",
        "[Tool/hack] that [authority figures] don't want you to know",
        "Reacting to [viral thing]",
        "I tried [trending thing] for [time period]",
        "[Topic] explained in 60 seconds",
        "Before and after [transformation]",
        "Testing viral [life hacks / products / tips]",
    ],
    hook_templates=[
        "You're never going to believe this",
        "This is the [best/worst] [thing] I've ever [seen/done]",
        "In the next 60 seconds, I'll change how you think about [topic]",
        "Watch until the end for [payoff]",
        "99% of people don't know this",
        "The real reason [surprising thing] happens",
    ],
)

INSTAGRAM_REELS = AlgorithmProfile(
    platform=Platform.INSTAGRAM_REELS,
    completion_rate_target=0.75,
    avg_watch_time_target=0.70,
    like_weight=1.0,
    comment_weight=2.0,
    share_weight=2.0,
    save_weight=4.0,         # Saves are Instagram's king metric
    follow_weight=2.5,
    rewatch_weight=2.0,
    hook_window_seconds=1.0,
    ideal_duration_seconds=(15, 30),
    max_duration_seconds=90,
    hashtag_count=(5, 10),
    hashtags_in_caption=False,  # Better in first comment
    trending_audio_boost=1.8,
    proven_formats=[
        "Carousel-style video (slides)",
        "Before/after transformation",
        "Aesthetic day in my life",
        "Tutorial with satisfying visuals",
        "Infographic animation",
        "Text overlay story",
        "Trend + niche twist",
        "Myth vs reality",
        "Ranking [things]",
    ],
    hook_templates=[
        "Save this for later",
        "You need to know this about [topic]",
        "The only [topic] guide you'll ever need",
        "POV: [relatable scenario]",
        "This is your reminder to [motivational thing]",
        "Things that changed my life at [age/stage]",
    ],
)


PROFILES = {
    Platform.TIKTOK: TIKTOK,
    Platform.YOUTUBE_SHORTS: YOUTUBE_SHORTS,
    Platform.INSTAGRAM_REELS: INSTAGRAM_REELS,
}


def get_profile(platform: Platform) -> AlgorithmProfile:
    """Get the algorithm profile for a platform."""
    return PROFILES[platform]


def score_content(content: dict, platform: Platform) -> dict:
    """
    Score content against a platform's algorithm.
    
    Returns a dict with:
    - overall_score: 0-100
    - breakdown: scores per signal
    - suggestions: how to improve
    """
    profile = get_profile(platform)
    scores = {}
    suggestions = []
    
    # Hook check
    hook = content.get("hook", "")
    if not hook:
        scores["hook"] = 0.0
        suggestions.append(f"⚠️ Missing hook — you have {profile.hook_window_seconds}s to grab attention")
    elif len(hook.split()) > 15:
        scores["hook"] = 0.5
        suggestions.append("⚠️ Hook is too long — make it punchier (under 10 words ideal)")
    else:
        scores["hook"] = 1.0
    
    # Duration check
    duration = content.get("duration_seconds", 0)
    ideal_min, ideal_max = profile.ideal_duration_seconds
    if duration == 0:
        scores["duration"] = 0.5
    elif ideal_min <= duration <= ideal_max:
        scores["duration"] = 1.0
    elif duration > profile.max_duration_seconds:
        scores["duration"] = 0.0
        suggestions.append(f"❌ Too long ({duration}s) — max is {profile.max_duration_seconds}s for {platform.value}")
    else:
        scores["duration"] = 0.7
    
    # Engagement potential
    has_question = "?" in content.get("caption", "")
    has_cta = any(w in content.get("caption", "").lower() for w in ["comment", "tell me", "what do you", "agree?", "thoughts"])
    if has_question or has_cta:
        scores["engagement_bait"] = 1.0
    else:
        scores["engagement_bait"] = 0.3
        suggestions.append("💡 Add a question or CTA to drive comments")
    
    # Hashtag check
    tags = content.get("hashtags", [])
    tag_min, tag_max = profile.hashtag_count
    if tag_min <= len(tags) <= tag_max:
        scores["hashtags"] = 1.0
    elif len(tags) < tag_min:
        scores["hashtags"] = 0.5
        suggestions.append(f"💡 Add more hashtags (currently {len(tags)}, ideal {tag_min}-{tag_max})")
    else:
        scores["hashtags"] = 0.7
        suggestions.append(f"💡 Too many hashtags ({len(tags)}), trim to {tag_max} max")
    
    # Format check
    fmt = content.get("format", "")
    if fmt in profile.proven_formats:
        scores["format"] = 1.0
    elif fmt:
        scores["format"] = 0.6
    else:
        scores["format"] = 0.3
        suggestions.append("💡 No format specified — pick a proven format for better reach")
    
    # Calculate overall
    weights = {"hook": 3.0, "duration": 2.0, "engagement_bait": 2.0, "hashtags": 1.0, "format": 1.5}
    total_weight = sum(weights.values())
    overall = sum(scores.get(k, 0.5) * v for k, v in weights.items()) / total_weight * 100
    
    return {
        "platform": platform.value,
        "overall_score": round(overall, 1),
        "breakdown": {k: round(v * 100, 1) for k, v in scores.items()},
        "suggestions": suggestions,
        "grade": "A" if overall >= 80 else "B" if overall >= 60 else "C" if overall >= 40 else "D",
    }


def get_best_posting_times(platform: Platform, timezone: str = "US/Pacific") -> dict:
    """
    Return optimal posting times for a platform.
    
    Based on aggregate engagement data across US audiences.
    """
    times = {
        Platform.TIKTOK: {
            "weekdays": ["7:00 AM", "12:00 PM", "7:00 PM", "10:00 PM"],
            "weekends": ["9:00 AM", "12:00 PM", "7:00 PM"],
            "best_day": "Tuesday",
            "peak_hours": [19, 20, 21],  # 7-9 PM
        },
        Platform.YOUTUBE_SHORTS: {
            "weekdays": ["3:00 PM", "7:00 PM", "9:00 PM"],
            "weekends": ["9:00 AM", "12:00 PM", "5:00 PM"],
            "best_day": "Thursday",
            "peak_hours": [15, 16, 17],  # 3-5 PM (after school/work)
        },
        Platform.INSTAGRAM_REELS: {
            "weekdays": ["7:00 AM", "12:00 PM", "5:00 PM", "7:00 PM"],
            "weekends": ["10:00 AM", "1:00 PM", "5:00 PM"],
            "best_day": "Wednesday",
            "peak_hours": [11, 12, 17, 18],  # Lunch + after work
        },
    }
    return times.get(platform, times[Platform.TIKTOK])
