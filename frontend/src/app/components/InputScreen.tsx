import { useState, useEffect, useRef } from 'react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Textarea } from '@/app/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { Sparkles, Paperclip, Upload, Youtube, Video, Check, X, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/app/components/ui/dialog';

interface InputScreenProps {
  onSubmit: (script: string, duration: string, title: string) => void;
}

const PLACEHOLDERS = [
  'Enter your script here...',
  'Paste your video script...',
  'Type or paste your script...',
];

export function InputScreen({ onSubmit }: InputScreenProps) {
  const [videoModel, setVideoModel] = useState<string>('deep-production-v1');
  const [duration, setDuration] = useState<string>('30-40');
  const [promptText, setPromptText] = useState<string>('');
  const [titleText, setTitleText] = useState<string>('');
  const [referenceVideoLink, setReferenceVideoLink] = useState<string>('');
  const [showReferenceInput, setShowReferenceInput] = useState<boolean>(false);
  const [tempReferenceLink, setTempReferenceLink] = useState<string>('');
  const [currentPlaceholder, setCurrentPlaceholder] = useState<string>('');
  const [placeholderIndex, setPlaceholderIndex] = useState<number>(0);
  const [charIndex, setCharIndex] = useState<number>(0);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [showScriptDialog, setShowScriptDialog] = useState<boolean>(false);
  const [scriptText, setScriptText] = useState<string>('');
  const [scriptTitle, setScriptTitle] = useState<string>('');
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Typing animation effect
  useEffect(() => {
    if (promptText.length > 0) {
      setCurrentPlaceholder('');
      return;
    }

    const typingSpeed = isDeleting ? 50 : 100;
    const pauseTime = isDeleting ? 1000 : 2000;

    const timer = setTimeout(() => {
      const currentText = PLACEHOLDERS[placeholderIndex];

      if (!isDeleting && charIndex < currentText.length) {
        setCurrentPlaceholder(currentText.substring(0, charIndex + 1));
        setCharIndex(charIndex + 1);
      } else if (isDeleting && charIndex > 0) {
        setCurrentPlaceholder(currentText.substring(0, charIndex - 1));
        setCharIndex(charIndex - 1);
      } else if (!isDeleting && charIndex === currentText.length) {
        setTimeout(() => setIsDeleting(true), pauseTime);
      } else if (isDeleting && charIndex === 0) {
        setIsDeleting(false);
        setPlaceholderIndex((placeholderIndex + 1) % PLACEHOLDERS.length);
      }
    }, typingSpeed);

    return () => clearTimeout(timer);
  }, [charIndex, isDeleting, placeholderIndex, promptText]);

  const handleSubmit = () => {
    if (promptText.trim() && promptText.length >= 200) {
      onSubmit(promptText, duration, titleText);
    }
  };

  const handleScriptSubmit = () => {
    if (scriptText.trim()) {
      setShowScriptDialog(false);
      onSubmit(scriptText, duration, scriptTitle);
    }
  };

  const handleAddReference = () => {
    setReferenceVideoLink(tempReferenceLink);
    setShowReferenceInput(false);
    setTempReferenceLink('');
  };

  const handleCancelReference = () => {
    setShowReferenceInput(false);
    setTempReferenceLink('');
  };
  
  const maxChars = 5000;
  const minChars = 200;
  const currentChars = promptText.length;
  const charsNeeded = Math.max(0, minChars - currentChars);
  
  const maxTitleChars = 100;
  const currentTitleChars = titleText.length;

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

      <div className="w-full max-w-2xl relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-2">
            <Video className="h-9 w-9 text-white" />
            <h1 className="text-5xl font-bold text-white">
              VidSquad
            </h1>
          </div>
          <p className="text-white/80 text-sm">Your AI Video Production Studio</p>
        </motion.div>

        {/* Main Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="bg-[#2a2f45]/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-700/30 overflow-hidden"
        >
          {/* Top Dropdowns */}
          <div className="flex gap-3 p-6 pb-4">
            <div className="relative">
              <Select value={videoModel} onValueChange={setVideoModel}>
                <SelectTrigger className="bg-[#353a52] border-none text-white hover:bg-[#3d4359] transition-all h-11 pr-10">
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent className="bg-[#2a2f45] border-slate-700/50 text-white backdrop-blur-xl">
                  <SelectItem value="deep-production-v1">Deep Production V1</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Main Prompt Area */}
          <div className="px-6 pb-6 pt-6">
            <div className="relative">
              <Textarea
                ref={textareaRef}
                value={promptText}
                onChange={(e) => setPromptText(e.target.value)}
                placeholder=""
                className="h-[180px] bg-transparent border-none text-white text-base placeholder:text-slate-500 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 p-0 leading-relaxed overflow-y-auto"
                maxLength={maxChars}
              />
              
              {/* Typing Animation Placeholder */}
              {promptText.length === 0 && (
                <div className="absolute top-0 left-0 pointer-events-none text-base text-slate-500">
                  {currentPlaceholder}
                  <span className="animate-pulse">|</span>
                </div>
              )}
            </div>

            {/* Bottom Bar with Character Count and Actions */}
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-700/30">
              <div className="flex items-center gap-4">
                {/* Character Count */}
                {promptText.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-sm"
                  >
                    {charsNeeded > 0 ? (
                      <span className="text-orange-400">
                        {charsNeeded} more characters needed
                      </span>
                    ) : (
                      <span className="text-green-400">
                        Ready to generate
                      </span>
                    )}
                    <span className="text-slate-500 ml-2">
                      {currentChars}/{maxChars}
                    </span>
                  </motion.div>
                )}
              </div>

              <div className="flex items-center gap-2">
                {/* Submit Button */}
                <Button
                  onClick={handleSubmit}
                  disabled={promptText.length < minChars}
                  className="h-11 px-6 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white shadow-lg shadow-blue-900/30"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Generate Video
                </Button>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Script Insertion Button - Removed for V1 */}
      </div>
    </div>
  );
}
