#!/usr/bin/env python3
"""
STRIKER ENGINE V3.0
Advanced Cryptocurrency Opportunity Scoring System
With Technical Analysis Integration (RSI, MACD, Bollinger Bands)

Author: Manus AI
Date: January 30, 2026
"""

import requests
import json
from datetime import datetime, timedelta
import time
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands
import pandas as pd


class StrikerEngineV3:
    """
    Striker Engine V3 - Advanced opportunity scoring with technical analysis

    Scoring System (160 points total):
    - Technical Analysis: 60 points (NEW)
    - Fundamental Analysis: 40 points
    - Catalyst Analysis: 40 points
    - Narrative Analysis: 20 points
    """

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"

    def fetch_historical_prices(self, coin_id, days=30):
        """Fetch historical price data for technical analysis"""
        try:
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'aud',
                'days': days
                # No interval specified = daily data (free tier compatible)
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Convert to pandas DataFrame
            prices = data['prices']
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            return df
        except Exception as e:
            print(f"  Error fetching historical data for {coin_id}: {e}")
            return None

    def calculate_technical_indicators(self, df):
        """Calculate RSI, MACD, and Bollinger Bands"""
        if df is None or len(df) < 26:  # Need at least 26 periods for MACD
            return None

        try:
            # RSI (14-period)
            rsi_indicator = RSIIndicator(close=df['price'], window=14)
            rsi = rsi_indicator.rsi().iloc[-1]

            # MACD
            macd_indicator = MACD(close=df['price'])
            macd = macd_indicator.macd().iloc[-1]
            macd_signal = macd_indicator.macd_signal().iloc[-1]
            macd_diff = macd_indicator.macd_diff().iloc[-1]

            # Bollinger Bands
            bb_indicator = BollingerBands(close=df['price'])
            bb_upper = bb_indicator.bollinger_hband().iloc[-1]
            bb_lower = bb_indicator.bollinger_lband().iloc[-1]
            bb_middle = bb_indicator.bollinger_mavg().iloc[-1]
            current_price = df['price'].iloc[-1]

            # Calculate BB position (0 = lower band, 0.5 = middle, 1 = upper band)
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5

            return {
                'rsi': rsi,
                'macd': macd,
                'macd_signal': macd_signal,
                'macd_diff': macd_diff,
                'bb_upper': bb_upper,
                'bb_lower': bb_lower,
                'bb_middle': bb_middle,
                'bb_position': bb_position,
                'current_price': current_price
            }
        except Exception as e:
            print(f"  Error calculating technical indicators: {e}")
            return None

    def score_technical(self, coin_data, technical_indicators):
        """
        Score technical analysis (60 points max)

        Breakdown:
        - RSI Score: 20 points (optimal 30-70, bonus for oversold 20-30)
        - MACD Score: 20 points (bullish crossover, momentum)
        - Bollinger Bands: 20 points (position, squeeze, breakout potential)
        """
        if technical_indicators is None:
            return 30, "No technical data available"  # Neutral score

        score = 0
        details = []

        # RSI Scoring (20 points)
        rsi = technical_indicators['rsi']
        if pd.isna(rsi):
            rsi_score = 10
            details.append(f"RSI: N/A (neutral: +10)")
        elif rsi < 20:
            rsi_score = 5  # Extremely oversold - risky
            details.append(f"RSI: {rsi:.1f} (extremely oversold: +5)")
        elif 20 <= rsi < 30:
            rsi_score = 18  # Oversold - good entry
            details.append(f"RSI: {rsi:.1f} (oversold, good entry: +18)")
        elif 30 <= rsi < 40:
            rsi_score = 20  # Optimal buy zone
            details.append(f"RSI: {rsi:.1f} (optimal buy zone: +20)")
        elif 40 <= rsi < 60:
            rsi_score = 15  # Neutral
            details.append(f"RSI: {rsi:.1f} (neutral: +15)")
        elif 60 <= rsi < 70:
            rsi_score = 10  # Getting overbought
            details.append(f"RSI: {rsi:.1f} (getting overbought: +10)")
        elif 70 <= rsi < 80:
            rsi_score = 3  # Overbought - SKIP
            details.append(f"RSI: {rsi:.1f} (overbought - SKIP: +3)")
        else:  # >= 80
            rsi_score = 0  # Extremely overbought - AVOID
            details.append(f"RSI: {rsi:.1f} (extremely overbought - AVOID: +0)")

        score += rsi_score

        # MACD Scoring (20 points)
        macd_diff = technical_indicators['macd_diff']
        if pd.isna(macd_diff):
            macd_score = 10
            details.append(f"MACD: N/A (neutral: +10)")
        elif macd_diff > 0:
            # Bullish - MACD above signal
            if macd_diff > 5:
                macd_score = 20  # Strong bullish momentum
                details.append(f"MACD: +{macd_diff:.2f} (strong bullish: +20)")
            elif macd_diff > 2:
                macd_score = 17  # Good bullish momentum
                details.append(f"MACD: +{macd_diff:.2f} (bullish: +17)")
            else:
                macd_score = 14  # Weak bullish
                details.append(f"MACD: +{macd_diff:.2f} (weak bullish: +14)")
        else:
            # Bearish - MACD below signal
            if macd_diff < -5:
                macd_score = 5  # Strong bearish - avoid
                details.append(f"MACD: {macd_diff:.2f} (strong bearish: +5)")
            elif macd_diff < -2:
                macd_score = 8  # Bearish
                details.append(f"MACD: {macd_diff:.2f} (bearish: +8)")
            else:
                macd_score = 11  # Weak bearish - potential reversal
                details.append(f"MACD: {macd_diff:.2f} (weak bearish: +11)")

        score += macd_score

        # Bollinger Bands Scoring (20 points)
        bb_position = technical_indicators['bb_position']
        if pd.isna(bb_position):
            bb_score = 10
            details.append(f"BB: N/A (neutral: +10)")
        elif bb_position < 0.2:
            bb_score = 18  # Near lower band - good entry
            details.append(f"BB: {bb_position:.2f} (near lower band, good entry: +18)")
        elif 0.2 <= bb_position < 0.4:
            bb_score = 20  # Optimal buy zone
            details.append(f"BB: {bb_position:.2f} (optimal buy zone: +20)")
        elif 0.4 <= bb_position < 0.6:
            bb_score = 15  # Middle zone - neutral
            details.append(f"BB: {bb_position:.2f} (middle zone: +15)")
        elif 0.6 <= bb_position < 0.8:
            bb_score = 10  # Upper zone - caution
            details.append(f"BB: {bb_position:.2f} (upper zone: +10)")
        elif 0.8 <= bb_position <= 1.0:
            bb_score = 5  # Near upper band - overbought
            details.append(f"BB: {bb_position:.2f} (near upper band, overbought: +5)")
        else:
            bb_score = 3  # Outside bands - extreme
            details.append(f"BB: {bb_position:.2f} (outside bands: +3)")

        score += bb_score

        return score, " | ".join(details)

    def score_fundamental(self, coin_data):
        """
        Score fundamental metrics (40 points max)

        Breakdown:
        - Price momentum: 15 points
        - Volume: 10 points
        - Market cap rank: 10 points
        - Volatility: 5 points
        """
        score = 0
        details = []

        # Price momentum (15 points)
        change_24h = coin_data.get('price_change_percentage_24h', 0) or 0
        change_7d = coin_data.get('price_change_percentage_7d', 0) or 0

        if change_24h > 20:
            momentum_score = 3  # Too hot, likely overbought
            details.append(f"24h: +{change_24h:.1f}% (too hot: +3)")
        elif 10 < change_24h <= 20:
            momentum_score = 10  # Strong but not extreme
            details.append(f"24h: +{change_24h:.1f}% (strong: +10)")
        elif 5 < change_24h <= 10:
            momentum_score = 15  # Optimal momentum
            details.append(f"24h: +{change_24h:.1f}% (optimal: +15)")
        elif 0 < change_24h <= 5:
            momentum_score = 12  # Positive but weak
            details.append(f"24h: +{change_24h:.1f}% (weak positive: +12)")
        elif -5 <= change_24h <= 0:
            momentum_score = 8  # Slight decline
            details.append(f"24h: {change_24h:.1f}% (slight decline: +8)")
        else:
            momentum_score = 5  # Declining
            details.append(f"24h: {change_24h:.1f}% (declining: +5)")

        score += momentum_score

        # Volume (10 points)
        volume = coin_data.get('total_volume', 0) or 0
        market_cap = coin_data.get('market_cap', 1) or 1
        volume_to_mcap = volume / market_cap if market_cap > 0 else 0

        if volume_to_mcap > 0.5:
            volume_score = 10  # Very high volume
            details.append(f"Vol/MCap: {volume_to_mcap:.2f} (very high: +10)")
        elif volume_to_mcap > 0.2:
            volume_score = 8  # High volume
            details.append(f"Vol/MCap: {volume_to_mcap:.2f} (high: +8)")
        elif volume_to_mcap > 0.1:
            volume_score = 6  # Good volume
            details.append(f"Vol/MCap: {volume_to_mcap:.2f} (good: +6)")
        else:
            volume_score = 3  # Low volume
            details.append(f"Vol/MCap: {volume_to_mcap:.2f} (low: +3)")

        score += volume_score

        # Market cap rank (10 points)
        rank = coin_data.get('market_cap_rank', 999) or 999

        if rank <= 50:
            rank_score = 7  # Large cap - safer but less upside
            details.append(f"Rank: #{rank} (large cap: +7)")
        elif rank <= 100:
            rank_score = 10  # Mid cap - good balance
            details.append(f"Rank: #{rank} (mid cap: +10)")
        elif rank <= 250:
            rank_score = 8  # Small cap - higher risk/reward
            details.append(f"Rank: #{rank} (small cap: +8)")
        else:
            rank_score = 5  # Micro cap - very high risk
            details.append(f"Rank: #{rank} (micro cap: +5)")

        score += rank_score

        # Volatility (5 points)
        # Using 7d change as proxy for volatility
        if abs(change_7d) > 50:
            volatility_score = 1  # Very volatile
            details.append(f"7d: {change_7d:+.1f}% (very volatile: +1)")
        elif abs(change_7d) > 25:
            volatility_score = 3  # Volatile
            details.append(f"7d: {change_7d:+.1f}% (volatile: +3)")
        else:
            volatility_score = 5  # Stable
            details.append(f"7d: {change_7d:+.1f}% (stable: +5)")

        score += volatility_score

        return score, " | ".join(details)

    def score_catalyst(self, coin_data):
        """
        Score catalyst potential (40 points max)
        This is a placeholder - real catalyst detection is done in catalyst_detector.py
        Here we just check for recent positive news
        """
        # Placeholder - real logic in catalyst_detector.py
        # For now, give a neutral score
        return 20, "Catalyst detection requires separate module"

    def score_narrative(self, coin_data):
        """
        Score narrative strength (20 points max)
        This is a placeholder - real narrative analysis is complex
        Here we just check for sector performance
        """
        # Placeholder - real logic in future versions
        # For now, give a neutral score
        return 10, "Narrative analysis requires sector data"

    def score_coin(self, coin_data):
        """
        Score a single coin across all categories
        """
        total_score = 0
        breakdown = {
            'coin_name': coin_data.get('name'),
            'symbol': coin_data.get('symbol', '').upper(),
            'price': coin_data.get('current_price'),
            'market_cap_rank': coin_data.get('market_cap_rank'),
            'change_24h': coin_data.get('price_change_percentage_24h'),
            'change_7d': coin_data.get('price_change_percentage_7d'),
        }

        # Technical Analysis
        df = self.fetch_historical_prices(coin_data['id'])
        technical_indicators = self.calculate_technical_indicators(df)
        technical_score, technical_details = self.score_technical(coin_data, technical_indicators)
        total_score += technical_score
        breakdown['technical_score'] = technical_score
        breakdown['technical_details'] = technical_details
        breakdown['technical_indicators'] = technical_indicators

        # Fundamental Analysis
        fundamental_score, fundamental_details = self.score_fundamental(coin_data)
        total_score += fundamental_score
        breakdown['fundamental_score'] = fundamental_score
        breakdown['fundamental_details'] = fundamental_details

        # Catalyst Analysis (placeholder)
        catalyst_score, catalyst_details = self.score_catalyst(coin_data)
        total_score += catalyst_score
        breakdown['catalyst_score'] = catalyst_score
        breakdown['catalyst_details'] = catalyst_details

        # Narrative Analysis (placeholder)
        narrative_score, narrative_details = self.score_narrative(coin_data)
        total_score += narrative_score
        breakdown['narrative_score'] = narrative_score
        breakdown['narrative_details'] = narrative_details

        breakdown['total_score'] = total_score

        print(f"  - Technical: {technical_score}/60")
        print(f"  - Fundamental: {fundamental_score}/40")
        print(f"  - Catalyst: {catalyst_score}/40")
        print(f"  - Narrative: {narrative_score}/20")
        print(f"  - TOTAL: {total_score}/160")

        return total_score, breakdown
