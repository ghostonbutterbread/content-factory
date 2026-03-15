"""Content Generator — AI-powered content creation optimized for algorithms.

Takes trending topics and generates platform-optimized content:
- Hooks (first 3 seconds)
- Scripts (full content outline)
- Captions (with hashtags)
- Engagement bait (questions, CTAs)
"""

import json
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from core.algorithm_profiles import (
    Platform, get_profile, score_content, get_best_posting_times
)

logger = logging.getLogger(__name__)


@dataclass
class ContentPiece:
    """A complete piece of content ready for a platform."""
    title: str
    hook: str
    script: str
    caption: str
    hashtags: list[str]
    format: str
    platform: str
    duration_seconds: int
    engagement_score: float = 0.0
    algorithm_grade: str = ""
    suggestions: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "hook": self.hook,
            "script": self.script,
            "caption": self.caption,
            "hashtags": self.hashtags,
            "format": self.format,
            "platform": self.platform,
            "duration_seconds": self.duration_seconds,
            "engagement_score": self.engagement_score,
            "algorithm_grade": self.algorithm_grade,
            "suggestions": self.suggestions,
            "metadata": self.metadata,
        }


class HookGenerator:
    """Generate attention-grabbing hooks optimized for platform algorithms."""
    
    # Hook formulas that consistently perform well
    FORMULAS = {
        "curiosity_gap": [
            "Nobody is talking about {topic} but...",
            "The {topic} industry doesn't want you to know this",
            "Here's what happens when you {action}",
            "I discovered something about {topic} that changes everything",
            "The real reason {topic} is trending right now",
        ],
        "contrarian": [
            "Everyone's wrong about {topic} — here's why",
            "Stop doing {action} — try this instead",
            "Unpopular opinion: {controversial_take}",
            "What if I told you {surprising_fact}?",
            "{authority_figure} was wrong about {topic}",
        ],
        "urgency": [
            "This {topic} hack is going viral for a reason",
            "You need to see this before {deadline}",
            "If you {do_thing}, watch this NOW",
            "This is your sign to {action}",
            "Save this before it gets taken down",
        ],
        "social_proof": [
            "I tested {topic} for {time} — here's what happened",
            "{number} million people watched this — now it's your turn",
            "Scientists just discovered {discovery}",
            "{percentage}% of people don't know this about {topic}",
            "I asked {number} experts about {topic} — here's what they said",
        ],
        "direct_value": [
            "{number} {topic} hacks that actually work",
            "How to {achieve_goal} in {timeframe}",
            "The only {topic} guide you'll ever need",
            "Free tool that replaces {expensive_thing}",
            "Step-by-step: {desired_outcome}",
        ],
        "story": [
            "POV: {relatable_scenario}",
            "Story time: How I {achievement}",
            "Day {number} of {challenge} — update",
            "I spent {time} doing {thing} — never again",
            "The moment I realized {insight}",
        ],
    }
    
    def generate(self, topic: str, platform: Platform, style: str = "auto") -> str:
        """Generate a hook for a topic on a specific platform."""
        profile = get_profile(platform)
        
        if style == "auto":
            # Pick style based on platform preference
            if platform == Platform.TIKTOK:
                style = random.choice(["curiosity_gap", "contrarian", "story"])
            elif platform == Platform.YOUTUBE_SHORTS:
                style = random.choice(["direct_value", "social_proof", "curiosity_gap"])
            else:
                style = random.choice(["urgency", "direct_value", "social_proof"])
        
        templates = self.FORMULAS.get(style, self.FORMULAS["curiosity_gap"])
        template = random.choice(templates)
        
        # Fill template with topic-specific content
        hook = template.format(
            topic=topic,
            action=f"use {topic}",
            controversial_take=f"{topic} is overrated",
            surprising_fact=f"{topic} is not what you think",
            authority_experts="experts",
            deadline="it's too late",
            authority_figure="Everyone",
            discovery=f"new things about {topic}",
            number=random.choice(["3", "5", "7"]),
            percentage=random.choice(["87", "93", "95", "99"]),
            time=random.choice(["30 days", "a week", "6 months"]),
            achieve_goal=f"master {topic}",
            timeframe=random.choice(["60 seconds", "a day", "a week"]),
            expensive_thing=f"expensive {topic} courses",
            desired_outcome=f"understand {topic}",
            relatable_scenario=f"you just discovered {topic}",
            achievement=f"figured out {topic}",
            challenge=f"testing {topic}",
            thing=f"deep dive into {topic}",
            insight=f"{topic} isn't what it seems",
        )
        
        # Keep it short (platform hook windows)
        words = hook.split()
        if len(words) > 15:
            hook = " ".join(words[:12]) + "..."
        
        return hook


