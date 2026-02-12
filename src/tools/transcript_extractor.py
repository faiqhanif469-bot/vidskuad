"""
Enterprise-Grade Transcript Extractor
Extracts and processes video transcripts with timestamps
"""

import yt_dlp
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TranscriptSegment:
    """Single transcript segment with timing"""
    start_time: float
    end_time: float
    text: str
    
    def to_dict(self) -> Dict:
        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'text': self.text
        }


class TranscriptExtractor:
    """Extract and process video transcripts"""
    
    def __init__(self):
        self.ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'quiet': True,
            'no_warnings': True,
        }
    
    def extract_transcript(self, video_url: str) -> Optional[List[TranscriptSegment]]:
        """Extract transcript from YouTube video"""
        try:
            logger.info(f"Extracting transcript from: {video_url}")
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                # Try automatic captions first
                subtitles = info.get('automatic_captions', {})
                if not subtitles:
                    subtitles = info.get('subtitles', {})
                
                if not subtitles or 'en' not in subtitles:
                    logger.warning(f"No English transcript available")
                    return None
                
                # Get English subtitles
                en_subs = subtitles['en']
                
                # Find JSON3 format
                json3_sub = None
                for sub in en_subs:
                    if sub.get('ext') == 'json3':
                        json3_sub = sub
                        break
                
                if not json3_sub:
                    return None
                
                # Download subtitle data
                import requests
                sub_data = requests.get(json3_sub['url']).json()
                
                # Parse segments
                segments = self._parse_json3_subtitles(sub_data)
                
                logger.info(f"Extracted {len(segments)} segments")
                return segments
                
        except Exception as e:
            logger.error(f"Error extracting transcript: {e}")
            return None
    
    def _parse_json3_subtitles(self, sub_data: Dict) -> List[TranscriptSegment]:
        """Parse JSON3 subtitle format"""
        segments = []
        
        events = sub_data.get('events', [])
        for event in events:
            if 'segs' not in event:
                continue
            
            start_time = event.get('tStartMs', 0) / 1000.0
            duration = event.get('dDurationMs', 0) / 1000.0
            end_time = start_time + duration
            
            text_parts = []
            for seg in event['segs']:
                if 'utf8' in seg:
                    text_parts.append(seg['utf8'])
            
            text = ''.join(text_parts).strip()
            
            if text:
                segments.append(TranscriptSegment(
                    start_time=start_time,
                    end_time=end_time,
                    text=text
                ))
        
        return segments
    
    def get_full_transcript_text(self, segments: List[TranscriptSegment]) -> str:
        """Get full transcript as single text"""
        return ' '.join(seg.text for seg in segments)
    
    def find_keyword_timestamps(
        self, 
        segments: List[TranscriptSegment], 
        keywords: List[str]
    ) -> List[Tuple[str, float]]:
        """Find timestamps where keywords appear"""
        matches = []
        
        for segment in segments:
            text_lower = segment.text.lower()
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in text_lower:
                    matches.append((keyword, segment.start_time))
        
        return matches
    
    def extract_best_segments(
        self, 
        segments: List[TranscriptSegment],
        keywords: List[str],
        min_duration: float = 5.0,
        max_duration: float = 15.0
    ) -> List[Dict]:
        """Extract best segments containing keywords"""
        keyword_times = self.find_keyword_timestamps(segments, keywords)
        
        if not keyword_times:
            return []
        
        best_segments = []
        for keyword, timestamp in keyword_times:
            start_time = max(0, timestamp - 2.0)
            end_time = timestamp + max_duration
            
            range_segments = [
                seg for seg in segments
                if seg.start_time >= start_time and seg.end_time <= end_time
            ]
            
            if not range_segments:
                continue
            
            actual_start = range_segments[0].start_time
            actual_end = range_segments[-1].end_time
            duration = actual_end - actual_start
            
            if duration < min_duration:
                continue
            
            text = ' '.join(seg.text for seg in range_segments)
            
            best_segments.append({
                'keyword': keyword,
                'start_time': actual_start,
                'end_time': actual_end,
                'duration': duration,
                'text': text,
                'keyword_count': sum(1 for kw in keywords if kw.lower() in text.lower())
            })
        
        best_segments.sort(key=lambda x: x['keyword_count'], reverse=True)
        
        return best_segments


if __name__ == '__main__':
    extractor = TranscriptExtractor()
    video_url = "https://www.youtube.com/watch?v=gm3IIIVCKR8"
    segments = extractor.extract_transcript(video_url)
    
    if segments:
        print(f"Extracted {len(segments)} segments")
        keywords = ["moon", "space"]
        best = extractor.extract_best_segments(segments, keywords)
        print(f"Found {len(best)} best segments")
