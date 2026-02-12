"""
Queue Service
Monitor Celery queue status
"""

from app.workers.celery_app import celery_app
from firebase_admin import firestore

db = firestore.client()


class QueueService:
    """Monitor and manage job queue"""
    
    def get_queue_stats(self) -> dict:
        """
        Get queue statistics
        
        Returns:
            Dict with queue stats
        """
        try:
            # Get active tasks from Celery
            inspect = celery_app.control.inspect()
            active = inspect.active()
            
            # Count active tasks
            active_count = 0
            if active:
                for worker, tasks in active.items():
                    active_count += len(tasks)
            
            # Get queue stats from Firestore
            projects_ref = db.collection('projects')
            
            pending = projects_ref.where('status', '==', 'queued').stream()
            pending_count = len(list(pending))
            
            processing = projects_ref.where('status', '==', 'processing').stream()
            processing_count = len(list(processing))
            
            completed = projects_ref.where('status', '==', 'completed').stream()
            completed_count = len(list(completed))
            
            failed = projects_ref.where('status', '==', 'failed').stream()
            failed_count = len(list(failed))
            
            # Estimate wait time (4 minutes per job, 4 workers)
            avg_job_time = 240  # 4 minutes
            workers = 4
            estimated_wait_time = (pending_count / workers) * avg_job_time
            
            return {
                'pending': pending_count,
                'processing': processing_count,
                'completed': completed_count,
                'failed': failed_count,
                'active_workers': active_count,
                'estimated_wait_time': int(estimated_wait_time)
            }
        
        except Exception as e:
            return {
                'pending': 0,
                'processing': 0,
                'completed': 0,
                'failed': 0,
                'active_workers': 0,
                'estimated_wait_time': 0,
                'error': str(e)
            }
