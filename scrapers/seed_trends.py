"""Seed trends database — curated trending topics by niche.

Used as fallback when live scraping is unavailable, or as a
starting point for content generation.
"""

# Topical seed data organized by niche
# Updated with commonly trending categories that perform well on short-form video

SEED_TRENDS = {
    "tech": [
        "AI tools that replace your entire job",
        "Coding in 60 seconds",
        "Tech gadgets you didn't know existed",
        "Why everyone is switching to this app",
        "The future of AI in 2026",
        "Free tools that replace expensive software",
        "How to automate boring tasks with AI",
        "This new programming language is taking over",
        "Secret browser features 99% of people don't know",
        "The app that's going viral right now",
        "How to build a website in 5 minutes",
        "AI writes better code than developers?",
        "The cybersecurity mistake everyone makes",
        "This $20 gadget replaces a $500 device",
        "Linux vs Windows vs Mac in 2026",
    ],
    "health": [
        "The supplement doctors actually recommend",
        "Morning routine that changed my life",
        "Why you're always tired (it's not sleep)",
        "This food is destroying your gut health",
        "The 5-minute workout that replaces the gym",
        "What happens to your body when you quit sugar",
        "The sleep hack NASA uses",
        "Foods that boost your brain power",
        "Why cold showers are overrated",
        "The vitamin deficiency everyone has",
    ],
    "finance": [
        "The investment strategy that beats the market",
        "How to make money while you sleep",
        "Money mistakes in your 20s you'll regret",
        "The credit card hack banks don't want you to know",
        "How I saved $10K in 3 months",
        "Passive income ideas that actually work",
        "Why most people stay broke",
        "The budgeting method that changed everything",
        "Side hustles making people rich in 2026",
        "Stocks vs crypto vs real estate",
    ],
    "lifestyle": [
        "Morning routines of successful people",
        "The productivity hack that doubled my output",
        "Minimalism changed my life — here's how",
        "Things you should stop buying",
        "The 30-day challenge that transformed me",
        "Why your to-do list doesn't work",
        "Life hacks that actually work",
        "The book that changed how I think",
        "Digital detox for 7 days — what happened",
        "Habits that separate successful people",
    ],
    "entertainment": [
        "Movies coming out this month you need to see",
        "The show everyone is binge watching",
        "Celebrity transformation that shocked everyone",
        "Behind the scenes of your favorite show",
        "The video game breaking records right now",
        "Unpopular movie opinions",
        "Songs that hit different at 3am",
        "The plot twist nobody saw coming",
        "Streaming wars: which platform wins in 2026",
        "Movies that predicted the future",
    ],
    "science": [
        "Space discovery that changes everything",
        "Scientists just found something terrifying",
        "The experiment that went horribly wrong",
        "Things about the universe that break your brain",
        "New species discovered in the deep ocean",
        "Why the speed of light is the limit",
        "Quantum computing explained in 60 seconds",
        "The black hole photo nobody talks about",
        "What's inside a neutron star",
        "Climate change: what scientists actually said",
    ],
    "general": [
        "Things that just make sense",
        "Wait for it...",
        "Rating things in [category]",
        "Unpopular opinion: [take]",
        "Things I wish I knew earlier",
        "Nobody talks about this but...",
        "Here's what happens when you...",
        "3 things that will blow your mind",
        "This changed everything for me",
        "POV: you just discovered this",
    ],
}


def get_seed_trends(niche: str = "general", limit: int = 20) -> list[dict]:
    """Get seed trends for a niche."""
    topics = SEED_TRENDS.get(niche.lower(), SEED_TRENDS["general"])
    
    trends = []
    for i, topic in enumerate(topics[:limit]):
        trends.append({
            "title": topic,
            "source": "seed_db",
            "score": 100 - (i * 5),  # Decreasing score
            "url": "",
            "keywords": topic.lower().split(),
            "description": "",
        })
    
    return trends
