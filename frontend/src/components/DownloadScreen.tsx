/**
 * DownloadScreen - V1 with Backend Integration
 * Downloads Premiere Pro and CapCut exports
 */

import { useState } from 'react';
import { motion } from 'motion/react';
import { Download, FileVideo, Package, CheckCircle2, Sparkles, Video, Clock } from 'lucide-react';
import { Button } from '@/app/components/ui/button';

interface DownloadScreenProps {
  jobId: string;
  premiereUrl: string;
  capcutUrl: string;
  clipsCount: number;
  imagesCount: number;
  expiresAt: string;
  onCreateNew: () => void;
}

export function DownloadScreen({
  jobId,
  premiereUrl,
  capcutUrl,
  clipsCount,
  imagesCount,
  expiresAt,
  onCreateNew,
}: DownloadScreenProps) {
  const [downloadingPremiere, setDownloadingPremiere] = useState(false);
  const [downloadingCapcut, setDownloadingCapcut] = useState(false);
  const [premiereDownloaded, setPremiereDownloaded] = useState(false);
  const [capcutDownloaded, setCapcutDownloaded] = useState(false);

  const handleDownloadPremiere = async () => {
    setDownloadingPremiere(true);
    try {
      // Trigger download
      const link = document.createElement('a');
      link.href = premiereUrl;
      link.download = `vidsquad-premiere-${jobId}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setTimeout(() => {
        setDownloadingPremiere(false);
        setPremiereDownloaded(true);
      }, 1000);
    } catch (error) {
      console.error('Download failed:', error);
      setDownloadingPremiere(false);
    }
  };

  const handleDownloadCapcut = async () => {
    setDownloadingCapcut(true);
    try {
      // Trigger download
      const link = document.createElement('a');
      link.href = capcutUrl;
      link.download = `vidsquad-capcut-${jobId}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setTimeout(() => {
        setDownloadingCapcut(false);
        setCapcutDownloaded(true);
      }, 1000);
    } catch (error) {
      console.error('Download failed:', error);
      setDownloadingCapcut(false);
    }
  };

  const formatExpiryTime = (expiresAt: string): string => {
    const expiryDate = new Date(expiresAt);
    const now = new Date();
    const diffMs = expiryDate.getTime() - now.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Expires soon';
    if (diffMins < 60) return `Expires in ${diffMins} minutes`;
    return `Expires in ${Math.floor(diffMins / 60)} hours`;
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-[#0a0e27] via-[#1a1f3a] to-[#0f1420] flex items-center justify-center p-6">
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

      <div className="w-full max-w-4xl relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Video className="h-10 w-10 text-white" />
            <h1 className="text-5xl font-bold text-white">
              VidSquad
            </h1>
          </div>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="flex items-center justify-center gap-2 mb-3"
          >
            <CheckCircle2 className="h-6 w-6 text-green-400" />
            <p className="text-white text-xl font-semibold">Video Generated Successfully!</p>
          </motion.div>
          <p className="text-white/70 text-sm mb-2">Download your video project in your preferred format</p>
          <div className="flex items-center justify-center gap-2 text-orange-400 text-sm">
            <Clock className="h-4 w-4" />
            <span>{formatExpiryTime(expiresAt)}</span>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex justify-center gap-6 mb-8"
        >
          <div className="bg-[#2a2f45]/50 backdrop-blur-xl rounded-xl px-6 py-3 border border-slate-700/30">
            <p className="text-slate-400 text-xs mb-1">Video Clips</p>
            <p className="text-white text-2xl font-bold">{clipsCount}</p>
          </div>
          <div className="bg-[#2a2f45]/50 backdrop-blur-xl rounded-xl px-6 py-3 border border-slate-700/30">
            <p className="text-slate-400 text-xs mb-1">AI Images</p>
            <p className="text-white text-2xl font-bold">{imagesCount}</p>
          </div>
        </motion.div>

        {/* Download Options */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="grid md:grid-cols-2 gap-6"
        >
          {/* Premiere Pro Card */}
          <motion.div
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.2 }}
            className="bg-[#2a2f45]/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-700/30 overflow-hidden"
          >
            <div className="p-8">
              <div className="flex items-start justify-between mb-6">
                <div className="p-3 bg-purple-600/20 rounded-xl border border-purple-500/30">
                  <FileVideo className="h-8 w-8 text-purple-400" />
                </div>
                {premiereDownloaded && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200 }}
                  >
                    <CheckCircle2 className="h-6 w-6 text-green-400" />
                  </motion.div>
                )}
              </div>
              
              <h3 className="text-xl font-bold text-white mb-2">Premiere Pro</h3>
              <p className="text-slate-400 text-sm mb-6">
                Professional XML project file compatible with Adobe Premiere Pro
              </p>
              
              <div className="space-y-2 mb-6">
                <div className="flex items-center gap-2 text-slate-300 text-sm">
                  <Sparkles className="h-4 w-4 text-purple-400" />
                  <span>Full timeline structure</span>
                </div>
                <div className="flex items-center gap-2 text-slate-300 text-sm">
                  <Sparkles className="h-4 w-4 text-purple-400" />
                  <span>All assets included</span>
                </div>
                <div className="flex items-center gap-2 text-slate-300 text-sm">
                  <Sparkles className="h-4 w-4 text-purple-400" />
                  <span>.prproj XML format</span>
                </div>
              </div>

              <Button
                onClick={handleDownloadPremiere}
                disabled={downloadingPremiere || premiereDownloaded}
                className="w-full h-12 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white shadow-lg shadow-purple-900/30 transition-all"
              >
                {downloadingPremiere ? (
                  <>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="mr-2"
                    >
                      <Package className="h-5 w-5" />
                    </motion.div>
                    Downloading...
                  </>
                ) : premiereDownloaded ? (
                  <>
                    <CheckCircle2 className="h-5 w-5 mr-2" />
                    Downloaded
                  </>
                ) : (
                  <>
                    <Download className="h-5 w-5 mr-2" />
                    Download ZIP
                  </>
                )}
              </Button>
            </div>
          </motion.div>

          {/* CapCut Card */}
          <motion.div
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.2 }}
            className="bg-[#2a2f45]/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-700/30 overflow-hidden"
          >
            <div className="p-8">
              <div className="flex items-start justify-between mb-6">
                <div className="p-3 bg-blue-600/20 rounded-xl border border-blue-500/30">
                  <FileVideo className="h-8 w-8 text-blue-400" />
                </div>
                {capcutDownloaded && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200 }}
                  >
                    <CheckCircle2 className="h-6 w-6 text-green-400" />
                  </motion.div>
                )}
              </div>
              
              <h3 className="text-xl font-bold text-white mb-2">CapCut</h3>
              <p className="text-slate-400 text-sm mb-6">
                Native CapCut project file for easy mobile and desktop editing
              </p>
              
              <div className="space-y-2 mb-6">
                <div className="flex items-center gap-2 text-slate-300 text-sm">
                  <Sparkles className="h-4 w-4 text-blue-400" />
                  <span>Mobile & desktop ready</span>
                </div>
                <div className="flex items-center gap-2 text-slate-300 text-sm">
                  <Sparkles className="h-4 w-4 text-blue-400" />
                  <span>All assets included</span>
                </div>
                <div className="flex items-center gap-2 text-slate-300 text-sm">
                  <Sparkles className="h-4 w-4 text-blue-400" />
                  <span>.ccut format</span>
                </div>
              </div>

              <Button
                onClick={handleDownloadCapcut}
                disabled={downloadingCapcut || capcutDownloaded}
                className="w-full h-12 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white shadow-lg shadow-blue-900/30 transition-all"
              >
                {downloadingCapcut ? (
                  <>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="mr-2"
                    >
                      <Package className="h-5 w-5" />
                    </motion.div>
                    Downloading...
                  </>
                ) : capcutDownloaded ? (
                  <>
                    <CheckCircle2 className="h-5 w-5 mr-2" />
                    Downloaded
                  </>
                ) : (
                  <>
                    <Download className="h-5 w-5 mr-2" />
                    Download ZIP
                  </>
                )}
              </Button>
            </div>
          </motion.div>
        </motion.div>

        {/* Info Note */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="mt-8 text-center"
        >
          <div className="bg-[#2a2f45]/50 backdrop-blur-xl rounded-xl p-4 border border-slate-700/30 mb-4">
            <p className="text-slate-400 text-sm">
              💡 Each ZIP file contains the complete project with all assets, ready to import into your preferred editor
            </p>
          </div>
          
          <Button
            onClick={onCreateNew}
            variant="outline"
            className="bg-[#353a52]/80 border-slate-700/50 text-white hover:bg-[#3d4359] hover:text-white backdrop-blur-sm"
          >
            Create Another Video
          </Button>
        </motion.div>
      </div>
    </div>
  );
}
