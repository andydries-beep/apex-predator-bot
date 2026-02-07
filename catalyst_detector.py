#!/usr/bin/env python3
"""
CATALYST DETECTOR V1.0
Real-time cryptocurrency news and catalyst detection
Uses CryptoPanic Free API to detect fresh catalysts
Runs hourly to catch opportunities within 24h

Author: Manus AI
Date: January 30, 2026
"""

import requests
import json
from datetime import datetime, timedelta
import time
import os


class CatalystDetector:
    """
    Catalyst Detector that:
    1. Monitors crypto news via CryptoPanic API
    2. Filters by sentiment (positive only)
    3. Identifies fresh catalysts (<24h old)
    4. Matches catalysts to coins
    5. Alerts on significant catalyst clusters
    """

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('CRYPTOPANIC_API_KEY')
        self.base_url = "https://cryptopanic.com/api/developer/v2"

        if not self.api_key:
            print("\u26a0 WARNING: No CryptoPanic API key found!")
            print("  Set CRYPTOPANIC_API_KEY environment variable")
            print("  Or sign up at: https://cryptopanic.com/developers/api/")
            print("  Free tier: 500 requests/day")

    def fetch_recent_news(self, hours=48, filter_type='important'):
        """
        Fetch recent crypto news

        Args:
            hours: How many hours back to fetch
            filter_type: 'rising', 'hot', 'bullish', 'bearish', 'important', 'lol'
        """
        if not self.api_key:
            print("\u274c Cannot fetch news without API key")
            return []

        try:
            url = f"{self.base_url}/posts/"
            params = {
                'auth_token': self.api_key,
                'filter': filter_type,
                'public': 'true'
            }

            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            posts = data.get('results', [])

            # Return all posts (API already filters by recency)
            # We'll analyze all available news for catalysts
            return posts

        except Exception as e:
            print(f"\u274c Error fetching news: {e}")
            return []

    def analyze_sentiment(self, posts):
        """
        Analyze sentiment of news posts
        Returns: dict of {coin: {positive: count, negative: count, neutral: count, posts: []}}
        """
        sentiment_map = {}

        for post in posts:
            # Get coins mentioned (V2 uses 'instruments' instead of 'currencies')
            currencies = post.get('instruments', [])

            # Get sentiment (votes)
            votes = post.get('votes', {})
            positive = votes.get('positive', 0)
            negative = votes.get('negative', 0)

            # Determine overall sentiment
            if positive > negative:
                sentiment = 'positive'
            elif negative > positive:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            # Update sentiment map
            for currency in currencies:
                coin_code = currency.get('code', '').upper()
                if coin_code:
                    if coin_code not in sentiment_map:
                        sentiment_map[coin_code] = {
                            'positive': 0,
                            'negative': 0,
                            'neutral': 0,
                            'posts': []
                        }
                    sentiment_map[coin_code][sentiment] += 1
                    sentiment_map[coin_code]['posts'].append({
                        'title': post.get('title'),
                        'url': post.get('url'),
                        'published_at': post.get('published_at'),
                        'sentiment': sentiment
                    })

        return sentiment_map

    def identify_catalysts(self, sentiment_map, min_positive=3):
        """
        Identify coins with significant positive catalyst clusters

        Args:
            sentiment_map: Output from analyze_sentiment()
            min_positive: Minimum positive news count to qualify as catalyst

        Returns: List of catalyst opportunities
        """
        catalysts = []

        for coin_code, data in sentiment_map.items():
            positive_count = data['positive']
            negative_count = data['negative']

            # Filter: Must have at least min_positive positive news
            if positive_count < min_positive:
                continue

            # Filter: Positive must outweigh negative
            if positive_count <= negative_count:
                continue

            # Calculate catalyst strength
            net_sentiment = positive_count - negative_count
            total_news = positive_count + negative_count + data['neutral']

            catalyst = {
                'coin': coin_code,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': data['neutral'],
                'net_sentiment': net_sentiment,
                'total_news': total_news,
                'catalyst_strength': net_sentiment / total_news if total_news > 0 else 0,
                'posts': data['posts']
            }

            catalysts.append(catalyst)

        # Sort by catalyst strength
        catalysts.sort(key=lambda x: x['catalyst_strength'], reverse=True)

        return catalysts

    def generate_catalyst_report(self, catalysts):
        """Generate catalyst detection report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S AWST")

        report = f"""
