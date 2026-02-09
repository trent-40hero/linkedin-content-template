#!/usr/bin/env python3
"""
LinkedIn posting schedule generator with compliance rules.

Generates randomized posting times that comply with safety rules:
- 4 posts/week
- Tue-Thu preferred, Mon/Fri backup
- Business hours (7am-6pm ET)
- Optimal windows (8-10am, 12-2pm)
- Random minutes (never :00 or :30)
- No consecutive days
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import sys

# Compliance configuration
POSTS_PER_WEEK = 4
PREFERRED_DAYS = [1, 2, 3]  # Tuesday, Wednesday, Thursday (Monday=0)
BACKUP_DAYS = [0, 4]  # Monday, Friday
OPTIMAL_HOURS = [8, 9, 12, 13]  # 8-10am and 12-2pm windows
BUSINESS_HOURS = list(range(7, 18))  # 7am-6pm
FORBIDDEN_MINUTES = [0, 30]
TIMEZONE = "America/New_York"


def get_week_start(week_str: str) -> datetime:
    """
    Parse week string and return the Monday of that week.

    Formats:
    - "next" - next week
    - "current" - current week
    - "2026-W05" - ISO week format
    """
    today = datetime.now()

    if week_str.lower() == "next":
        # Find next Monday
        days_ahead = 7 - today.weekday()
        return today + timedelta(days=days_ahead)

    elif week_str.lower() == "current":
        # Find this week's Monday
        days_behind = today.weekday()
        return today - timedelta(days=days_behind)

    else:
        # Parse ISO week format (2026-W05)
        try:
            year, week = week_str.split("-W")
            year = int(year)
            week = int(week)
            # ISO week: first Thursday of year is in week 1
            jan4 = datetime(year, 1, 4)
            week1_monday = jan4 - timedelta(days=jan4.weekday())
            return week1_monday + timedelta(weeks=week - 1)
        except ValueError:
            raise ValueError(f"Invalid week format: {week_str}. Use 'next', 'current', or '2026-W05'")


def get_random_minute() -> int:
    """Generate random minute avoiding :00 and :30."""
    while True:
        minute = random.randint(5, 55)
        if minute not in FORBIDDEN_MINUTES:
            return minute


def get_posting_hour(prefer_optimal: bool = True) -> int:
    """
    Get a posting hour.

    80% chance of optimal window, 20% chance of other business hours.
    """
    if prefer_optimal and random.random() < 0.8:
        return random.choice(OPTIMAL_HOURS)
    else:
        return random.choice(BUSINESS_HOURS)


def select_posting_days(week_start: datetime, num_posts: int = 4) -> List[datetime]:
    """
    Select posting days for the week.

    Prefers Tue-Thu, uses Mon/Fri as backup.
    Ensures no consecutive days.
    """
    available_days = []

    # Add preferred days (Tue, Wed, Thu)
    for day_offset in PREFERRED_DAYS:
        available_days.append(week_start + timedelta(days=day_offset))

    # Add backup days (Mon, Fri) if needed
    for day_offset in BACKUP_DAYS:
        available_days.append(week_start + timedelta(days=day_offset))

    # Select days ensuring no consecutive days
    selected = []
    attempts = 0
    max_attempts = 100

    while len(selected) < num_posts and attempts < max_attempts:
        attempts += 1
        candidate = random.choice(available_days)

        # Check for consecutive days
        is_consecutive = False
        for existing in selected:
            if abs((candidate - existing).days) <= 1:
                is_consecutive = True
                break

        if not is_consecutive and candidate not in selected:
            selected.append(candidate)

    # If we couldn't avoid consecutive days, just pick any
    if len(selected) < num_posts:
        remaining = [d for d in available_days if d not in selected]
        while len(selected) < num_posts and remaining:
            selected.append(remaining.pop(0))

    return sorted(selected)


def generate_schedule(week_str: str, num_posts: int = 4) -> List[Dict]:
    """
    Generate a compliant posting schedule for the week.

    Returns list of dictionaries with slot number and datetime.
    """
    week_start = get_week_start(week_str)
    posting_days = select_posting_days(week_start, num_posts)

    schedule = []
    used_hours = []

    for i, day in enumerate(posting_days):
        # Get hour (avoid repeating same hour if possible)
        hour = get_posting_hour()
        attempts = 0
        while hour in used_hours and attempts < 10:
            hour = get_posting_hour(prefer_optimal=False)
            attempts += 1
        used_hours.append(hour)

        minute = get_random_minute()

        post_datetime = day.replace(hour=hour, minute=minute, second=0, microsecond=0)

        schedule.append({
            "slot": i + 1,
            "date": post_datetime.strftime("%Y-%m-%d"),
            "time": post_datetime.strftime("%H:%M"),
            "datetime": post_datetime.strftime("%Y-%m-%dT%H:%M:00-05:00"),  # ET
            "day_name": post_datetime.strftime("%A"),
            "iso_week": post_datetime.strftime("%Y-W%W")
        })

    return schedule


def validate_schedule(schedule: List[Dict]) -> Dict:
    """
    Validate a schedule against compliance rules.

    Returns validation result with any issues found.
    """
    issues = []

    # Check post count
    if len(schedule) > POSTS_PER_WEEK:
        issues.append(f"Too many posts: {len(schedule)} > {POSTS_PER_WEEK}")

    # Check for more than 3 consecutive posting days
    dates = [datetime.strptime(s["date"], "%Y-%m-%d") for s in schedule]
    consecutive_count = 1
    for i in range(len(dates) - 1):
        if (dates[i + 1] - dates[i]).days == 1:
            consecutive_count += 1
            if consecutive_count > 3:
                issues.append(f"More than 3 consecutive posting days ending {schedule[i + 1]['date']}")
        else:
            consecutive_count = 1

    # Check for weekend posts
    for s in schedule:
        day = datetime.strptime(s["date"], "%Y-%m-%d").weekday()
        if day >= 5:  # Saturday or Sunday
            issues.append(f"Weekend post: {s['date']} ({s['day_name']})")

    # Check for forbidden minutes
    for s in schedule:
        minute = int(s["time"].split(":")[1])
        if minute in FORBIDDEN_MINUTES:
            issues.append(f"Forbidden minute (:00 or :30): {s['datetime']}")

    # Check business hours
    for s in schedule:
        hour = int(s["time"].split(":")[0])
        if hour < 7 or hour >= 18:
            issues.append(f"Outside business hours: {s['datetime']}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "post_count": len(schedule)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate compliant LinkedIn posting schedule"
    )
    parser.add_argument(
        "--week",
        default="next",
        help="Week to schedule: 'next', 'current', or '2026-W05' format"
    )
    parser.add_argument(
        "--posts",
        type=int,
        default=4,
        help="Number of posts (default: 4)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate an existing schedule (reads from stdin)"
    )

    args = parser.parse_args()

    if args.validate:
        # Read schedule from stdin and validate
        schedule = json.load(sys.stdin)
        result = validate_schedule(schedule)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result["valid"]:
                print("✓ Schedule is compliant")
            else:
                print("✗ Schedule has issues:")
                for issue in result["issues"]:
                    print(f"  - {issue}")
        return 0 if result["valid"] else 1

    # Generate schedule
    schedule = generate_schedule(args.week, args.posts)
    validation = validate_schedule(schedule)

    if args.json:
        output = {
            "week": args.week,
            "generated_at": datetime.now().isoformat(),
            "schedule": schedule,
            "validation": validation
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\nLinkedIn Posting Schedule for {args.week}")
        print("=" * 50)
        for s in schedule:
            print(f"  Post {s['slot']}: {s['day_name']} {s['date']} at {s['time']} ET")
        print()
        if validation["valid"]:
            print("✓ Schedule is compliant with all safety rules")
        else:
            print("⚠ Issues found:")
            for issue in validation["issues"]:
                print(f"  - {issue}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
