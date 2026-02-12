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
import { generateVideo, checkStatus } from '@/services/api';

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
  const [user, setUser] = useState<any>(null);
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

  // Store input data temporarily
  const [inputData, setInputData] = useState<{
    script: string;
    duration: string;
    title: string;
  } | null>(null);

  // Handle script submission from InputScreen
  const handleInputSubmit = async (script: string, duration: string, title: string) => {
    try {
      setError('');
      
      // Simulate backend call - remove this and uncomment real API call when backend is ready
      const mockJobId = 'test-job-' + Date.now();
      
      // Initialize job data
      setJobData({
        jobId: mockJobId,
        status: 'processing',
        progress: 0,
        currentStep: 'Starting...',
      });
      
      // Move to progress screen
      setCurrentScreen('progress');
      
      // Simulate progress updates
      let currentProgress = 0;
      const progressInterval = setInterval(() => {
        currentProgress += 5;
        
        if (currentProgress <= 100) {
          const steps = [
            'Analyzing script...',
            'Generating scene breakdown...',
            'Searching for video clips...',
            'Generating AI images...',
            'Processing media assets...',
            'Creating timeline...',
            'Finalizing exports...',
            'Complete!'
          ];
          
          const stepIndex = Math.floor((currentProgress / 100) * steps.length);
          const currentStepText = steps[Math.min(stepIndex, steps.length - 1)];
          
          setJobData({
            jobId: mockJobId,
            status: currentProgress >= 100 ? 'completed' : 'processing',
            progress: currentProgress,
            currentStep: currentStepText,
            etaSeconds: Math.max(0, Math.floor((100 - currentProgress) * 2)),
            result: currentProgress >= 100 ? {
              premiere_url: 'https://example.com/premiere.zip',
              capcut_url: 'https://example.com/capcut.zip',
              clips_count: 15,
              images_count: 8,
              expires_at: new Date(Date.now() + 20 * 60 * 1000).toISOString(),
            } : undefined,
          });
          
          if (currentProgress >= 100) {
            clearInterval(progressInterval);
            setTimeout(() => {
              setCurrentScreen('download');
            }, 1000);
          }
        }
      }, 1000); // Update every second
      
      // Cleanup on unmount
      return () => clearInterval(progressInterval);
      
      /* UNCOMMENT THIS WHEN BACKEND IS READY:
      
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
      
      // Start polling for status
      const pollInterval = setInterval(async () => {
        try {
          const status = await checkStatus(result.job_id);
          
          setJobData({
            jobId: result.job_id,
            status: status.status,
            progress: status.progress,
            currentStep: status.current_step,
            etaSeconds: status.eta_seconds,
            error: status.error,
            result: status.result,
          });
          
          // If completed or failed, stop polling
          if (status.status === 'completed') {
            clearInterval(pollInterval);
            setCurrentScreen('download');
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            setError(status.error || 'Video generation failed');
          }
        } catch (err: any) {
          console.error('Error checking status:', err);
          // Don't stop polling on error, might be temporary
        }
      }, 2000); // Poll every 2 seconds
      
      // Cleanup on unmount
      return () => clearInterval(pollInterval);
      
      */
      
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