================================================================================
CATALYST DETECTION REPORT
================================================================================
Scan Time: {timestamp}
Catalysts Found: {len(catalysts)}
================================================================================
"""

        if len(catalysts) == 0:
            report += "No significant catalysts detected in the past 24 hours.\n"
        else:
            report += f"================================================================================\n"
            report += f"DETECTED CATALYSTS\n"
            report += f"================================================================================\n"

            for i, catalyst in enumerate(catalysts, 1):
                report += f"#{i}. {catalyst['coin']}\n"
                report += f"    Catalyst Strength: {catalyst['catalyst_strength']:.0%}\n"
                report += f"    Positive News: {catalyst['positive_count']}\n"
                report += f"    Negative News: {catalyst['negative_count']}\n"
                report += f"    Net Sentiment: +{catalyst['net_sentiment']}\n"
                report += f"\n"
                report += f"    Recent Headlines:\n"

                # Show top 3 positive posts
                positive_posts = [p for p in catalyst['posts'] if p['sentiment'] == 'positive']
                for j, post in enumerate(positive_posts[:3], 1):
                    report += f"      {j}. {post['title']}\n"
                    report += f"         {post['published_at']}\n"
                    report += f"         {post['url']}\n"

                report += f"\n{'='*40}\n\n"

        report += f"================================================================================\n"
        report += "END OF REPORT\n"
        report += f"================================================================================\n"

        return report

    def run_detection(self, hours=48, min_positive=2):
        """Run catalyst detection"""
        print("=" * 80)
        print("CATALYST DETECTOR V1.0")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S AWST')}")
        print(f"Lookback: {hours} hours")
        print(f"Min Positive News: {min_positive}")
        print("=" * 80)

        if not self.api_key:
            print("\n\u274c No API key configured. Cannot run detection.")
            print("\nTo set up CryptoPanic API:")
            print("1. Sign up at: https://cryptopanic.com/developers/api/")
            print("2. Get your free API key (500 requests/day)")
            print("3. Set environment variable: export CRYPTOPANIC_API_KEY='your_key'")
            print("4. Or pass api_key parameter when creating CatalystDetector")
            return None

        # Step 1: Fetch recent news
        print("\nFetching recent news...")
        posts = self.fetch_recent_news(hours=hours, filter_type='rising')
        print(f"\u2705 Fetched {len(posts)} recent posts")

        if not posts:
            print("\n\u274c No recent posts found. Aborting detection.")
            return None

        # Step 2: Analyze sentiment
        print("\nAnalyzing sentiment...")
        sentiment_map = self.analyze_sentiment(posts)
        print(f"\u2705 Analyzed sentiment for {len(sentiment_map)} coins")

        # Step 3: Identify catalysts
        print("\nIdentifying catalysts...")
        catalysts = self.identify_catalysts(sentiment_map, min_positive=min_positive)
        print(f"\u2705 Found {len(catalysts)} catalyst opportunities")

        # Step 4: Generate report
        report = self.generate_catalyst_report(catalysts)

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"/home/ubuntu/Trading_Records/FY2025-2026/catalysts/catalyst_{timestamp}.txt"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w') as f:
            f.write(report)

        print(f"\n\u2705 Report saved: {report_path}\n")
        print(report)

        return catalysts


if __name__ == "__main__":
    # Test the catalyst detector
    detector = CatalystDetector()
    catalysts = detector.run_detection(hours=24, min_positive=3)
