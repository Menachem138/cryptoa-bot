import os
import ccxt
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
import time
from sentiment_analyzer import SentimentAnalyzer
from technical_analyzer import TechnicalAnalyzer

class CryptoAnalyzer:
    def __init__(self):
        load_dotenv()
        self.exchange = ccxt.binance()
        self.min_market_cap = 1000000  # $1M minimum market cap
        self.min_daily_volume = 100000  # $100K minimum daily volume
        self.sentiment_analyzer = SentimentAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        
    def get_promising_coins(self):
        """Identify promising early-stage cryptocurrencies."""
        try:
            # Get all markets from Binance
            markets = self.exchange.load_markets()
            promising_coins = []
            
            for symbol in markets:
                if symbol.endswith('/USDT'):
                    try:
                        # Get detailed market data
                        ticker = self.exchange.fetch_ticker(symbol)
                        
                        # Basic filtering
                        if (ticker['quoteVolume'] > self.min_daily_volume):
                            coin_analysis = self.analyze_coin(symbol, ticker)
                            if coin_analysis:
                                promising_coins.append(coin_analysis)
                    
                    except Exception as e:
                        print(f"Error analyzing {symbol}: {str(e)}")
                        continue
            
            # Sort by combined score
            if promising_coins:
                promising_coins.sort(key=lambda x: x['combined_score'], reverse=True)
            
            return promising_coins
        
        except Exception as e:
            print(f"Error in get_promising_coins: {str(e)}")
            return []

    def analyze_coin(self, symbol, ticker):
        """Perform comprehensive analysis on a specific coin."""
        try:
            # Get historical data
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1d', limit=30)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Technical Analysis
            technical_analysis = self.technical_analyzer.analyze_technical_indicators(df)
            
            # Sentiment Analysis
            base_symbol = symbol.split('/')[0]
            sentiment_analysis = self.sentiment_analyzer.analyze_social_sentiment(base_symbol)
            
            # Calculate basic metrics
            price_change_24h = ((ticker['last'] - ticker['open']) / ticker['open']) * 100
            volume_change_24h = ticker['quoteVolume'] - df['volume'].mean()
            volatility = df['close'].std() / df['close'].mean() * 100
            
            # Risk assessment
            risk_score = self.calculate_risk_score(volatility, volume_change_24h, price_change_24h,
                                                 technical_analysis, sentiment_analysis)
            
            # Potential assessment
            potential_score = self.assess_potential(df, ticker, technical_analysis, sentiment_analysis)
            
            # Calculate combined score
            combined_score = self.calculate_combined_score(risk_score, potential_score,
                                                         technical_analysis, sentiment_analysis)
            
            if combined_score >= 6:  # Adjustable threshold
                return {
                    'symbol': symbol,
                    'current_price': ticker['last'],
                    'price_change_24h': price_change_24h,
                    'daily_volume': ticker['quoteVolume'],
                    'risk_score': risk_score,
                    'potential_score': potential_score,
                    'combined_score': combined_score,
                    'technical_analysis': technical_analysis,
                    'sentiment_analysis': sentiment_analysis,
                    'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'recommendation': self.generate_recommendation(risk_score, potential_score,
                                                                technical_analysis, sentiment_analysis)
                }
            
            return None
            
        except Exception as e:
            print(f"Error in analyze_coin for {symbol}: {str(e)}")
            return None

    def calculate_risk_score(self, volatility, volume_change, price_change, technical_analysis, sentiment_analysis):
        """Calculate comprehensive risk score (1-10, where 10 is highest risk)."""
        risk_score = 0
        
        # Volatility contribution (0-3 points)
        if volatility > 50:
            risk_score += 3
        elif volatility > 30:
            risk_score += 2
        elif volatility > 10:
            risk_score += 1
            
        # Volume stability (0-2 points)
        if volume_change < -50000:
            risk_score += 2
        elif volume_change < -20000:
            risk_score += 1
            
        # Price stability (0-2 points)
        if abs(price_change) > 30:
            risk_score += 2
        elif abs(price_change) > 15:
            risk_score += 1
            
        # Technical indicators contribution (0-2 points)
        if technical_analysis:
            if technical_analysis['analysis']['volatility']['bb_position'] in ['upper', 'lower']:
                risk_score += 1
            if technical_analysis['analysis']['momentum']['rsi_condition'] in ['overbought', 'oversold']:
                risk_score += 1
                
        # Sentiment contribution (0-1 point)
        if sentiment_analysis and sentiment_analysis['combined_score'] < -0.5:
            risk_score += 1
            
        return risk_score

    def assess_potential(self, df, ticker, technical_analysis, sentiment_analysis):
        """Assess potential score (1-10, where 10 is highest potential)."""
        potential_score = 5  # Start with neutral score
        
        # Technical analysis contribution
        if technical_analysis:
            # Trend strength
            if all(technical_analysis['analysis']['trend'][key] == 'bullish' for key in ['macd_trend', 'sma_trend']):
                potential_score += 1
            
            # Volume confirmation
            if technical_analysis['analysis']['volume']['volume_trend'] == 'increasing':
                potential_score += 1
                
            # Price momentum
            if technical_analysis['analysis']['momentum']['rsi_value'] > 50:
                potential_score += 0.5
                
        # Sentiment contribution
        if sentiment_analysis and sentiment_analysis['combined_score'] > 0:
            sentiment_boost = min(2, sentiment_analysis['combined_score'] * 2)
            potential_score += sentiment_boost
            
        # Market performance
        price_trend = df['close'].pct_change().mean() * 100
        if price_trend > 5:
            potential_score += 1
        elif price_trend > 2:
            potential_score += 0.5
            
        # Ensure score stays within bounds
        return max(1, min(10, potential_score))

    def calculate_combined_score(self, risk_score, potential_score, technical_analysis, sentiment_analysis):
        """Calculate overall investment score considering all factors."""
        # Base score from risk and potential
        combined_score = (potential_score * 0.4) + ((10 - risk_score) * 0.3)
        
        # Technical analysis contribution (20%)
        if technical_analysis:
            technical_score = technical_analysis['technical_score']
            combined_score += (technical_score * 0.2)
            
        # Sentiment analysis contribution (10%)
        if sentiment_analysis and sentiment_analysis['combined_score'] is not None:
            sentiment_score = ((sentiment_analysis['combined_score'] + 1) / 2) * 10  # Convert -1 to 1 range to 0-10
            combined_score += (sentiment_score * 0.1)
            
        return round(combined_score, 2)

    def generate_recommendation(self, risk_score, potential_score, technical_analysis, sentiment_analysis):
        """Generate detailed investment recommendation."""
        recommendation = []
        
        # Overall recommendation
        combined_score = self.calculate_combined_score(risk_score, potential_score,
                                                     technical_analysis, sentiment_analysis)
        
        if combined_score >= 8:
            recommendation.append("Strong Buy - Exceptional opportunity with high potential and managed risk")
        elif combined_score >= 7:
            recommendation.append("Buy - Favorable conditions for investment")
        elif combined_score >= 6:
            recommendation.append("Consider - Positive indicators with some caution")
        else:
            recommendation.append("Hold - Monitor for better entry points")
            
        # Technical Analysis insights
        if technical_analysis:
            for signal in technical_analysis['signals']:
                recommendation.append(f"Technical: {signal}")
                
        # Risk Assessment
        risk_level = "Low" if risk_score <= 3 else "Moderate" if risk_score <= 6 else "High"
        recommendation.append(f"Risk Level: {risk_level} (Score: {risk_score}/10)")
        
        # Potential Assessment
        potential_level = "High" if potential_score >= 7 else "Moderate" if potential_score >= 5 else "Low"
        recommendation.append(f"Potential: {potential_level} (Score: {potential_score}/10)")
        
        # Sentiment insights
        if sentiment_analysis:
            recommendation.append(f"Market Sentiment: {self.sentiment_analyzer.get_sentiment_summary(sentiment_analysis)}")
            
        return "\n".join(recommendation)

if __name__ == "__main__":
    analyzer = CryptoAnalyzer()
    promising_coins = analyzer.get_promising_coins()
    
    print("\nCrypto Investment Analysis Report")
    print("=" * 50)
    
    if promising_coins:
        for coin in promising_coins:
            print(f"\nSymbol: {coin['symbol']}")
            print(f"Current Price: ${coin['current_price']:.4f}")
            print(f"24h Price Change: {coin['price_change_24h']:.2f}%")
            print(f"Daily Volume: ${coin['daily_volume']:,.2f}")
            print(f"Combined Score: {coin['combined_score']}/10")
            print(f"Risk Score: {coin['risk_score']}/10")
            print(f"Potential Score: {coin['potential_score']}/10")
            print("\nRecommendation:")
            print(coin['recommendation'])
            print("-" * 50)
    else:
        print("No promising investment opportunities found at this time.")