class ScriptGenerator:
    """Generate content scripts optimized for retention and engagement."""
    
    SCRIPT_TEMPLATES = {
        "listicle": {
            "structure": [
                "HOOK: {hook}",
                "INTRO: Quick setup (why this matters)",
                "ITEM 1: {point_1} — brief explanation",
                "ITEM 2: {point_2} — brief explanation", 
                "ITEM 3: {point_3} — brief explanation",
                "TWIST: The unexpected one that surprises",
                "CTA: Follow for more {niche} content",
            ],
            "retention_tricks": [
                "Save the best for last ('But number 3 is the craziest...')",
                "Use countdown format (creates completion desire)",
                "Add a 'bonus' item after the main list",
            ],
        },
        "story": {
            "structure": [
                "HOOK: {hook}",
                "SETUP: Here's what happened...",
                "CONFLICT: But then something changed",
                "CLIMAX: The moment everything clicked",
                "LESSON: Here's what I learned",
                "CTA: Has this happened to you? Comment below",
            ],
            "retention_tricks": [
                "Start mid-action ('So there I was...')",
                "Use tension ('I couldn't believe what happened next')",
                "End with a cliffhanger for part 2",
            ],
        },
        "educational": {
            "structure": [
                "HOOK: {hook}",
                "CONTEXT: Why this matters right now",
                "EXPLANATION: How it actually works",
                "EXAMPLE: Real-world demonstration",
                "APPLICATION: How you can use this",
                "CTA: Save this for later & share with someone who needs it",
            ],
            "retention_tricks": [
                "Use analogies ('Think of it like...')",
                "Address objections ('You might be thinking...')",
                "Add a 'secret tip' at the end",
            ],
        },
        "trend_reaction": {
            "structure": [
                "HOOK: {hook}",
                "CONTEXT: What's happening with {topic}",
                "TAKE: Here's my hot take on this",
                "EVIDENCE: Here's why I think this",
                "PREDICTION: Here's what I think happens next",
                "CTA: Do you agree? Let me know",
            ],
            "retention_tricks": [
                "Have a controversial but defensible take",
                "Use 'but here's the thing...' transitions",
                "Include a bold prediction people will comment on",
            ],
        },
    }
    
    def generate(self, topic: str, hook: str, platform: Platform, 
                 format_type: str = "auto") -> dict:
        """Generate a full content script."""
        profile = get_profile(platform)
        
        if format_type == "auto":
            # Pick format based on topic and platform
            format_type = self._pick_format(topic, platform)
        
        template = self.SCRIPT_TEMPLATES.get(format_type, self.SCRIPT_TEMPLATES["educational"])
        
        # Build the script
        script_lines = []
        for line in template["structure"]:
            script_lines.append(line.format(
                hook=hook,
                topic=topic,
                niche=topic,
                point_1=f"First key insight about {topic}",
                point_2=f"What most people miss about {topic}",
                point_3=f"The game-changing aspect of {topic}",
            ))
        
        return {
            "format": format_type,
            "script": "\n".join(script_lines),
            "retention_tricks": template["retention_tricks"],
            "duration_target": profile.ideal_duration_seconds,
        }
    
    def _pick_format(self, topic: str, platform: Platform) -> str:
        """Pick the best format for a topic on a platform."""
        topic_lower = topic.lower()
        
        # Topic-based format selection
        if any(w in topic_lower for w in ["how", "tutorial", "guide", "learn"]):
            return "educational"
        elif any(w in topic_lower for w in ["story", "happened", "experience"]):
            return "story"
        elif any(w in topic_lower for w in ["trending", "viral", "reaction", "opinion"]):
            return "trend_reaction"
        else:
            return random.choice(["listicle", "educational"])


