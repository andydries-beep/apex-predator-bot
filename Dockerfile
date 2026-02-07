FROM python:3.11-slim

# Set timezone to AWST
ENV TZ=Australia/Perth
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all bot files
COPY *.py .
COPY *.sh .
COPY *.md .

# Make shell scripts executable
RUN chmod +x *.sh

# Create necessary directories
RUN mkdir -p scans catalysts learning_journal reports

# Run the trading bot
CMD ["python3", "-u", "trading_bot.py"]
