import tweepy
import praw
import os
from textblob import TextBlob
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict

class SentimentAnalyzer:
    def __init__(self):
        # Twitter setup
        self.twitter_api = self._setup_twitter()
        # Reddit setup
        self.reddit_api = self._setup_reddit()
        
    def _setup_twitter(self):
        try:
            auth = tweepy.OAuthHandler(
                os.getenv('TWITTER_API_KEY'),
                os.getenv('TWITTER_API_SECRET')
            )
            auth.set_access_token(
                os.getenv('TWITTER_ACCESS_TOKEN'),
                os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            )
            return tweepy.API(auth)
        except Exception as e:
            print(f"Twitter API setup failed: {str(e)}")
            return None

    def _setup_reddit(self):
        try:
            return praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent='Crypto Analyzer Bot 1.0'
            )
        except Exception as e:
            print(f"Reddit API setup failed: {str(e)}")
            return None

    def analyze_social_sentiment(self, symbol, timeframe_hours=24):
        """Analyze social media sentiment for a given crypto symbol."""
        sentiment_data = {
            'twitter': self._analyze_twitter_sentiment(symbol, timeframe_hours),
            'reddit': self._analyze_reddit_sentiment(symbol, timeframe_hours)
        }
        
        # Combine sentiment scores
        total_sentiment = 0
        total_weight = 0
        
        for source, data in sentiment_data.items():
            if data['score'] is not None:
                weight = 1.0 if source == 'twitter' else 0.8  # Twitter slightly weighted higher
                total_sentiment += data['score'] * weight
                total_weight += weight
        
        if total_weight == 0:
            return None
            
        return {
            'combined_score': total_sentiment / total_weight,
            'details': sentiment_data,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _analyze_twitter_sentiment(self, symbol, timeframe_hours):
        if not self.twitter_api:
            return {'score': None, 'message': 'Twitter API not available'}
            
        try:
            # Search for recent tweets
            query = f"#{symbol} OR ${symbol} -filter:retweets"
            tweets = self.twitter_api.search_tweets(
                q=query,
                lang="en",
                count=100,
                tweet_mode="extended"
            )
            
            sentiments = []
            for tweet in tweets:
                analysis = TextBlob(tweet.full_text)
                sentiments.append(analysis.sentiment.polarity)
            
            if not sentiments:
                return {'score': None, 'message': 'No tweets found'}
                
            avg_sentiment = sum(sentiments) / len(sentiments)
            return {
                'score': avg_sentiment,
                'sample_size': len(sentiments),
                'message': 'Analysis successful'
            }
            
        except Exception as e:
            return {'score': None, 'message': f'Error: {str(e)}'}

    def _analyze_reddit_sentiment(self, symbol, timeframe_hours):
        if not self.reddit_api:
            return {'score': None, 'message': 'Reddit API not available'}
            
        try:
            # Search in relevant subreddits
            subreddits = ['cryptocurrency', 'cryptomarkets', f'{symbol.lower()}']
            posts = []
            
            for subreddit in subreddits:
                try:
                    sub = self.reddit_api.subreddit(subreddit)
                    posts.extend(sub.search(
                        query=symbol,
                        time_filter='day',
                        limit=50
                    ))
                except:
                    continue
            
            sentiments = []
            for post in posts:
                # Analyze post title and body
                title_analysis = TextBlob(post.title)
                body_analysis = TextBlob(post.selftext) if post.selftext else None
                
                # Weight title sentiment more heavily than body
                title_weight = 0.6
                body_weight = 0.4
                
                sentiment = title_analysis.sentiment.polarity * title_weight
                if body_analysis:
                    sentiment += body_analysis.sentiment.polarity * body_weight
                
                sentiments.append(sentiment)
            
            if not sentiments:
                return {'score': None, 'message': 'No Reddit posts found'}
                
            avg_sentiment = sum(sentiments) / len(sentiments)
            return {
                'score': avg_sentiment,
                'sample_size': len(sentiments),
                'message': 'Analysis successful'
            }
            
        except Exception as e:
            return {'score': None, 'message': f'Error: {str(e)}'}

    def get_sentiment_summary(self, sentiment_data):
        """Generate a human-readable summary of sentiment analysis."""
        if not sentiment_data or 'combined_score' not in sentiment_data:
            return "Sentiment analysis unavailable"
            
        score = sentiment_data['combined_score']
        
        if score >= 0.5:
            return "Very Positive - Strong community enthusiasm and support"
        elif score >= 0.2:
            return "Positive - Generally favorable community sentiment"
        elif score >= -0.2:
            return "Neutral - Mixed or balanced community sentiment"
        elif score >= -0.5:
            return "Negative - Significant community concerns"
        else:
            return "Very Negative - Strong community skepticism or criticism"
