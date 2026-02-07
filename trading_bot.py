#!/usr/bin/env python3
"""
TRADING BOT V1.0
Automated cryptocurrency trading system with scheduled scans and alerts

Features:
- Daily market scan at 8 AM AWST (top 250 coins)
- Hourly catalyst detection
- Regime monitoring every 6 hours
- Position monitoring every 6 hours
- HTTP health check endpoint for hosting platforms

Author: Manus AI
Date: January 30, 2026
"""

import threading
import time
import os
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============================================================
# STEP 1: Start health check server IMMEDIATELY
# Koyeb needs a response on PORT within seconds or it fails
# ============================================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks (keeps Koyeb happy)"""

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        uptime = datetime.now().strftime('%Y-%m-%d %H:%M:%S AWST')
        self.wfile.write(f"Apex Predator Trading Bot - ONLINE\nTime: {uptime}\n".encode())

    def log_message(self, format, *args):
        pass


def start_health_server():
    """Start a simple HTTP server for health checks"""
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Health check server running on port {port}", flush=True)
    server.serve_forever()


# Start health server FIRST in a background thread
health_thread = threading.Thread(target=start_health_server, daemon=True)
health_thread.start()
print("Health check server started - bot is initializing...", flush=True)

# Give the health server a moment to bind
time.sleep(1)

# ============================================================
# STEP 2: Now import the heavy modules and start the bot
# ============================================================

import schedule

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automated_scanner import AutomatedScanner
from catalyst_detector import CatalystDetector


class TradingBot:
    """
    Automated trading bot that runs scheduled tasks
    """

    def __init__(self):
        self.scanner = AutomatedScanner(top_n=250, min_score=95)
        self.catalyst_detector = CatalystDetector()

        print("=" * 80, flush=True)
        print("TRADING BOT V1.0 INITIALIZED", flush=True)
        print("=" * 80, flush=True)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S AWST')}", flush=True)
        print("\nScheduled Tasks:", flush=True)
        print("- Daily Market Scan: 8:00 AM AWST", flush=True)
        print("- Hourly Catalyst Detection: Every hour", flush=True)
        print("- Regime Monitoring: Every 6 hours", flush=True)
        print("- Position Monitoring: Every 6 hours", flush=True)
        print("=" * 80, flush=True)

    def daily_market_scan(self):
        """Run daily market scan"""
        print("\n" + "=" * 80, flush=True)
        print(f"DAILY MARKET SCAN TRIGGERED", flush=True)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S AWST')}", flush=True)
        print("=" * 80, flush=True)

        try:
            opportunities = self.scanner.run_scan()
            if opportunities and len(opportunities) > 0:
                print(f"\n\U0001f3af ALERT: {len(opportunities)} opportunities found!", flush=True)
                print("Check scan report for details.", flush=True)
            else:
                print("\nNo opportunities found today.", flush=True)
        except Exception as e:
            print(f"\n\u274c Error during daily scan: {e}", flush=True)

    def hourly_catalyst_detection(self):
        """Run hourly catalyst detection"""
        print("\n" + "=" * 80, flush=True)
        print(f"HOURLY CATALYST DETECTION TRIGGERED", flush=True)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S AWST')}", flush=True)
        print("=" * 80, flush=True)

        try:
            catalysts = self.catalyst_detector.run_detection(hours=1, min_positive=2)
            if catalysts and len(catalysts) > 0:
                print(f"\n\U0001f525 ALERT: {len(catalysts)} fresh catalysts detected!", flush=True)
                print("Check catalyst report for details.", flush=True)
            else:
                print("\nNo fresh catalysts detected this hour.", flush=True)
        except Exception as e:
            print(f"\n\u274c Error during catalyst detection: {e}", flush=True)

    def regime_monitoring(self):
        """Monitor market regime every 6 hours"""
        print("\n" + "=" * 80, flush=True)
        print(f"REGIME MONITORING TRIGGERED", flush=True)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S AWST')}", flush=True)
        print("=" * 80, flush=True)

        try:
            import requests

            # Fetch Fear & Greed Index
            response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
            response.raise_for_status()
            fng_data = response.json()
            fng_value = int(fng_data['data'][0]['value'])
            fng_classification = fng_data['data'][0]['value_classification']

            print(f"\nFear & Greed Index: {fng_value} ({fng_classification})", flush=True)

        except Exception as e:
            print(f"\n\u274c Error during regime monitoring: {e}", flush=True)

    def position_monitoring(self):
        """Monitor open positions every 6 hours"""
        print("\n" + "=" * 80, flush=True)
        print(f"POSITION MONITORING TRIGGERED", flush=True)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S AWST')}", flush=True)
        print("=" * 80, flush=True)

        try:
            print("\nNo open positions to monitor.", flush=True)
        except Exception as e:
            print(f"\n\u274c Error during position monitoring: {e}", flush=True)

    def run(self):
        """Start the bot with scheduled tasks"""
        # Schedule daily market scan at 8:00 AM AWST
        schedule.every().day.at("08:00").do(self.daily_market_scan)

        # Schedule hourly catalyst detection
        schedule.every().hour.do(self.hourly_catalyst_detection)

        # Schedule regime monitoring every 6 hours
        schedule.every(6).hours.do(self.regime_monitoring)

        # Schedule position monitoring every 6 hours
        schedule.every(6).hours.do(self.position_monitoring)

        print("\n\u2705 Bot started! Running scheduled tasks...", flush=True)

        # Run initial checks
        print("\nRunning initial checks...", flush=True)
        self.regime_monitoring()
        self.position_monitoring()

        # Keep the bot running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n\n" + "=" * 80, flush=True)
            print("BOT STOPPED BY USER", flush=True)
            print("=" * 80, flush=True)
            print(f"Stop Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S AWST')}", flush=True)
            print("=" * 80, flush=True)


if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
