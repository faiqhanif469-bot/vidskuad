/**
 * API Service - Backend Communication
 * Auth disabled for now - remove token requirement
 */

// import { auth } from './firebase'; // Disabled for now

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Generate video from script
 */
export const generateVideo = async (
  script: string,
  duration: number,
  title?: string
): Promise<{ success: boolean; job_id: string; task_id: string; status: string; message: string }> => {
  // const token = await auth.currentUser?.getIdToken(); // Disabled for now

  const response = await fetch(`${API_URL}/api/videos/generate`, {
    method: 'POST',
    headers: {
      // Authorization: `Bearer ${token}`, // Disabled for now
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ script, duration, title }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate video');
  }

  return await response.json();
};

/**
 * Check job status
 */
export const checkStatus = async (
  jobId: string
): Promise<{
  job_id: string;
  status: string;
  progress: number;
  current_step?: string;
  eta_seconds?: number;
  error?: string;
  result?: any;
}> => {
  // const token = await auth.currentUser?.getIdToken(); // Disabled for now

  const response = await fetch(`${API_URL}/api/videos/status/${jobId}`, {
    headers: {
      // Authorization: `Bearer ${token}`, // Disabled for now
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to check status');
  }

  return await response.json();
};

/**
 * Get download links
 */
export const getDownloadLinks = async (
  jobId: string
): Promise<{
  job_id: string;
  premiere_url: string;
  capcut_url: string;
  expires_at: string;
  clips_count: number;
  images_count: number;
}> => {
  // const token = await auth.currentUser?.getIdToken(); // Disabled for now

  const response = await fetch(`${API_URL}/api/videos/download/${jobId}`, {
    headers: {
      // Authorization: `Bearer ${token}`, // Disabled for now
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get download links');
  }

  return await response.json();
};

/**
 * Get user's projects
 */
export const getProjects = async (): Promise<{
  success: boolean;
  projects: Array<{
    job_id: string;
    title: string;
    status: string;
    progress: number;
    created_at: string;
    completed_at?: string;
  }>;
  total: number;
}> => {
  // const token = await auth.currentUser?.getIdToken(); // Disabled for now

  const response = await fetch(`${API_URL}/api/projects/`, {
    headers: {
      // Authorization: `Bearer ${token}`, // Disabled for now
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get projects');
  }

  return await response.json();
};

/**
 * Get current user info
 */
export const getCurrentUser = async (): Promise<{
  user_id: string;
  email: string;
  subscription_tier: string;
  videos_created_this_month: number;
  created_at: string;
}> => {
  // const token = await auth.currentUser?.getIdToken(); // Disabled for now

  const response = await fetch(`${API_URL}/api/auth/me`, {
    headers: {
      // Authorization: `Bearer ${token}`, // Disabled for now
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get user info');
  }

  return await response.json();
};

/**
 * Get queue status
 */
export const getQueueStatus = async (): Promise<{
  pending_jobs: number;
  processing_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  estimated_wait_time_seconds: number;
}> => {
  // const token = await auth.currentUser?.getIdToken(); // Disabled for now

  const response = await fetch(`${API_URL}/api/videos/queue/status`, {
    headers: {
      // Authorization: `Bearer ${token}`, // Disabled for now
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get queue status');
  }

  return await response.json();
};

/**
 * Generate single image
 */
export const generateImage = async (
  prompt: string,
  provider: string = 'cloudflare'
): Promise<{
  success: boolean;
  image_id: string;
  image_url: string;
  prompt: string;
}> => {
  // const token = await auth.currentUser?.getIdToken(); // Disabled for now

  const response = await fetch(`${API_URL}/api/images/generate`, {
    method: 'POST',
    headers: {
      // Authorization: `Bearer ${token}`, // Disabled for now
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt, provider }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate image');
  }

  return await response.json();
};

/**
 * Connect to WebSocket for real-time progress updates
 * Falls back to polling if WebSocket fails
 */
export const connectProgressWebSocket = (
  jobId: string,
  onUpdate: (data: any) => void,
  onError: (error: Error) => void
): (() => void) => {
  const wsUrl = API_URL.replace('http', 'ws').replace('https', 'wss');
  let ws: WebSocket | null = null;
  let pollInterval: NodeJS.Timeout | null = null;
  let isConnected = false;

  // Try WebSocket first
  try {
    ws = new WebSocket(`${wsUrl}/ws/progress/${jobId}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
      isConnected = true;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onUpdate(data);

        // Close if completed or failed
        if (data.status === 'completed' || data.status === 'failed') {
          ws?.close();
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      isConnected = false;
      
      // Fallback to polling
      if (!pollInterval) {
        console.log('Falling back to polling...');
        startPolling();
      }
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
      isConnected = false;
    };
  } catch (err) {
    console.error('Failed to create WebSocket:', err);
    startPolling();
  }

  // Polling fallback
  function startPolling() {
    pollInterval = setInterval(async () => {
      try {
        const status = await checkStatus(jobId);
        onUpdate(status);

        // Stop polling if completed or failed
        if (status.status === 'completed' || status.status === 'failed') {
          if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
          }
        }
      } catch (err: any) {
        console.error('Polling error:', err);
        onError(err);
      }
    }, 2000);
  }

  // Cleanup function
  return () => {
    if (ws && isConnected) {
      ws.close();
    }
    if (pollInterval) {
      clearInterval(pollInterval);
    }
  };
};
