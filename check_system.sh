#!/bin/bash
# System Status Check Script
# Quick command to check if everything is running

echo "================================================================================"
echo "🦅 APEX PREDATOR TRADING SYSTEM - STATUS CHECK"
echo "================================================================================"
echo "Time: $(TZ='Australia/Perth' date '+%A, %B %d, %Y @ %I:%M %p AWST')"
echo ""

# Check if bot is running
echo "📊 BOT STATUS:"
if ps aux | grep -q "[p]ython3 trading_bot.py"; then
    PID=$(ps aux | grep "[p]ython3 trading_bot.py" | awk '{print $2}')
    echo "  ✅ Trading bot is RUNNING (PID: $PID)"
else
    echo "  ❌ Trading bot is NOT running"
    echo "     To start: cd /home/ubuntu/Trading_Records/FY2025-2026 && ./start_trading_system.sh"
fi
echo ""

echo "🔑 API KEYS:"
if [ -n "$CRYPTOPANIC_API_KEY" ]; then
    echo "  ✅ CryptoPanic API: Configured"
else
    echo "  ❌ CryptoPanic API: NOT configured"
fi

if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    echo "  ✅ Telegram Bot: Configured"
else
    echo "  ❌ Telegram Bot: NOT configured"
fi
echo ""

echo "📁 RECENT ACTIVITY:"
echo "  Last scan: $(ls -t /home/ubuntu/Trading_Records/FY2025-2026/scans/*.txt 2>/dev/null | head -1 || echo 'No scans yet')"
echo "  Last catalyst: $(ls -t /home/ubuntu/Trading_Records/FY2025-2026/catalysts/*.txt 2>/dev/null | head -1 || echo 'No catalysts yet')"
echo ""

echo "📋 BOT LOG (last 10 lines):"
if [ -f /home/ubuntu/Trading_Records/FY2025-2026/bot.log ]; then
    tail -10 /home/ubuntu/Trading_Records/FY2025-2026/bot.log | sed 's/^/  /'
else
    echo "  No log file found"
fi
echo ""

echo "================================================================================"
echo "SCHEDULED TASKS:"
echo "  • Daily Market Scan: 8:00 AM AWST"
echo "  • Hourly Catalyst Detection: Every hour"
echo "  • Regime Monitoring: Every 6 hours"
echo "  • Position Monitoring: Every 6 hours"
echo "================================================================================"