class CaptionGenerator:
    """Generate platform-optimized captions with hashtags."""
    
    NICHE_HASHTAGS = {
        "tech": ["#tech", "#technology", "#ai", "#coding", "#programming", "#gadgets", "#innovation", "#startup", "#techreview"],
        "health": ["#health", "#wellness", "#fitness", "#nutrition", "#mentalhealth", "#selfcare", "#healthyliving"],
        "finance": ["#finance", "#money", "#investing", "#personalfinance", "#wealth", "#crypto", "#stocks", "#passiveincome"],
        "lifestyle": ["#lifestyle", "#lifehacks", "#motivation", "#selfimprovement", "#productivity", "#mindset", "#growth"],
        "entertainment": ["#entertainment", "#movies", "#gaming", "#music", "#celebrity", "#viral", "#trending"],
        "science": ["#science", "#space", "#physics", "#discovery", "#research", "#knowledge", "#facts"],
        "general": ["#fyp", "#viral", "#trending", "#foryou", "#explore", "#discover", "#mustwatch"],
    }
    
    VIRAL_HASHTAGS = ["#fyp", "#foryou", "#viral", "#trending", "#explorepage"]
    
    def generate(self, topic: str, niche: str, platform: Platform, 
                 hook: str) -> dict:
        """Generate caption and hashtags."""
        profile = get_profile(platform)
        
        # Build caption
        caption_parts = [
            hook,
            "",  # blank line
            self._generate_body(topic),
            "",  # blank line
            self._generate_cta(platform),
        ]
        caption = "\n".join(caption_parts)
        
        # Build hashtags
        niche_tags = self.NICHE_HASHTAGS.get(niche.lower(), self.NICHE_HASHTAGS["general"])
        topic_tags = self._topic_hashtags(topic)
        
        all_tags = self.VIRAL_HASHTAGS + niche_tags + topic_tags
        # Deduplicate while preserving order
        seen = set()
        unique_tags = []
        for tag in all_tags:
            tag_lower = tag.lower()
            if tag_lower not in seen:
                seen.add(tag_lower)
                unique_tags.append(tag)
        
        # Limit to platform max
        tag_min, tag_max = profile.hashtag_count
        final_tags = unique_tags[:tag_max]
        
        return {
            "caption": caption,
            "hashtags": final_tags,
            "tag_string": " ".join(final_tags),
        }
    
    def _generate_body(self, topic: str) -> str:
        """Generate caption body text."""
        bodies = [
            f"Here's what you need to know about {topic} 👇",
            f"Everything about {topic} in 60 seconds ⚡",
            f"The truth about {topic} that nobody's saying 🤫",
            f"Save this for when you need to remember {topic} 📌",
            f"POV: You just learned the truth about {topic} 😳",
        ]
        return random.choice(bodies)
    
    def _generate_cta(self, platform: Platform) -> str:
        """Generate call-to-action text."""
        ctas = [
            "Follow for more 🔔",
            "Save this & share with someone who needs it",
            "Comment your thoughts below 👇",
            "Do you agree? Let me know!",
            "Which one surprised you the most?",
            "Drop a 🤯 if this blew your mind",
            "Tag someone who needs to see this",
        ]
        return random.choice(ctas)
    
    def _topic_hashtags(self, topic: str) -> list[str]:
        """Generate hashtags from the topic."""
        words = topic.lower().split()
        tags = []
        for word in words:
            if len(word) > 3:  # Skip short words
                tags.append(f"#{word}")
        # Also add the full phrase as one tag
        tags.append(f"#{''.join(words)}")
        return tags


class ContentFactory:
    """Main content generation pipeline."""
    
    def __init__(self):
        self.hook_gen = HookGenerator()
        self.script_gen = ScriptGenerator()
        self.caption_gen = CaptionGenerator()
    
    def generate(self, topic: str, platform: Platform, niche: str = "general",
                 format_type: str = "auto") -> ContentPiece:
        """Generate a complete piece of content."""
        logger.info(f"Generating content: '{topic}' for {platform.value}")
        
        # 1. Generate hook
        hook = self.hook_gen.generate(topic, platform)
        
        # 2. Generate script
        script_data = self.script_gen.generate(topic, hook, platform, format_type)
        
        # 3. Generate caption + hashtags
        caption_data = self.caption_gen.generate(topic, niche, platform, hook)
        
        # 4. Estimate duration
        duration = self._estimate_duration(script_data["script"], platform)
        
        # 5. Assemble content piece
        content = ContentPiece(
            title=topic,
            hook=hook,
            script=script_data["script"],
            caption=caption_data["caption"],
            hashtags=caption_data["hashtags"],
            format=script_data["format"],
            platform=platform.value,
            duration_seconds=duration,
            metadata={
                "retention_tricks": script_data["retention_tricks"],
                "tag_string": caption_data["tag_string"],
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "niche": niche,
            },
        )
        
        # 6. Score against algorithm
        score = score_content({
            "hook": hook,
            "caption": caption_data["caption"],
            "hashtags": caption_data["hashtags"],
            "duration_seconds": duration,
            "format": script_data["format"],
        }, platform)
        
        content.engagement_score = score["overall_score"]
        content.algorithm_grade = score["grade"]
        content.suggestions = score["suggestions"]
        
        logger.info(f"Content generated: grade={score['grade']} score={score['overall_score']}")
        
        return content
    
    def generate_batch(self, topics: list[str], platform: Platform, 
                       niche: str = "general") -> list[ContentPiece]:
        """Generate multiple pieces of content."""
        pieces = []
        for topic in topics:
            try:
                piece = self.generate(topic, platform, niche)
                pieces.append(piece)
            except Exception as e:
                logger.error(f"Failed to generate content for '{topic}': {e}")
        
        # Sort by engagement score
        pieces.sort(key=lambda x: x.engagement_score, reverse=True)
        return pieces
    
    def _estimate_duration(self, script: str, platform: Platform) -> int:
        """Estimate video duration from script (words → seconds)."""
        word_count = len(script.split())
        # Average speaking rate: ~150 words/min for videos
        # But with visuals/b-roll, faster pacing: ~180 words/min
        seconds = int((word_count / 180) * 60)
        
        profile = get_profile(platform)
        # Clamp to platform limits
        min_dur, max_dur = profile.ideal_duration_seconds
        return max(min_dur, min(seconds, max_dur))
