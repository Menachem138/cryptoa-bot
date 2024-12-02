import pandas as pd
import numpy as np
from ta import add_all_ta_features
from ta.utils import dropna
from ta.volatility import BollingerBands
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator
from datetime import datetime, timedelta

class TechnicalAnalyzer:
    def __init__(self):
        self.indicators = {}
        
    def analyze_technical_indicators(self, df):
        """Perform comprehensive technical analysis on price data."""
        try:
            # Ensure we have OHLCV data
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                return None
                
            # Clean data
            df = dropna(df)
            
            # Calculate all technical indicators
            df = self._calculate_indicators(df)
            
            # Generate analysis
            analysis = self._analyze_indicators(df)
            
            return {
                'technical_score': self._calculate_technical_score(analysis),
                'analysis': analysis,
                'signals': self._generate_signals(analysis),
                'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error in technical analysis: {str(e)}")
            return None

    def _calculate_indicators(self, df):
        """Calculate various technical indicators."""
        try:
            # Trend Indicators
            macd = MACD(close=df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            
            # Momentum Indicators
            rsi = RSIIndicator(close=df['close'])
            df['rsi'] = rsi.rsi()
            
            # Volatility Indicators
            bb = BollingerBands(close=df['close'])
            df['bb_high'] = bb.bollinger_hband()
            df['bb_low'] = bb.bollinger_lband()
            df['bb_mid'] = bb.bollinger_mavg()
            
            # Volume Indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            
            # Price Action
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['sma_200'] = df['close'].rolling(window=200).mean()
            
            # Price changes
            df['price_change_24h'] = df['close'].pct_change(periods=1)
            df['price_change_7d'] = df['close'].pct_change(periods=7)
            
            return df
            
        except Exception as e:
            print(f"Error calculating indicators: {str(e)}")
            return df

    def _analyze_indicators(self, df):
        """Analyze the calculated indicators."""
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        analysis = {
            'trend': self._analyze_trend(df),
            'momentum': self._analyze_momentum(df),
            'volatility': self._analyze_volatility(df),
            'volume': self._analyze_volume(df),
            'price_action': self._analyze_price_action(df)
        }
        
        return analysis

    def _analyze_trend(self, df):
        """Analyze trend indicators."""
        latest = df.iloc[-1]
        
        trend_analysis = {
            'macd_trend': 'bullish' if latest['macd'] > latest['macd_signal'] else 'bearish',
            'sma_trend': 'bullish' if latest['sma_20'] > latest['sma_50'] else 'bearish',
            'long_term_trend': 'bullish' if latest['close'] > latest['sma_200'] else 'bearish'
        }
        
        return trend_analysis

    def _analyze_momentum(self, df):
        """Analyze momentum indicators."""
        latest = df.iloc[-1]
        
        momentum_analysis = {
            'rsi_value': latest['rsi'],
            'rsi_condition': 'overbought' if latest['rsi'] > 70 else 'oversold' if latest['rsi'] < 30 else 'neutral'
        }
        
        return momentum_analysis

    def _analyze_volatility(self, df):
        """Analyze volatility indicators."""
        latest = df.iloc[-1]
        
        volatility_analysis = {
            'bb_position': 'upper' if latest['close'] > latest['bb_high'] else 'lower' if latest['close'] < latest['bb_low'] else 'middle',
            'bb_width': (latest['bb_high'] - latest['bb_low']) / latest['bb_mid']
        }
        
        return volatility_analysis

    def _analyze_volume(self, df):
        """Analyze volume indicators."""
        latest = df.iloc[-1]
        
        volume_analysis = {
            'volume_trend': 'increasing' if latest['volume'] > latest['volume_sma'] else 'decreasing',
            'volume_change': (latest['volume'] - latest['volume_sma']) / latest['volume_sma']
        }
        
        return volume_analysis

    def _analyze_price_action(self, df):
        """Analyze price action."""
        latest = df.iloc[-1]
        
        price_analysis = {
            'price_change_24h': latest['price_change_24h'],
            'price_change_7d': latest['price_change_7d'],
            'above_200_sma': latest['close'] > latest['sma_200']
        }
        
        return price_analysis

    def _calculate_technical_score(self, analysis):
        """Calculate overall technical score (1-10)."""
        score = 5  # Start neutral
        
        # Trend scoring
        if analysis['trend']['macd_trend'] == 'bullish':
            score += 0.5
        if analysis['trend']['sma_trend'] == 'bullish':
            score += 0.5
        if analysis['trend']['long_term_trend'] == 'bullish':
            score += 1
            
        # Momentum scoring
        rsi = analysis['momentum']['rsi_value']
        if 40 <= rsi <= 60:  # Healthy range
            score += 1
        elif rsi > 70 or rsi < 30:  # Extreme conditions
            score -= 1
            
        # Volatility scoring
        if analysis['volatility']['bb_position'] == 'middle':
            score += 0.5
            
        # Volume scoring
        if analysis['volume']['volume_trend'] == 'increasing':
            score += 0.5
            
        # Price action scoring
        if analysis['price_action']['price_change_24h'] > 0:
            score += 0.5
        if analysis['price_action']['price_change_7d'] > 0:
            score += 0.5
            
        return max(1, min(10, score))  # Ensure score is between 1 and 10

    def _generate_signals(self, analysis):
        """Generate trading signals based on technical analysis."""
        signals = []
        
        # Trend signals
        if all(analysis['trend'][key] == 'bullish' for key in ['macd_trend', 'sma_trend', 'long_term_trend']):
            signals.append("Strong uptrend confirmed by multiple indicators")
        elif all(analysis['trend'][key] == 'bearish' for key in ['macd_trend', 'sma_trend', 'long_term_trend']):
            signals.append("Strong downtrend confirmed by multiple indicators")
            
        # Momentum signals
        rsi = analysis['momentum']['rsi_value']
        if rsi > 70:
            signals.append("Overbought conditions - potential reversal point")
        elif rsi < 30:
            signals.append("Oversold conditions - potential reversal point")
            
        # Volume signals
        if analysis['volume']['volume_trend'] == 'increasing' and analysis['volume']['volume_change'] > 0.5:
            signals.append("Significant volume increase - strong trend confirmation")
            
        # Price action signals
        if analysis['price_action']['above_200_sma']:
            signals.append("Price above 200 SMA - long-term uptrend")
            
        return signals
