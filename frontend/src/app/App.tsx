/**
 * VidSquad V1 - Main App
 * Simplified flow: Input → Progress → Download (Auth disabled for now)
 */

import { useState } from 'react';
// import { auth } from '@/services/firebase'; // Disabled for now
// import { AuthScreen } from '@/components/AuthScreen'; // Disabled for now
import { InputScreen } from '@/app/components/InputScreen';
import { ProgressScreen } from '@/components/ProgressScreen';
import { DownloadScreen } from '@/components/DownloadScreen';
import { generateVideo, connectProgressWebSocket } from '@/services/api';

type Screen = 'input' | 'progress' | 'download'; // Removed 'auth'

interface JobData {
  jobId: string;
  status: string;
  progress: number;
  currentStep?: string;
  etaSeconds?: number;
  error?: string;
  result?: {
    premiere_url: string;
    capcut_url: string;
    clips_count: number;
    images_count: number;
    expires_at: string;
  };
}

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('input'); // Skip auth for now
  const [jobData, setJobData] = useState<JobData | null>(null);
  const [error, setError] = useState<string>('');

  // Auth disabled for now - skip straight to input
  // useEffect(() => {
  //   const unsubscribe = auth.onAuthStateChanged((user) => {
  //     setUser(user);
  //     if (user) {
  //       setCurrentScreen('input');
  //     } else {
  //       setCurrentScreen('auth');
  //     }
  //   });

  //   return () => unsubscribe();
  // }, []);

  // Handle script submission from InputScreen
  const handleInputSubmit = async (script: string, duration: string, title: string) => {
    try {
      setError('');
      
      // Convert duration string to seconds
      const durationMap: { [key: string]: number } = {
        '6-9': 450,      // 7.5 minutes
        '10-12': 660,    // 11 minutes
        '18-20': 1140,   // 19 minutes
        '30-40': 2100,   // 35 minutes
      };
      
      const durationSeconds = durationMap[duration] || 2100;
      
      // Call backend API
      const result = await generateVideo(script, durationSeconds, title || 'Untitled Video');
      
      // Initialize job data
      setJobData({
        jobId: result.job_id,
        status: 'queued',
        progress: 0,
        currentStep: 'Starting...',
      });
      
      // Move to progress screen
      setCurrentScreen('progress');
      
      // Connect to WebSocket for real-time updates (with polling fallback)
      const cleanup = connectProgressWebSocket(
        result.job_id,
        (data) => {
          // Update job data with real-time progress
          setJobData({
            jobId: result.job_id,
            status: data.status,
            progress: data.progress,
            currentStep: data.current_step,
            etaSeconds: data.eta_seconds,
            error: data.error,
            result: data.result,
          });
          
          // If completed, move to download screen
          if (data.status === 'completed') {
            setCurrentScreen('download');
          } else if (data.status === 'failed') {
            setError(data.error || 'Video generation failed');
          }
        },
        (err) => {
          console.error('Progress update error:', err);
          // Don't show error to user, WebSocket will fallback to polling
        }
      );
      
      // Cleanup on unmount
      return cleanup;
      
    } catch (err: any) {
      console.error('Error starting video generation:', err);
      setError(err.message || 'Failed to start video generation');
    }
  };

  // Handle new video creation
  const handleCreateNew = () => {
    setJobData(null);
    setError('');
    setCurrentScreen('input');
  };

  return (
    <>
      {/* Auth disabled for now */}
      {/* {currentScreen === 'auth' && (
        <AuthScreen onLogin={() => setCurrentScreen('input')} />
      )} */}
      
      {currentScreen === 'input' && (
        <InputScreen 
          onSubmit={(script: string, duration: string, title: string) => {
            handleInputSubmit(script, duration, title);
          }} 
        />
      )}
      
      {currentScreen === 'progress' && jobData && (
        <ProgressScreen
          progress={jobData.progress}
          currentStep={jobData.currentStep || 'Processing...'}
          etaSeconds={jobData.etaSeconds || 0}
          error={error}
        />
      )}
      
      {currentScreen === 'download' && jobData?.result && (
        <DownloadScreen
          jobId={jobData.jobId}
          premiereUrl={jobData.result.premiere_url}
          capcutUrl={jobData.result.capcut_url}
          clipsCount={jobData.result.clips_count}
          imagesCount={jobData.result.images_count}
          expiresAt={jobData.result.expires_at}
          onCreateNew={handleCreateNew}
        />
      )}
    </>
  );
}
