# Cryptoa Bot

An advanced AI-powered cryptocurrency analysis and investment recommendation system.

## Features

- **Cryptocurrency Analysis**
  - Early-stage cryptocurrency identification
  - Market data and trends analysis
  - Risk assessment and potential scoring
  - Investment recommendations

- **Technical Analysis**
  - MACD (Moving Average Convergence Divergence)
  - RSI (Relative Strength Index)
  - Bollinger Bands
  - Moving Averages
  - Volume trend analysis

- **Sentiment Analysis**
  - Social media sentiment tracking
  - Twitter and Reddit analysis
  - Community perception evaluation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Menachem138/cryptoa-bot.git
cd cryptoa-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env` file:
```
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
```

## Usage

Run the main analysis:
```bash
python crypto_analyzer.py
```

## Project Structure

- `crypto_analyzer.py`: Core analysis logic
- `technical_analyzer.py`: Technical indicators and analysis
- `sentiment_analyzer.py`: Social media sentiment analysis
- `requirements.txt`: Project dependencies
- `.env`: Configuration and API keys
- `Dockerfile`: Container configuration
- `render.yaml`: Deployment configuration

## Deployment

The project is configured for deployment on Render.com using Docker containerization.

## Warning

Cryptocurrency investments carry high risk. This tool is for research purposes only. Always do your own research before making any investment decisions.
