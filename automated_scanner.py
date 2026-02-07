#!/usr/bin/env python3
"""
AUTOMATED MARKET SCANNER V1.0
Daily cryptocurrency market scanner with top 250 coverage

Author: Manus AI
Date: January 30, 2026
"""

import requests
import json
from datetime import datetime
import time
import sys
import os

# Add the current directory to path to import striker_engine_v3
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from striker_engine_v3 import StrikerEngineV3

# Import pandas for isna check
import pandas as pd


class AutomatedScanner:
    """
    Automated market scanner that:
    1. Scans top 250 coins (vs old 100)
    2. Applies technical analysis (RSI/MACD/BB)
    3. Filters overbought assets (RSI >70)
    4. Scores with Striker Engine V3
    5. Identifies top opportunities
    """

    def __init__(self, top_n=250, min_score=95, check_regime=True):
        self.top_n = top_n
        self.min_score = min_score
        self.check_regime = check_regime
        self.base_url = "https://api.coingecko.com/api/v3"
        self.engine = StrikerEngineV3()

    def get_market_regime(self):
        """Get current market regime (BEAR/NEUTRAL/BULL)"""
        try:
            # Get Fear & Greed Index
            fng_response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
            fng_data = fng_response.json()
            fng_value = int(fng_data['data'][0]['value'])

            # Simple regime classification
            if fng_value < 35:
                regime = "BEAR"
                score = fng_value
            elif fng_value < 65:
                regime = "NEUTRAL"
                score = fng_value
            else:
                regime = "BULL"
                score = fng_value

            print(f"\nMarket Regime: {regime} (F&G: {fng_value})")
            return regime, fng_value
        except Exception as e:
            print(f"\n\u26a0 Could not fetch market regime: {e}")
            print("Proceeding with scan anyway...")
            return "UNKNOWN", None

    def fetch_top_coins(self):
        """Fetch top N coins by market cap"""
        print(f"Fetching top {self.top_n} coins...")
        coins = []
        per_page = 250
        pages = (self.top_n + per_page - 1) // per_page  # Ceiling division

        for page in range(1, pages + 1):
            try:
                url = f"{self.base_url}/coins/markets"
                params = {
                    'vs_currency': 'aud',
                    'order': 'market_cap_desc',
                    'per_page': per_page,
                    'page': page,
                    'sparkline': False,
                    'price_change_percentage': '24h,7d,30d'
                }
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                page_coins = response.json()
                coins.extend(page_coins)
                print(f"  Page {page}/{pages}: {len(page_coins)} coins fetched")
                time.sleep(1.5)  # Rate limiting
            except Exception as e:
                print(f"  Error fetching page {page}: {e}")
                continue

        # Limit to exactly top_n
        coins = coins[:self.top_n]
        print(f"\n\u2705 Total coins fetched: {len(coins)}")
        return coins

    # Stablecoins to exclude from scan results
    STABLECOINS = {
        'usdt', 'usdc', 'dai', 'busd', 'tusd', 'usdp', 'gusd', 'frax',
        'usdd', 'lusd', 'susd', 'eurs', 'usdx', 'usds', 'fdusd', 'pyusd',
        'eurc', 'usd1', 'usde', 'usdy', 'usdtb', 'cusd', 'usdr', 'usdj',
        'ustb', 'usdf', 'usd0', 'usda', 'ylds', 'ust', 'flexusd'
    }

    def apply_filters(self, coins):
        """
        Apply filters to remove unsuitable coins
        Filters:
        1. Stablecoin filter (exclude pegged assets)
        2. Overbought filter (RSI >70 from technical analysis)
        3. Extreme volatility filter (>50% 24h change)
        4. Low volume filter (volume/mcap < 0.01)
        """
        print(f"\nApplying filters to {len(coins)} coins...")
        filtered = []

        for coin in coins:
            # Filter 0: Stablecoin filter
            symbol = (coin.get('symbol', '') or '').lower()
            if symbol in self.STABLECOINS:
                print(f"  \u274c {coin['name']}: Stablecoin (excluded)")
                continue

            # Filter 1: Extreme volatility (likely pump & dump)
            change_24h = coin.get('price_change_percentage_24h', 0) or 0
            if abs(change_24h) > 50:
                print(f"  \u274c {coin['name']}: Extreme volatility ({change_24h:.1f}%)")
                continue

            # Filter 2: Low volume
            volume = coin.get('total_volume', 0) or 0
            market_cap = coin.get('market_cap', 1) or 1
            volume_ratio = volume / market_cap if market_cap > 0 else 0
            if volume_ratio < 0.01:
                print(f"  \u274c {coin['name']}: Low volume (V/MC: {volume_ratio:.4f})")
                continue

            # Filter 3: Overbought will be checked during scoring (RSI >70)
            # For now, use 24h change as proxy
            if change_24h > 30:
                print(f"  \u26a0 {coin['name']}: Likely overbought (+{change_24h:.1f}%)")
                # Don't skip yet, let technical analysis confirm

            filtered.append(coin)

        print(f"\n\u2705 Coins after filtering: {len(filtered)}")
        return filtered

    def score_opportunities(self, coins, limit=20):
        """
        Score coins using Striker Engine V3
        Returns top N opportunities
        """
        print(f"\nScoring top {limit} candidates...")
        scored_coins = []

        for i, coin in enumerate(coins[:limit], 1):
            try:
                print(f"\n[{i}/{limit}] Scoring {coin['name']}...")

                # Score with Striker Engine V3
                score, breakdown = self.engine.score_coin(coin)

                # Check if overbought (RSI >70)
                tech_indicators = breakdown.get('technical_indicators')
                if tech_indicators and not pd.isna(tech_indicators.get('rsi')):
                    rsi = tech_indicators['rsi']
                    if rsi > 70:
                        print(f"  \u26a0 OVERBOUGHT: RSI = {rsi:.1f} (skipping)")
                        continue

                scored_coins.append(breakdown)
                time.sleep(6)  # Rate limiting (6s to stay under CoinGecko free tier)
            except Exception as e:
                print(f"  \u274c Error scoring {coin['name']}: {e}")
                continue

        # Sort by score
        scored_coins.sort(key=lambda x: x['total_score'], reverse=True)
        return scored_coins

    def generate_report(self, opportunities, market_regime=None):
        """Generate scan report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S AWST")

        report = f"""
