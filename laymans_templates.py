#!/usr/bin/env python3
"""
LAYMAN'S TEMPLATES V1.0
Templates for presenting trading data in simple, easy-to-understand language

Author: Manus AI
Date: January 30, 2026
"""


class LaymansTemplates:
    """
    Templates that translate technical trading data into plain English
    using analogies and simple explanations.
    """

    @staticmethod
    def explain_rsi(rsi_value):
        """Explain RSI in layman's terms"""
        if rsi_value < 20:
            return f"RSI is {rsi_value:.0f} - Think of this like a store having a massive clearance sale. " \
                   f"The price has dropped so much that it might be a bargain, but there could be a reason " \
                   f"everyone's selling. Proceed with caution."
        elif rsi_value < 30:
            return f"RSI is {rsi_value:.0f} - This is like finding a quality item on sale. " \
                   f"The price has come down enough that it could be a good entry point."
        elif rsi_value < 40:
            return f"RSI is {rsi_value:.0f} - This is the sweet spot, like buying during a seasonal sale. " \
                   f"Not too cheap (suspicious) and not too expensive."
        elif rsi_value < 60:
            return f"RSI is {rsi_value:.0f} - Fair price territory. Like buying at regular retail price. " \
                   f"Nothing special, but nothing wrong either."
        elif rsi_value < 70:
            return f"RSI is {rsi_value:.0f} - Getting a bit pricey. Like buying something that's trending " \
                   f"and the price is starting to go up."
        elif rsi_value < 80:
            return f"RSI is {rsi_value:.0f} - Overpriced territory. Like buying a hot item at a premium. " \
                   f"Most of the easy gains are probably gone."
        else:
            return f"RSI is {rsi_value:.0f} - Extremely overpriced. Like buying concert tickets from a scalper. " \
                   f"The smart money has already taken profits."

    @staticmethod
    def explain_score(total_score):
        """Explain the total score in layman's terms"""
        if total_score >= 130:
            return f"Score: {total_score}/160 - EXCELLENT. This is like finding a diamond in the rough. " \
                   f"Multiple indicators are all pointing in the same direction."
        elif total_score >= 110:
            return f"Score: {total_score}/160 - VERY GOOD. Like a restaurant with 4.5 stars. " \
                   f"Strong opportunity with minor concerns."
        elif total_score >= 95:
            return f"Score: {total_score}/160 - GOOD. Like a solid 4-star review. " \
                   f"Worth considering but do your own research too."
        elif total_score >= 80:
            return f"Score: {total_score}/160 - AVERAGE. Like a 3-star hotel. " \
                   f"It'll do the job but nothing to write home about."
        else:
            return f"Score: {total_score}/160 - BELOW AVERAGE. Like a 2-star review. " \
                   f"Probably best to look elsewhere."

    @staticmethod
    def explain_regime(regime, fng_value):
        """Explain market regime in layman's terms"""
        if regime == "BEAR":
            return f"Market Regime: BEAR (Fear & Greed: {fng_value})\n" \
                   f"Think of this like winter for the market. People are scared and selling. " \
                   f"Like a housing market crash - prices are falling and everyone's nervous. " \
                   f"Be extra careful and only buy the absolute best opportunities."
        elif regime == "NEUTRAL":
            return f"Market Regime: NEUTRAL (Fear & Greed: {fng_value})\n" \
                   f"Think of this like autumn/spring for the market. Neither hot nor cold. " \
                   f"Like a stable housing market - normal activity, normal prices. " \
                   f"Good time for selective buying."
        else:
            return f"Market Regime: BULL (Fear & Greed: {fng_value})\n" \
                   f"Think of this like summer for the market. Everyone's excited and buying. " \
                   f"Like a booming housing market - prices going up, lots of activity. " \
                   f"Good time to trade but don't get greedy."


if __name__ == "__main__":
    templates = LaymansTemplates()
    print(templates.explain_rsi(35))
    print()
    print(templates.explain_score(105))
    print()
    print(templates.explain_regime("NEUTRAL", 52))
