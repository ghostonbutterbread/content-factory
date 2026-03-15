"""CLI Interface for Content Factory."""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from core.algorithm_profiles import Platform, get_profile, score_content, get_best_posting_times
from generators.content import ContentFactory
from scrapers.trends import TrendAggregator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("content-factory")


def cmd_discover(args):
    """Discover trending topics."""
    print(f"\n🔍 Discovering trends" + (f" for niche: {args.niche}" if args.niche else " (all niches)") + "...\n")
    
    aggregator = TrendAggregator()
    
    if args.niche:
        trends = asyncio.run(aggregator.discover_for_niche(args.niche, limit=args.limit))
    else:
        trends = asyncio.run(aggregator.discover(limit=args.limit))
    
    print(f"Found {len(trends)} trends:\n")
    print(f"{'#':<4} {'Score':<8} {'Source':<20} {'Title'}")
    print("─" * 80)
    
    for i, trend in enumerate(trends, 1):
        score_str = f"{trend.score:.1f}"
        print(f"{i:<4} {score_str:<8} {trend.source:<20} {trend.title[:50]}")
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump([{
                "title": t.title,
                "source": t.source,
                "score": t.score,
                "url": t.url,
                "keywords": t.keywords,
            } for t in trends], f, indent=2)
        print(f"\n💾 Saved to {args.output}")
    
    return trends


def cmd_generate(args):
    """Generate content from a topic."""
    print(f"\n🎬 Generating {args.platform} content for: {args.topic}\n")
    
    factory = ContentFactory()
    platform = Platform(args.platform)
    
    piece = factory.generate(
        topic=args.topic,
        platform=platform,
        niche=args.niche,
        format_type=args.format,
    )
    
    _print_content(piece)
    
    if args.output:
        _save_content(piece, args.output)
    
    return piece


def cmd_pipeline(args):
    """Full pipeline: discover → generate → score."""
    print(f"\n🚀 Running full pipeline for {args.platform}")
    print(f"   Niche: {args.niche} | Count: {args.count}\n")
    
    aggregator = TrendAggregator()
    factory = ContentFactory()
    platform = Platform(args.platform)
    
    # 1. Discover trends
    print("📡 Step 1: Discovering trends...")
    trends = asyncio.run(aggregator.discover_for_niche(args.niche, limit=args.count * 2))
    print(f"   Found {len(trends)} trends")
    
    # 2. Generate content for top trends
    print("\n🎨 Step 2: Generating content...")
    topics = [t.title for t in trends[:args.count]]
    pieces = factory.generate_batch(topics, platform, args.niche)
    print(f"   Generated {len(pieces)} pieces")
    
    # 3. Show results
    print("\n📊 Step 3: Results\n")
    print(f"{'Grade':<6} {'Score':<8} {'Format':<15} {'Hook'}")
    print("─" * 90)
    
    for piece in pieces:
        print(f"{piece.algorithm_grade:<6} {piece.engagement_score:<8.1f} {piece.format:<15} {piece.hook[:55]}")
    
    # 4. Show best piece in detail
    if pieces:
        best = pieces[0]
        print(f"\n{'='*60}")
        print(f"🏆 TOP CONTENT (Grade: {best.algorithm_grade}, Score: {best.engagement_score})")
        print(f"{'='*60}\n")
        _print_content(best)
    
    # 5. Save all
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        for i, piece in enumerate(pieces):
            _save_content(piece, output_dir / f"content_{i+1}.json")
        print(f"\n💾 All content saved to {output_dir}/")
    
    return pieces


def cmd_score(args):
    """Score existing content."""
    print(f"\n📊 Scoring content for {args.platform}...\n")
    
    platform = Platform(args.platform)
    
    with open(args.file) as f:
        content = json.load(f)
    
    result = score_content(content, platform)
    
    print(f"Overall Score: {result['overall_score']}/100 (Grade: {result['grade']})")
    print(f"\nBreakdown:")
    for signal, score in result["breakdown"].items():
        bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
        print(f"  {signal:<20} {bar} {score}%")
    
    if result["suggestions"]:
        print(f"\nSuggestions:")
        for s in result["suggestions"]:
            print(f"  {s}")


def cmd_times(args):
    """Show best posting times."""
    platform = Platform(args.platform) if args.platform else Platform.TIKTOK
    times = get_best_posting_times(platform)
    
    print(f"\n⏰ Best posting times for {platform.value}:\n")
    print(f"  Weekdays:  {', '.join(times['weekdays'])}")
    print(f"  Weekends:  {', '.join(times['weekends'])}")
    print(f"  Best day:  {times['best_day']}")
    print(f"  Peak hours: {', '.join(str(h) + ':00' for h in times['peak_hours'])}")


def _print_content(piece):
    """Print a content piece in a readable format."""
    print(f"📌 Title: {piece.title}")
    print(f"🎯 Platform: {piece.platform} | Format: {piece.format} | Duration: {piece.duration_seconds}s")
    print(f"📊 Grade: {piece.algorithm_grade} ({piece.engagement_score}/100)")
    print()
    print(f"🪝 HOOK: {piece.hook}")
    print()
    print("📝 SCRIPT:")
    print(piece.script)
    print()
    print("📱 CAPTION:")
    print(piece.caption)
    print()
    print(f"🏷️ HASHTAGS: {' '.join(piece.hashtags)}")
    
    if piece.suggestions:
        print()
        print("💡 SUGGESTIONS:")
        for s in piece.suggestions:
            print(f"   {s}")
    print()


def _save_content(piece, path):
    """Save content to JSON."""
    with open(path, "w") as f:
        json.dump(piece.to_dict(), f, indent=2)
    print(f"💾 Saved to {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Content Factory — AI-powered UGC automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="Command to run")
    
    # discover
    p = sub.add_parser("discover", help="Discover trending topics")
    p.add_argument("--niche", default=None, help="Content niche (tech, health, finance, etc.)")
    p.add_argument("--limit", type=int, default=20, help="Number of trends to return")
    p.add_argument("--output", "-o", help="Save trends to JSON file")
    
    # generate
    p = sub.add_parser("generate", help="Generate content from a topic")
    p.add_argument("--topic", required=True, help="Topic to create content about")
    p.add_argument("--platform", default="tiktok", choices=["tiktok", "youtube_shorts", "instagram_reels"])
    p.add_argument("--niche", default="general", help="Content niche")
    p.add_argument("--format", default="auto", help="Content format (listicle, story, educational, trend_reaction, auto)")
    p.add_argument("--output", "-o", help="Save content to JSON file")
    
    # pipeline
    p = sub.add_parser("pipeline", help="Full pipeline: discover → generate → score")
    p.add_argument("--niche", default="tech", help="Content niche")
    p.add_argument("--platform", default="tiktok", choices=["tiktok", "youtube_shorts", "instagram_reels", "all"])
    p.add_argument("--count", type=int, default=5, help="Number of content pieces to generate")
    p.add_argument("--output", "-o", help="Save content to directory")
    
    # score
    p = sub.add_parser("score", help="Score existing content for algorithm fit")
    p.add_argument("--file", required=True, help="JSON file with content to score")
    p.add_argument("--platform", default="tiktok", choices=["tiktok", "youtube_shorts", "instagram_reels"])
    
    # times
    p = sub.add_parser("times", help="Show best posting times")
    p.add_argument("--platform", default="tiktok", choices=["tiktok", "youtube_shorts", "instagram_reels"])
    
    args = parser.parse_args()
    
    commands = {
        "discover": cmd_discover,
        "generate": cmd_generate,
        "pipeline": cmd_pipeline,
        "score": cmd_score,
        "times": cmd_times,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