================================================================================
AUTOMATED MARKET SCAN REPORT
================================================================================
Scan Time: {timestamp}
Coins Scanned: {self.top_n}
Min Score Threshold: {self.min_score}/160
"""

        if market_regime:
            report += f"Market Regime: {market_regime}\n\n"

        report += f"================================================================================\n"
        report += f"TOP OPPORTUNITIES ({len(opportunities)} found)\n"
        report += f"================================================================================\n"

        for i, opp in enumerate(opportunities, 1):
            report += f"#{i}. {opp['coin_name']} ({opp['symbol']})\n"
            report += f"    Score: {opp['total_score']}/160\n"
            report += f"    Price: ${opp['price']:.4f} AUD\n"
            change_24h = opp.get('change_24h', 0) or 0
            change_7d = opp.get('change_7d', 0) or 0
            report += f"    24h: {change_24h:+.2f}% | 7d: {change_7d:+.2f}%\n"
            report += f"    Rank: #{opp['market_cap_rank']}\n"
            report += f"\n"
            report += f"    Breakdown:\n"
            report += f"      - Technical: {opp['technical_score']}/60\n"
            report += f"        {opp['technical_details']}\n"
            report += f"      - Fundamental: {opp['fundamental_score']}/40\n"
            report += f"        {opp['fundamental_details']}\n"
            report += f"      - Catalyst: {opp['catalyst_score']}/40\n"
            report += f"        {opp['catalyst_details']}\n"
            report += f"      - Narrative: {opp['narrative_score']}/20\n"
            report += f"        {opp['narrative_details']}\n"
            report += f"\n"

            # Technical indicators
            tech = opp.get('technical_indicators')
            if tech:
                report += f"    Technical Indicators:\n"
                if not pd.isna(tech.get('rsi')):
                    report += f"      - RSI: {tech['rsi']:.1f}\n"
                if not pd.isna(tech.get('macd_diff')):
                    report += f"      - MACD: {tech['macd_diff']:.2f}\n"
                if not pd.isna(tech.get('bb_position')):
                    report += f"      - BB Position: {tech['bb_position']:.2f}\n"

            report += f"\n{'='*40}\n\n"

        if len(opportunities) == 0:
            report += "No opportunities found meeting criteria.\n"
            report += "Consider lowering min_score threshold or waiting for better conditions.\n"

        report += f"================================================================================\n"
        report += "END OF REPORT\n"
        report += f"================================================================================\n"

        return report

    def run_scan(self):
        """Run complete scan"""
        print("=" * 80)
        print("AUTOMATED MARKET SCANNER V1.0")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S AWST')}")
        print(f"Coverage: Top {self.top_n} coins")
        print(f"Min Score: {self.min_score}/160")
        print("=" * 80)

        # Step 0: Check market regime (optional)
        regime = None
        fng_value = None
        if self.check_regime:
            regime, fng_value = self.get_market_regime()

            # Warn if BEAR market but continue
            if regime == "BEAR":
                print(f"\n\u26a0 WARNING: Market in BEAR regime (F&G: {fng_value})")
                print("Raising score threshold to 110+ for safety")
                self.min_score = max(self.min_score, 110)  # Raise threshold in bear market

        # Step 1: Fetch top coins
        coins = self.fetch_top_coins()
        if not coins:
            print("\n\u274c Failed to fetch coins. Aborting scan.")
            return None

        # Step 2: Apply filters
        filtered_coins = self.apply_filters(coins)
        if not filtered_coins:
            print("\n\u274c No coins passed filters. Aborting scan.")
            return None

        # Step 3: Score opportunities
        scored_opportunities = self.score_opportunities(filtered_coins, limit=20)

        # Step 4: Filter by min score
        qualified_opportunities = [
            opp for opp in scored_opportunities
            if opp['total_score'] >= self.min_score
        ]

        print(f"\n{'='*80}")
        print(f"SCAN COMPLETE")
        print(f"{'='*80}")
        print(f"Total scanned: {len(coins)}")
        print(f"After filters: {len(filtered_coins)}")
        print(f"Scored: {len(scored_opportunities)}")
        print(f"Qualified (>={self.min_score}): {len(qualified_opportunities)}")
        print(f"{'='*80}\n")

        # Step 5: Generate report
        report = self.generate_report(qualified_opportunities)

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"/home/ubuntu/Trading_Records/FY2025-2026/scans/scan_{timestamp}.txt"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w') as f:
            f.write(report)

        print(f"\u2705 Report saved: {report_path}\n")
        print(report)

        return qualified_opportunities


if __name__ == "__main__":
    scanner = AutomatedScanner(top_n=250, min_score=95)
    opportunities = scanner.run_scan()
