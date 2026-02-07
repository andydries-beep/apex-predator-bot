#!/usr/bin/env python3
"""
LEARNING SYSTEM V1.0
Trade-specific learning journal and improvement tracking

Author: Manus AI
Date: January 30, 2026
"""

import os
import json
from datetime import datetime


class LearningSystem:
    """
    Learning system that:
    1. Creates trade-specific learning journals
    2. Tracks lessons learned from each trade
    3. Identifies patterns in wins and losses
    4. Generates improvement suggestions
    """

    def __init__(self):
        self.journal_dir = "/home/ubuntu/Trading_Records/FY2025-2026/learning_journal"
        os.makedirs(self.journal_dir, exist_ok=True)

    def create_journal_entry(self, trade_data):
        """Create a learning journal entry for a trade"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        coin = trade_data.get('coin', 'UNKNOWN')
        
        entry = f"""# Learning Journal: {coin}
## Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S AWST')}

### Trade Summary
- **Coin:** {coin}
- **Entry Price:** ${trade_data.get('entry_price', 'N/A')} AUD
- **Exit Price:** ${trade_data.get('exit_price', 'N/A')} AUD
- **P/L:** {trade_data.get('pnl', 'N/A')}%
- **Score at Entry:** {trade_data.get('score', 'N/A')}/160

### What Went Right
- [To be filled]

### What Went Wrong
- [To be filled]

### Lessons Learned
- [To be filled]

### Action Items
- [To be filled]

### Emotional State
- Before trade: [To be filled]
- During trade: [To be filled]
- After trade: [To be filled]

---
*Every trade is a lesson, win or lose.*
"""
        
        filepath = os.path.join(self.journal_dir, f"journal_{coin}_{timestamp}.md")
        with open(filepath, 'w') as f:
            f.write(entry)
        
        print(f"\u2705 Learning journal created: {filepath}")
        return filepath


if __name__ == "__main__":
    system = LearningSystem()
    # Test with sample data
    sample_trade = {
        'coin': 'BTC',
        'entry_price': 150000,
        'exit_price': 155000,
        'pnl': 3.33,
        'score': 120
    }
    system.create_journal_entry(sample_trade)
