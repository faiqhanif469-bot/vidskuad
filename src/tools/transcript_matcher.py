"""
Enterprise-Grade Transcript Matching
TF-IDF and BM25 algorithms for semantic matching
"""

import numpy as np
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from rank_bm25 import BM25Okapi
import logging

logger = logging.getLogger(__name__)


class TranscriptMatcher:
    """Match transcripts to scene requirements using TF-IDF and BM25"""
    
    def __init__(self):
        self.tfidf = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),  # Unigrams and bigrams
            max_features=5000
        )
        self.bm25 = None
        self.corpus = []
    
    def fit(self, transcripts: List[str]):
        """
        Fit the matcher on a corpus of transcripts
        
        Args:
            transcripts: List of transcript texts
        """
        self.corpus = transcripts
        
        # Fit TF-IDF
        if transcripts:
            self.tfidf.fit(transcripts)
            
            # Fit BM25
            tokenized_corpus = [doc.lower().split() for doc in transcripts]
            self.bm25 = BM25Okapi(tokenized_corpus)
            
            logger.info(f"Fitted matcher on {len(transcripts)} transcripts")
    
    def score_tfidf(self, query: str, transcripts: List[str]) -> np.ndarray:
        """
        Score transcripts using TF-IDF cosine similarity
        
        Args:
            query: Search query
            transcripts: List of transcript texts
        
        Returns:
            Array of scores (0-1)
        """
        if not transcripts:
            return np.array([])
        
        # Transform query and transcripts
        query_vec = self.tfidf.transform([query])
        transcript_vecs = self.tfidf.transform(transcripts)
        
        # Calculate cosine similarity
        scores = (transcript_vecs * query_vec.T).toarray().flatten()
        
        return scores
    
    def score_bm25(self, query: str) -> np.ndarray:
        """
        Score transcripts using BM25
        
        Args:
            query: Search query
        
        Returns:
            Array of scores
        """
        if not self.bm25:
            return np.array([])
        
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # Normalize to 0-1
        if scores.max() > 0:
            scores = scores / scores.max()
        
        return scores
    
    def score_hybrid(
        self, 
        query: str, 
        transcripts: List[str],
        tfidf_weight: float = 0.5,
        bm25_weight: float = 0.5
    ) -> np.ndarray:
        """
        Hybrid scoring combining TF-IDF and BM25
        
        Args:
            query: Search query
            transcripts: List of transcript texts
            tfidf_weight: Weight for TF-IDF score
            bm25_weight: Weight for BM25 score
        
        Returns:
            Array of combined scores
        """
        # Fit if needed
        if not self.corpus or self.corpus != transcripts:
            self.fit(transcripts)
        
        # Get scores
        tfidf_scores = self.score_tfidf(query, transcripts)
        bm25_scores = self.score_bm25(query)
        
        # Combine
        combined = tfidf_scores * tfidf_weight + bm25_scores * bm25_weight
        
        return combined
    
    def rank_videos_by_transcript(
        self,
        videos: List[Dict],
        scene: Dict,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Rank videos by transcript matching
        
        Args:
            videos: List of video dicts with 'transcript' field
            scene: Scene dict with keywords and description
            top_k: Number of top videos to return
        
        Returns:
            Ranked list of videos with scores
        """
        # Extract transcripts
        transcripts = []
        valid_videos = []
        
        for video in videos:
            transcript = video.get('transcript_text', '')
            if transcript:
                transcripts.append(transcript)
                valid_videos.append(video)
        
        if not transcripts:
            logger.warning("No transcripts available for ranking")
            return []
        
        # Build query from scene
        query_parts = []
        query_parts.extend(scene.get('keywords', []))
        query_parts.append(scene.get('scene_description', ''))
        query_parts.append(scene.get('visual_context', ''))
        query = ' '.join(query_parts)
        
        # Score
        scores = self.score_hybrid(query, transcripts)
        
        # Add scores to videos
        for i, video in enumerate(valid_videos):
            video['transcript_score'] = float(scores[i])
        
        # Sort by score
        ranked = sorted(valid_videos, key=lambda x: x['transcript_score'], reverse=True)
        
        return ranked[:top_k]
    
    def find_best_timestamp_in_transcript(
        self,
        transcript_segments: List[Dict],
        keywords: List[str],
        duration_needed: float = 8.0
    ) -> Dict:
        """
        Find best timestamp in transcript for keywords
        
        Args:
            transcript_segments: List of segment dicts with start_time, end_time, text
            keywords: Keywords to find
            duration_needed: Duration of clip needed
        
        Returns:
            Dict with start_time, end_time, score, text
        """
        best_segment = None
        best_score = 0
        
        for i, segment in enumerate(transcript_segments):
            # Get text window
            window_segments = transcript_segments[i:i+5]  # 5 segments window
            window_text = ' '.join(s['text'] for s in window_segments)
            window_text_lower = window_text.lower()
            
            # Count keyword matches
            score = sum(1 for kw in keywords if kw.lower() in window_text_lower)
            
            if score > best_score:
                best_score = score
                start_time = segment['start_time']
                end_time = min(
                    start_time + duration_needed,
                    window_segments[-1]['end_time']
                )
                
                best_segment = {
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'text': window_text,
                    'keyword_matches': score
                }
        
        return best_segment or {}


if __name__ == '__main__':
    # Test
    matcher = TranscriptMatcher()
    
    transcripts = [
        "President Kennedy speaks about going to the moon",
        "The Apollo program was a success",
        "World War 2 combat footage"
    ]
    
    query = "Kennedy moon speech"
    
    matcher.fit(transcripts)
    scores = matcher.score_hybrid(query, transcripts)
    
    print("Scores:", scores)
    print("Best match:", transcripts[scores.argmax()])
