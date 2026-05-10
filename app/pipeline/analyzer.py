import math
import time
from math import exp
from collections import deque

class ViralAnalyzer:
    def __init__(self):
        self.clip_scores = deque(maxlen=100)
        
    def analyze(self, posts, top_k=10):
        if not posts:
            return []
            
        now_ts = time.time()
        
        scored_posts = []
        
        for p in posts:
            try:
                # Safe extraction with defaults
                views = p.get('views', 0)
                likes = p.get('likes', 0)
                timestamp = p.get('timestamp', now_ts)
                duration = p.get('duration')
                
                # Skip if critical data missing
                if views == 0:
                    continue
                
                # Engagement rate
                engagement = likes / max(views, 1)
                
                # Freshness decay
                age_hours = (now_ts - timestamp) / 3600
                if age_hours <= 0:
                    age_hours = 0.1
                
                freshness = exp(-age_hours / 24)
                freshness = min(freshness, 1.0)
                
                # Velocity (views per hour)
                velocity = views / age_hours
                velocity = min(velocity, 1_000_000)
                
                # Log-scale for stability
                velocity_score = math.log1p(velocity) * 1000
                views_score = math.log1p(views) * 500
                
                # Length bonus (optional - only if duration exists)
                length_bonus = 0
                if duration is not None:
                    # Prefer 1-5 min videos (60-300s) for chinese drama clips
                    if 60 <= duration <= 300:
                        length_bonus = 10_000
                    elif duration <= 60:
                        length_bonus = 5_000  # shorts are OK too
                
                # Combined score
                p['score'] = (
                    engagement * 150_000 +
                    velocity_score +
                    views_score +
                    freshness * 40_000 +
                    length_bonus
                )
                
                scored_posts.append(p)
                
            except Exception as e:
                # Log but don't crash
                import logging
                logging.warning(f"Failed to score post {p.get('video_id')}: {e}")
                continue
        
        return sorted(scored_posts, key=lambda x: x['score'], reverse=True)[:top_k]