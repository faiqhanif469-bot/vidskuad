"""
Enterprise-Grade CLIP Verification
Visual content matching using CLIP model
"""

import torch
import clip
from PIL import Image
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CLIPVerifier:
    """Verify visual content using CLIP model"""
    
    def __init__(self, model_name: str = "ViT-B/32", device: Optional[str] = None):
        """
        Initialize CLIP verifier
        
        Args:
            model_name: CLIP model name (ViT-B/32 is lightweight and fast)
            device: Device to use ('cuda' or 'cpu', auto-detect if None)
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            logger.info(f"Loading CLIP model {model_name} on {self.device}")
            self.model, self.preprocess = clip.load(model_name, device=self.device)
            self.model.eval()
            logger.info("CLIP model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading CLIP model: {e}")
            raise
    
    def verify_frame(
        self,
        frame_path: str,
        description: str
    ) -> float:
        """
        Verify if frame matches description
        
        Args:
            frame_path: Path to frame image
            description: Text description to match
        
        Returns:
            Similarity score (0-1)
        """
        try:
            # Load and preprocess image
            image = Image.open(frame_path).convert('RGB')
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Tokenize text
            text_input = clip.tokenize([description]).to(self.device)
            
            # Get features
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                text_features = self.model.encode_text(text_input)
                
                # Normalize features
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                
                # Calculate similarity
                similarity = (image_features @ text_features.T).item()
            
            # Convert to 0-1 range (CLIP outputs -1 to 1)
            score = (similarity + 1) / 2
            
            return score
            
        except Exception as e:
            logger.error(f"Error verifying frame: {e}")
            return 0.0
    
    def verify_frames_batch(
        self,
        frame_paths: List[str],
        description: str
    ) -> np.ndarray:
        """
        Verify multiple frames at once (faster)
        
        Args:
            frame_paths: List of frame paths
            description: Text description
        
        Returns:
            Array of similarity scores
        """
        if not frame_paths:
            return np.array([])
        
        try:
            # Load and preprocess images
            images = []
            for path in frame_paths:
                try:
                    image = Image.open(path).convert('RGB')
                    images.append(self.preprocess(image))
                except Exception as e:
                    logger.warning(f"Error loading {path}: {e}")
                    images.append(None)
            
            # Filter valid images
            valid_images = [img for img in images if img is not None]
            if not valid_images:
                return np.zeros(len(frame_paths))
            
            # Stack images
            image_input = torch.stack(valid_images).to(self.device)
            
            # Tokenize text
            text_input = clip.tokenize([description]).to(self.device)
            
            # Get features
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                text_features = self.model.encode_text(text_input)
                
                # Normalize
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                
                # Calculate similarities
                similarities = (image_features @ text_features.T).squeeze().cpu().numpy()
            
            # Convert to 0-1 range
            scores = (similarities + 1) / 2
            
            # Handle single image case
            if isinstance(scores, np.float32):
                scores = np.array([scores])
            
            return scores
            
        except Exception as e:
            logger.error(f"Error verifying frames batch: {e}")
            return np.zeros(len(frame_paths))
    
    def find_best_frame(
        self,
        frame_paths: List[str],
        description: str
    ) -> Dict:
        """
        Find best matching frame
        
        Args:
            frame_paths: List of frame paths
            description: Text description
        
        Returns:
            Dict with best_frame, score, index
        """
        scores = self.verify_frames_batch(frame_paths, description)
        
        if len(scores) == 0:
            return {'best_frame': None, 'score': 0.0, 'index': -1}
        
        best_idx = scores.argmax()
        
        return {
            'best_frame': frame_paths[best_idx],
            'score': float(scores[best_idx]),
            'index': int(best_idx),
            'all_scores': scores.tolist()
        }
    
    def verify_video_content(
        self,
        video_frames: List[str],
        scene_description: str,
        visual_context: str,
        keywords: List[str]
    ) -> Dict:
        """
        Comprehensive video content verification
        
        Args:
            video_frames: List of frame paths
            scene_description: Scene description
            visual_context: Visual context
            keywords: Keywords
        
        Returns:
            Verification result dict
        """
        # Build comprehensive description
        descriptions = [
            scene_description,
            visual_context,
            ' '.join(keywords)
        ]
        
        # Score against each description
        all_scores = []
        for desc in descriptions:
            if desc:
                scores = self.verify_frames_batch(video_frames, desc)
                all_scores.append(scores)
        
        if not all_scores:
            return {'verified': False, 'confidence': 0.0}
        
        # Average scores
        avg_scores = np.mean(all_scores, axis=0)
        max_score = avg_scores.max()
        best_idx = avg_scores.argmax()
        
        return {
            'verified': max_score > 0.6,  # Threshold
            'confidence': float(max_score),
            'best_frame_index': int(best_idx),
            'best_frame': video_frames[best_idx] if video_frames else None,
            'all_scores': avg_scores.tolist()
        }


if __name__ == '__main__':
    # Test CLIP verifier
    verifier = CLIPVerifier()
    
    # Test with a frame
    frame_path = "cache/frames/test_frame.jpg"
    description = "President Kennedy giving a speech"
    
    if os.path.exists(frame_path):
        score = verifier.verify_frame(frame_path, description)
        print(f"Similarity score: {score:.3f}")
    else:
        print("Test frame not found")
