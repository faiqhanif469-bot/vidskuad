/**
 * ProgressScreen - V1 Simplified
 * Shows real-time progress from backend
 */

import { motion } from 'motion/react';
import { CheckCircle2, Circle, Loader2, AlertCircle, Video } from 'lucide-react';
import { Progress } from '@/app/components/ui/progress';

interface ProgressScreenProps {
  progress: number;
  currentStep: string;
  etaSeconds: number;
  error?: string;
}

export function ProgressScreen({ progress, currentStep, etaSeconds, error }: ProgressScreenProps) {
  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${minutes}m ${secs}s`;
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-[#0a0e27] via-[#1a1f3a] to-[#0f1420] flex items-center justify-center p-8">
      {/* Animated Background Gradients */}
      <motion.div
        className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-[120px]"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <motion.div
        className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[120px]"
        animate={{
          scale: [1.2, 1, 1.2],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1,
        }}
      />

      <div className="w-full max-w-2xl relative z-10">
        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-3 mb-3">
            <Video className="h-10 w-10 text-white" />
            <h1 className="text-5xl font-bold text-white">
              VidSquad
            </h1>
          </div>
          <motion.p
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="text-white/70 text-lg"
          >
            {error ? 'Generation Failed' : 'Generating your video...'}
          </motion.p>
        </motion.div>

        {/* Progress Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="bg-[#2a2f45]/80 backdrop-blur-xl rounded-2xl p-8 shadow-2xl border border-slate-700/30"
        >
          {error ? (
            /* Error State */
            <div className="text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
                className="flex justify-center mb-4"
              >
                <AlertCircle className="h-16 w-16 text-red-400" />
              </motion.div>
              <h2 className="text-xl font-semibold text-white mb-2">Generation Failed</h2>
              <p className="text-slate-400 text-sm">{error}</p>
            </div>
          ) : (
            <>
              {/* Overall Progress */}
              <div className="mb-8">
                <div className="flex justify-between items-center mb-3">
                  <h2 className="text-lg font-semibold text-white">Overall Progress</h2>
                  <span className="text-blue-400 text-sm font-medium tabular-nums">
                    {Math.round(progress)}%
                  </span>
                </div>
                <Progress value={progress} className="h-2 bg-slate-800/50" />
                <div className="flex justify-between items-center mt-2">
                  <p className="text-slate-500 text-sm">{currentStep}</p>
                  {etaSeconds > 0 && (
                    <p className="text-slate-500 text-sm tabular-nums">
                      ETA: {formatTime(etaSeconds)}
                    </p>
                  )}
                </div>
              </div>

              {/* Current Step Indicator */}
              <motion.div
                className="flex items-center gap-4 p-4 rounded-xl bg-blue-600/20 border border-blue-500/50 shadow-lg shadow-blue-900/20"
              >
                <Loader2 className="h-6 w-6 text-blue-400 animate-spin flex-shrink-0" />
                <div className="flex-1">
                  <p className="font-medium text-blue-300">{currentStep}</p>
                </div>
                <motion.span
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="text-xs text-blue-400 font-medium"
                >
                  In Progress...
                </motion.span>
              </motion.div>
            </>
          )}
        </motion.div>

        {/* Fun Fact */}
        {!error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="text-center mt-6"
          >
            <p className="text-slate-500 text-sm">
              💡 Our AI is analyzing thousands of sources and generating custom visuals for your video
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
