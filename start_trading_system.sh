#!/bin/bash
# Start the Apex Predator Trading System

cd /home/ubuntu/Trading_Records/FY2025-2026

# Check if bot is already running
if ps aux | grep -q "[p]ython3 trading_bot.py"; then
    echo "❌ Trading bot is already running."
    exit 1
fi

# Start the bot in the background
python3 -u trading_bot.py > bot.log 2>&1 &

# Save the PID
echo $! > bot.pid

# Wait a moment for initialization
sleep 5

# Check if it started successfully
if ps -p $(cat bot.pid) > /dev/null; then
    echo "✅ Trading bot started successfully (PID: $(cat bot.pid))"
    echo "   View log: tail -f bot.log"
else
    echo "❌ Failed to start trading bot."
    echo "   Check bot.log for errors."
fi
