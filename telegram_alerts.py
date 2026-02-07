#!/usr/bin/env python3
"""
TELEGRAM ALERTS V1.0
Instant alert system for trading opportunities and updates

Author: Manus AI
Date: January 30, 2026
"""

import os
import asyncio
from telegram import Bot
from telegram.error import TelegramError


class TelegramAlerts:
    """
    Telegram alert system for instant notifications

    Setup Instructions:
    1. Create a Telegram bot:
       - Open Telegram and search for @BotFather
       - Send /newbot and follow instructions
       - Copy the API token

    2. Get your chat ID:
       - Send a message to your bot
       - Visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
       - Copy your chat ID from the response

    3. Set environment variables:
       export TELEGRAM_BOT_TOKEN='your_bot_token'
       export TELEGRAM_CHAT_ID='your_chat_id'
    """

    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')

        if not self.bot_token or not self.chat_id:
            print("\u26a0 WARNING: Telegram not configured!")
            print("  Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
            print("  See setup instructions in telegram_alerts.py")
            self.bot = None
        else:
            self.bot = Bot(token=self.bot_token)

    async def send_message_async(self, message):
        """Send message asynchronously"""
        if not self.bot:
            print("\u274c Cannot send message: Telegram not configured")
            return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            return True
        except TelegramError as e:
            print(f"\u274c Telegram error: {e}")
            return False
        except Exception as e:
            print(f"\u274c Error sending message: {e}")
            return False

    def send_message(self, message):
        """Send message synchronously"""
        if not self.bot:
            print("\u274c Cannot send message: Telegram not configured")
            return False

        try:
            # Run async function in sync context
            # Create a fresh bot instance each time to avoid event loop issues
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                bot = Bot(token=self.bot_token)
                result = loop.run_until_complete(
                    bot.send_message(
                        chat_id=self.chat_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                )
                return True
            finally:
                loop.close()
        except Exception as e:
            print(f"\u274c Error sending message: {e}")
            return False

    def alert_opportunities_found(self, count, top_opportunity=None):
        """Alert when new opportunities are found"""
        message = f"\U0001f3af *OPPORTUNITIES FOUND*\n\n"
        message += f"Found {count} qualified opportunities!\n\n"

        if top_opportunity:
            message += f"*Top Opportunity:*\n"
            message += f"\u2022 {top_opportunity['coin_name']} ({top_opportunity['symbol']})\n"
            message += f"\u2022 Score: {top_opportunity['total_score']}/160\n"
            message += f"\u2022 Price: ${top_opportunity['price']:.4f} AUD\n"
            message += f"\u2022 24h: {top_opportunity['change_24h']:+.2f}%\n"

        message += f"\nCheck scan report for full details."
        return self.send_message(message)

    def alert_catalyst_detected(self, count, top_catalyst=None):
        """Alert when fresh catalysts are detected"""
        message = f"\U0001f525 *FRESH CATALYSTS DETECTED*\n\n"
        message += f"Found {count} catalyst opportunities!\n\n"

        if top_catalyst:
            message += f"*Top Catalyst:*\n"
            message += f"\u2022 {top_catalyst['coin']}\n"
            message += f"\u2022 Strength: {top_catalyst['catalyst_strength']:.0%}\n"
            message += f"\u2022 Positive News: {top_catalyst['positive_count']}\n"

        message += f"\nCheck catalyst report for full details."
        return self.send_message(message)

    def alert_target_hit(self, coin_name, target_level, current_price, profit_pct):
        """Alert when T1/T2 target is hit"""
        message = f"\U0001f3af *TARGET HIT!*\n\n"
        message += f"*{coin_name}* hit {target_level}!\n\n"
        message += f"\u2022 Current Price: ${current_price:.4f} AUD\n"
        message += f"\u2022 Profit: {profit_pct:+.2f}%\n\n"
        message += f"Framework says: Exit {target_level} portion now."
        return self.send_message(message)

    def alert_stop_near(self, coin_name, current_price, stop_price, distance_pct):
        """Alert when price is near stop-loss"""
        message = f"\u26a0 *STOP-LOSS WARNING*\n\n"
        message += f"*{coin_name}* approaching stop-loss!\n\n"
        message += f"\u2022 Current: ${current_price:.4f} AUD\n"
        message += f"\u2022 Stop: ${stop_price:.4f} AUD\n"
        message += f"\u2022 Distance: {distance_pct:.1f}%\n\n"
        message += f"Monitor closely for potential exit."
        return self.send_message(message)

    def alert_regime_change(self, old_regime, new_regime, fng_value):
        """Alert when market regime changes significantly"""
        message = f"\U0001f4ca *MARKET REGIME CHANGE*\n\n"
        message += f"Regime shifted:\n"
        message += f"\u2022 From: {old_regime}\n"
        message += f"\u2022 To: {new_regime}\n"
        message += f"\u2022 F&G: {fng_value}\n\n"

        if new_regime == "BEAR":
            message += f"\u26a0 Trading restricted. Preserve capital."
        elif new_regime == "NEUTRAL":
            message += f"\u26a1 Selective trading allowed (95+ score)."
        else:  # BULL
            message += f"\U0001f680 Active trading mode (90+ score)."

        return self.send_message(message)

    def test_connection(self):
        """Test Telegram connection"""
        message = "\u2705 *Telegram Alerts Connected!*\n\n"
        message += "Trading bot is now online.\n"
        message += "You will receive alerts for:\n"
        message += "\u2022 New opportunities\n"
        message += "\u2022 Fresh catalysts\n"
        message += "\u2022 Target hits\n"
        message += "\u2022 Stop-loss warnings\n"
        message += "\u2022 Regime changes"
        return self.send_message(message)


if __name__ == "__main__":
    # Test the Telegram alerts
    print("=" * 80)
    print("TELEGRAM ALERTS TEST")
    print("=" * 80)

    alerts = TelegramAlerts()

    if alerts.bot:
        print("\nSending test message...")
        success = alerts.test_connection()
        if success:
            print("\u2705 Test message sent successfully!")
            print("Check your Telegram for the message.")
        else:
            print("\u274c Failed to send test message.")
    else:
        print("\n\u274c Telegram not configured.")
        print("\nSetup Instructions:")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Get your chat ID from https://api.telegram.org/bot<TOKEN>/getUpdates")
        print("3. Set environment variables:")
        print("   export TELEGRAM_BOT_TOKEN='your_token'")
        print("   export TELEGRAM_CHAT_ID='your_chat_id'")
        print("4. Run this script again to test")

    print("\n" + "=" * 80)
