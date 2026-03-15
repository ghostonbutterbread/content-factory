# Content Factory — AI-Powered UGC Automation

Automated content creation pipeline optimized for algorithm performance.

## Architecture

```
Trend Sources → Content Generator → Platform Formatter → Publisher
     ↓               ↓                    ↓                  ↓
Google Trends    AI Script Writer    TikTok format       API upload
Reddit hot       Visual Generator    YouTube Shorts      Scheduler
Twitter/X        Voiceover Gen       IG Reels            Analytics
YouTube trends
```

## Modules

### 1. Trend Scraper (`scrapers/`)
- `google_trends.py` — Google Trends API + rising queries
- `reddit.py` — Reddit hot/rising posts across niches
- `youtube.py` — YouTube trending + popular shorts

### 2. Content Generator (`generators/`)
- `script_writer.py` — AI-powered script generation
- `hook_generator.py` — First 3 seconds optimization
- `visual_generator.py` — Image/video asset creation

### 3. Algorithm Intelligence (`core/`)
- `algorithm_profiles.py` — Platform-specific optimization rules
- `engagement_predictor.py` — Score content before publishing
- `timing_optimizer.py` — Best posting times per platform

### 4. Platform Formatter (`core/`)
- `formatter.py` — Adapt content to platform specs
- `caption_generator.py` — Platform-optimized captions/hashtags

### 5. Pipeline (`core/`)
- `pipeline.py` — End-to-end orchestration
- `scheduler.py` — Timing and frequency control

## Usage

```bash
# Discover trending topics
python -m content_factory discover --niche tech --limit 10

# Generate content from a trend
python -m content_factory generate --trend "AI tools 2026" --platform tiktok

# Full pipeline: discover → generate → format
python -m content_factory pipeline --niche tech --count 5 --platform all

# Score existing content for algorithm fit
python -m content_factory score --file content_idea.json --platform tiktok
```

## Algorithm Optimization

Each platform has specific signals the algorithm looks for:

### TikTok
- Hook in first 0.5 seconds
- Completion rate > 80%
- Rewatch value
- Comment bait (questions, controversial takes)
- Trending sounds/hashtags

### YouTube Shorts
- CTR > 10%
- AVD > 70%
- First frame hook
- Loop-friendly endings
- Search-optimized titles

### Instagram Reels
- Share/save ratio
- Audio trending match
- Carousel-style information density
- Story-worthy content

## Niches

Configure in `config/niches.yaml` — each niche has:
- Seed keywords
- Trend sources
- Content templates
- Audience demographics
- Optimal posting times
