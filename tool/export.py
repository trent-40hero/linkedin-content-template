#!/usr/bin/env python3
"""
Export LinkedIn posts to Make.com webhook format.

Reads posts from posts/{week}/ directory and generates JSON
payload for Make.com or n8n automation.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Try to import requests for webhook sending
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# n8n webhook URL for LinkedIn post scheduling
N8N_WEBHOOK_URL = os.environ.get(
    "N8N_LINKEDIN_WEBHOOK",
    "https://your-n8n-instance.com/webhook/linkedin-posts"
)


def get_project_root() -> Path:
    """Get the linkedin-content project root directory."""
    # Assume we're in tool/ subdirectory
    return Path(__file__).parent.parent


def parse_post_file(filepath: Path) -> Optional[Dict]:
    """
    Parse a post markdown file and extract content and metadata.

    Expected format:
    ---
    slot: 1
    format: story
    pillar: educational
    scheduled: 2026-01-28T08:47:00-05:00
    hashtags: [automation, engineering]
    ---

    Post content here...
    """
    try:
        content = filepath.read_text()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return None

    # Parse YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)

    if frontmatter_match:
        frontmatter_str = frontmatter_match.group(1)
        body = frontmatter_match.group(2).strip()

        # Simple YAML parsing (avoiding external dependency)
        metadata = {}
        for line in frontmatter_str.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Parse arrays
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]

                # Parse booleans
                elif value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'

                # Parse numbers
                elif value.isdigit():
                    value = int(value)

                metadata[key] = value
    else:
        # No frontmatter, just content
        body = content.strip()
        metadata = {}

    # Count words
    word_count = len(body.split())

    # Determine length category
    if word_count <= 150:
        length_category = "short"
    elif word_count <= 220:
        length_category = "medium"
    else:
        length_category = "long"

    return {
        "content": body,
        "word_count": word_count,
        "length_category": length_category,
        "metadata": metadata,
        "source_file": str(filepath)
    }


def load_week_posts(week: str) -> List[Dict]:
    """
    Load all posts for a given week from posts/{week}/ directory.
    """
    project_root = get_project_root()
    week_dir = project_root / "posts" / week

    if not week_dir.exists():
        print(f"Week directory not found: {week_dir}", file=sys.stderr)
        return []

    posts = []

    # Find all post-*.md files
    for filepath in sorted(week_dir.glob("post-*.md")):
        post = parse_post_file(filepath)
        if post:
            posts.append(post)

    return posts


def generate_export(week: str, posts: List[Dict]) -> Dict:
    """
    Generate Make.com webhook payload from posts.
    """
    export_posts = []

    for i, post in enumerate(posts):
        metadata = post.get("metadata", {})

        export_post = {
            "slot": metadata.get("slot", i + 1),
            "scheduled_datetime": metadata.get("scheduled", None),
            "content": post["content"],
            "hashtags": metadata.get("hashtags", []),
            "has_link": "http" in post["content"].lower(),
            "metadata": {
                "pillar": metadata.get("pillar", "unknown"),
                "format": metadata.get("format", "unknown"),
                "word_count": post["word_count"],
                "length_category": post["length_category"],
                "source_file": post["source_file"]
            }
        }

        export_posts.append(export_post)

    # Calculate summary statistics
    pillars_used = list(set(p["metadata"]["pillar"] for p in export_posts))
    formats_used = list(set(p["metadata"]["format"] for p in export_posts))
    total_words = sum(p["metadata"]["word_count"] for p in export_posts)

    return {
        "week": week,
        "generated_at": datetime.now().isoformat(),
        "author": {
            "name": os.environ.get("LINKEDIN_AUTHOR_NAME", "[YOUR_NAME]"),
            "company": os.environ.get("LINKEDIN_AUTHOR_COMPANY", "[YOUR_COMPANY]")
        },
        "posts": export_posts,
        "summary": {
            "total_posts": len(export_posts),
            "pillars_used": pillars_used,
            "formats_used": formats_used,
            "total_words": total_words,
            "avg_words": total_words // len(export_posts) if export_posts else 0
        }
    }


def send_to_webhook(webhook_url: str, payload: Dict) -> Dict:
    """
    Send payload to Make.com webhook.
    """
    if not REQUESTS_AVAILABLE:
        return {
            "success": False,
            "error": "requests library not installed. Run: pip install requests"
        }

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        return {
            "success": response.status_code in (200, 201, 202),
            "status_code": response.status_code,
            "response": response.text[:500] if response.text else None
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def save_export(week: str, payload: Dict) -> Path:
    """
    Save export payload to exports/{week}.json
    """
    project_root = get_project_root()
    exports_dir = project_root / "exports"
    exports_dir.mkdir(exist_ok=True)

    export_path = exports_dir / f"{week}.json"
    export_path.write_text(json.dumps(payload, indent=2))

    return export_path


def main():
    parser = argparse.ArgumentParser(
        description="Export LinkedIn posts to Make.com format"
    )
    parser.add_argument(
        "--week",
        required=True,
        help="Week to export (e.g., '2026-W05')"
    )
    parser.add_argument(
        "--webhook-url",
        help="Make.com webhook URL to send payload"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        default=True,
        help="Save export to exports/ directory (default: true)"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save export file"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON to stdout"
    )
    parser.add_argument(
        "--n8n",
        action="store_true",
        help="Send to n8n webhook for scheduled posting"
    )
    parser.add_argument(
        "--n8n-url",
        help=f"Override n8n webhook URL (default: {N8N_WEBHOOK_URL})"
    )

    args = parser.parse_args()

    # Load posts
    posts = load_week_posts(args.week)

    if not posts:
        print(f"No posts found for week {args.week}", file=sys.stderr)
        print(f"Create posts in: posts/{args.week}/post-1.md, post-2.md, etc.", file=sys.stderr)
        return 1

    # Generate export
    payload = generate_export(args.week, posts)

    # Save if requested
    if args.save and not args.no_save:
        export_path = save_export(args.week, payload)
        print(f"✓ Saved export to: {export_path}")

    # Output JSON if requested
    if args.json:
        print(json.dumps(payload, indent=2))

    # Send to webhook if URL provided
    if args.webhook_url:
        print(f"Sending to webhook: {args.webhook_url[:50]}...")
        result = send_to_webhook(args.webhook_url, payload)

        if result["success"]:
            print("✓ Successfully sent to Make.com")
        else:
            print(f"✗ Failed to send: {result.get('error', 'Unknown error')}")
            return 1

    # Send to n8n if requested
    if args.n8n:
        n8n_url = args.n8n_url or N8N_WEBHOOK_URL
        print(f"Sending to n8n: {n8n_url[:50]}...")
        result = send_to_webhook(n8n_url, payload)

        if result["success"]:
            # Try to parse n8n response
            try:
                n8n_response = json.loads(result.get("response", "{}"))
                posts_scheduled = n8n_response.get("posts_scheduled", len(payload["posts"]))
                print(f"✓ Successfully scheduled {posts_scheduled} posts via n8n")
            except (json.JSONDecodeError, TypeError):
                print("✓ Successfully sent to n8n")
        else:
            print(f"✗ Failed to send to n8n: {result.get('error', 'Unknown error')}")
            return 1

    # Print summary
    if not args.json:
        print(f"\nExport Summary for {args.week}")
        print("=" * 40)
        print(f"Posts: {payload['summary']['total_posts']}")
        print(f"Total words: {payload['summary']['total_words']}")
        print(f"Pillars: {', '.join(payload['summary']['pillars_used'])}")
        print(f"Formats: {', '.join(payload['summary']['formats_used'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
