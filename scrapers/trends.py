"""Trend Scrapers — Pull trending topics from multiple sources.

Scrapes: Google Trends, Reddit, YouTube
Returns normalized trend objects for content generation.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class Trend:
    """A trending topic with metadata for content generation."""
    title: str
    source: str  # google_trends, reddit, youtube
    url: str = ""
    score: float = 0.0  # Trending strength (0-100)
    category: str = ""
    keywords: list = field(default_factory=list)
    description: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.keywords:
            self.keywords = self.title.lower().split()


class GoogleTrendsScraper:
    """Pull trending searches from Google Trends."""
    
    def __init__(self):
        self.base_url = "https://trends.google.com/trendingjson"
        self.geo = "US"
    
    async def fetch(self, category: str = "all", limit: int = 20) -> list[Trend]:
        """Fetch current trending searches."""
        trends = []
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    self.base_url,
                    params={
                        "geo": self.geo,
                        "category": category,
                        "hours": 24,
                    },
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=15,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("trendingSearchesDays", []):
                        for search in item.get("trendingSearches", []):
                            trend = Trend(
                                title=search.get("title", {}).get("query", ""),
                                source="google_trends",
                                url=search.get("title", {}).get("exploreLink", ""),
                                score=float(search.get("formattedTraffic", "0").replace("+", "").replace(",", "") or 0),
                                keywords=search.get("relatedQueries", []),
                                description=search.get("articles", [{}])[0].get("snippet", "") if search.get("articles") else "",
                            )
                            if trend.title:
                                trends.append(trend)
                    logger.info(f"Google Trends: {len(trends)} trends fetched")
                else:
                    logger.debug(f"Google Trends returned {resp.status_code}")
        except Exception as e:
            logger.debug(f"Google Trends error: {e}")
        
        return trends[:limit]
    
    async def fetch_rising(self, limit: int = 20) -> list[Trend]:
        """Fetch rising/trending queries using pytrends."""
        trends = []
        try:
            # Use real-time trending searches (most reliable)
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://trends.google.com/trendingjson",
                    params={"geo": "US", "hours": 4},
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=15,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for day in data.get("trendingSearchesDays", []):
                        for s in day.get("trendingSearches", []):
                            trends.append(Trend(
                                title=s.get("title", {}).get("query", ""),
                                source="google_trends_rising",
                                score=float(s.get("formattedTraffic", "50K+").replace("K+", "000").replace("M+", "000000").replace("+", "").replace(",", "") or 0),
                            ))
        except Exception as e:
            logger.debug(f"Google Trends rising error: {e}")
        
        return trends[:limit]


class RedditScraper:
    """Pull trending topics from Reddit."""
    
    def __init__(self):
        self.base_url = "https://www.reddit.com"
    
    async def fetch(self, subreddit: str = "all", sort: str = "hot", limit: int = 20) -> list[Trend]:
        """Fetch hot/rising posts from a subreddit."""
        trends = []
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.base_url}/r/{subreddit}/{sort}.json",
                    params={"limit": limit, "t": "day"},
                    headers={"User-Agent": "ContentFactory/1.0"},
                    timeout=15,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for post in data.get("data", {}).get("children", []):
                        p = post.get("data", {})
                        trend = Trend(
                            title=p.get("title", ""),
                            source="reddit",
                            url=f"https://reddit.com{p.get('permalink', '')}",
                            score=p.get("score", 0) / 1000,  # Normalize to thousands
                            category=p.get("subreddit", ""),
                            description=p.get("selftext", "")[:200],
                        )
                        if trend.title:
                            trends.append(trend)
                    logger.info(f"Reddit r/{subreddit}: {len(trends)} posts fetched")
        except Exception as e:
            logger.debug(f"Reddit r/{subreddit} error: {e}")
        
        return trends
    
    async def fetch_multi(self, subreddits: list[str] = None, limit_per: int = 10) -> list[Trend]:
        """Fetch from multiple subreddits."""
        if subreddits is None:
            subreddits = [
                "technology", "science", "worldnews", "todayilearned",
                "explainlikeimfive", "futurology", "space", "interestingasfuck",
                "Damnthatsinteresting", "nextfuckinglevel", "lifehacks",
                "unpopularopinion", "Showerthoughts",
            ]
        
        tasks = [self.fetch(sub, limit=limit_per) for sub in subreddits]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_trends = []
        for r in results:
            if isinstance(r, list):
                all_trends.extend(r)
        
        # Deduplicate and sort by score
        seen = set()
        unique = []
        for t in sorted(all_trends, key=lambda x: x.score, reverse=True):
            if t.title.lower() not in seen:
                seen.add(t.title.lower())
                unique.append(t)
        
        return unique


class YouTubeTrendsScraper:
    """Pull trending topics from YouTube."""
    
    def __init__(self):
        self.base_url = "https://www.youtube.com"
    
    async def fetch_trending(self, limit: int = 20) -> list[Trend]:
        """Fetch trending videos (requires scraping the trending page)."""
        trends = []
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.base_url}/feed/trending",
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=15,
                )
                # YouTube embeds initial data in a JSON blob
                # This is a simplified extraction
                content = resp.text
                # Look for trending video titles in the HTML
                import re
                titles = re.findall(r'"title":\{"runs":\[\{"text":"([^"]+)"', content)
                for title in titles[:limit]:
                    if title and len(title) > 5:
                        trends.append(Trend(
                            title=title,
                            source="youtube_trending",
                            score=50.0,
                        ))
                logger.info(f"YouTube trending: {len(trends)} videos found")
        except Exception as e:
            logger.debug(f"YouTube trending error: {e}")
        
        return trends


class TrendAggregator:
    """Aggregate trends from all sources and find the best content opportunities."""
    
    def __init__(self):
        self.google = GoogleTrendsScraper()
        self.reddit = RedditScraper()
        self.youtube = YouTubeTrendsScraper()
    
    async def discover(self, limit: int = 30) -> list[Trend]:
        """Fetch trends from all sources, merge, and rank."""
        logger.info("Discovering trends from all sources...")
        
        # Fetch from all sources in parallel
        results = await asyncio.gather(
            self.google.fetch(limit=20),
            self.reddit.fetch_multi(limit_per=5),
            self.youtube.fetch_trending(limit=15),
            return_exceptions=True,
        )
        
        all_trends = []
        for r in results:
            if isinstance(r, list):
                all_trends.extend(r)
        
        # Fallback to seed trends if live scraping returned nothing
        if not all_trends:
            logger.info("Live scraping returned 0 trends, using seed database")
            from scrapers.seed_trends import get_seed_trends
            seeds = get_seed_trends("general", limit)
            for s in seeds:
                all_trends.append(Trend(
                    title=s["title"],
                    source=s["source"],
                    score=s["score"],
                    keywords=s["keywords"],
                ))
        
        # Score and rank
        ranked = self._rank_trends(all_trends)
        
        logger.info(f"Total trends discovered: {len(ranked)} (top {limit} returned)")
        return ranked[:limit]
    
    def _rank_trends(self, trends: list[Trend]) -> list[Trend]:
        """Rank trends by content opportunity score."""
        # Factors: score, source diversity, keyword richness
        source_bonus = {
            "google_trends": 2.0,
            "google_trends_rising": 2.5,
            "reddit": 1.5,
            "youtube_trending": 1.8,
        }
        
        for trend in trends:
            multiplier = source_bonus.get(trend.source, 1.0)
            trend.score = trend.score * multiplier
            
            # Bonus for having good keywords
            if len(trend.keywords) > 2:
                trend.score *= 1.2
            
            # Bonus for having a description (more context)
            if trend.description:
                trend.score *= 1.1
        
        # Sort by score
        return sorted(trends, key=lambda x: x.score, reverse=True)
    
    async def discover_for_niche(self, niche: str, limit: int = 20) -> list[Trend]:
        """Discover trends relevant to a specific niche."""
        # Map niches to relevant subreddits
        niche_map = {
            "tech": ["technology", "gadgets", "programming", "artificial", "futurology"],
            "health": ["health", "fitness", "nutrition", "medicine", "mentalhealth"],
            "finance": ["personalfinance", "investing", "cryptocurrency", "stocks", "economy"],
            "lifestyle": ["lifehacks", "selfimprovement", "GetMotivated", "todayilearned"],
            "entertainment": ["movies", "television", "gaming", "music", "celebrity"],
            "science": ["science", "space", "physics", "biology", "chemistry"],
            "politics": ["politics", "worldnews", "geopolitics", "PoliticalDiscussion"],
        }
        
        subreddits = niche_map.get(niche.lower(), ["all"])
        
        # Fetch from relevant sources
        results = await asyncio.gather(
            self.google.fetch(limit=15),
            self.reddit.fetch_multi(subreddits=subreddits, limit_per=8),
            return_exceptions=True,
        )
        
        all_trends = []
        for r in results:
            if isinstance(r, list):
                all_trends.extend(r)
        
        # Fallback to seed trends if live scraping returned nothing
        if not all_trends:
            logger.info(f"Live scraping returned 0 trends for niche '{niche}', using seed database")
            from scrapers.seed_trends import get_seed_trends
            seeds = get_seed_trends(niche, limit)
            for s in seeds:
                all_trends.append(Trend(
                    title=s["title"],
                    source=s["source"],
                    score=s["score"],
                    keywords=s["keywords"],
                ))
        
        return self._rank_trends(all_trends)[:limit]
