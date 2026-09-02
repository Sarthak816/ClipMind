"use client";

import { useState, useRef } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, Link as LinkIcon, FileVideo, AlertCircle, CheckCircle2, ArrowRight } from "lucide-react";

export default function UploadPage() {
  const [activeTab, setActiveTab] = useState<"file" | "youtube">("file");
  const [isHovering, setIsHovering] = useState(false);
  
  // File upload state
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [processedVideoId, setProcessedVideoId] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // YouTube state
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [youtubeTitle, setYoutubeTitle] = useState("");

  const allowed = ["video/mp4", "video/quicktime", "video/webm", "video/x-msvideo"];
  const maxSize = 500 * 1024 * 1024;

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsHovering(false);
    const f = e.dataTransfer.files[0];
    validate(f);
  };

  const validate = (f: File) => {
    setError("");
    setStatus("");
    setProcessedVideoId(null);
    if (!allowed.includes(f.type)) {
      setError("Unsupported file type. Use MP4, MOV, WebM or AVI.");
      return;
    }
    if (f.size > maxSize) {
      setError("File too large. Maximum size is 500 MB.");
      return;
    }
    setFile(f);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError("");
    setStatus("");
    setProcessedVideoId(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      
      const token = localStorage.getItem("accessToken");
      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;
      
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
      const uploadRes = await fetch(`${API_URL}/videos/upload`, {
        method: "POST",
        headers,
        body: formData
      });
      
      if (!uploadRes.ok) {
        throw new Error("Upload failed. Make sure the file is an MP4.");
      }
      
      const data = await uploadRes.json();

      await api(`/videos/${data.videoId}/process`, {
        method: "POST",
      });

      setStatus("File successfully uploaded and processing started in background!");
      setProcessedVideoId(data.videoId);
      setFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleYouTubeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!youtubeUrl.trim()) return;
    setUploading(true);
    setError("");
    setStatus("");
    setProcessedVideoId(null);
    try {
      const video = await api<{
        videoId: string;
        title: string;
      }>("/videos/youtube", {
        method: "POST",
        body: {
          url: youtubeUrl.trim(),
          title: youtubeTitle.trim() || undefined,
        },
      });

      setStatus(`YouTube Video "${video.title}" registered! Starting background processing...`);

      await api(`/videos/${video.videoId}/process`, {
        method: "POST",
      });

      setStatus(`YouTube Video "${video.title}" added and processing started successfully!`);
      setProcessedVideoId(video.videoId);
      setYoutubeUrl("");
      setYoutubeTitle("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to import YouTube video");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-8">
        <h2 className="text-3xl font-semibold tracking-tight text-white">Upload Video</h2>
        <p className="mt-2 text-sm text-[#a1a1aa]">Add a new video to generate transcripts, summaries, and key moments.</p>
      </div>
      
      <div className="mb-8 flex gap-1 rounded-lg border border-white/[0.08] bg-white/[0.02] p-1 shadow-inner">
        <button
          onClick={() => {
            setActiveTab("file");
            setError("");
            setStatus("");
            setProcessedVideoId(null);
          }}
          className={`relative flex flex-1 items-center justify-center gap-2 rounded-md py-2.5 text-sm font-medium transition-colors ${
            activeTab === "file" ? "text-white" : "text-[#a1a1aa] hover:text-white"
          }`}
        >
          {activeTab === "file" && (
            <motion.div
              layoutId="upload-tab"
              className="absolute inset-0 rounded-md bg-white/[0.08] shadow-sm border border-white/[0.04]"
              initial={false}
              transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
            />
          )}
          <UploadCloud className="relative z-10 h-4 w-4" />
          <span className="relative z-10">File Upload</span>
        </button>
        <button
          onClick={() => {
            setActiveTab("youtube");
            setError("");
            setStatus("");
            setProcessedVideoId(null);
          }}
          className={`relative flex flex-1 items-center justify-center gap-2 rounded-md py-2.5 text-sm font-medium transition-colors ${
            activeTab === "youtube" ? "text-white" : "text-[#a1a1aa] hover:text-white"
          }`}
        >
          {activeTab === "youtube" && (
            <motion.div
              layoutId="upload-tab"
              className="absolute inset-0 rounded-md bg-white/[0.08] shadow-sm border border-white/[0.04]"
              initial={false}
              transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
            />
          )}
          <LinkIcon className="relative z-10 h-4 w-4" />
          <span className="relative z-10">YouTube Link</span>
        </button>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === "file" ? (
            <div>
              <div
                onDrop={handleDrop}
                onDragOver={(e) => { e.preventDefault(); setIsHovering(true); }}
                onDragLeave={() => setIsHovering(false)}
                onClick={() => inputRef.current?.click()}
                className={`group relative flex cursor-pointer flex-col items-center justify-center overflow-hidden rounded-xl border-2 border-dashed p-12 text-center transition-all ${
                  isHovering 
                    ? "border-white/40 bg-white/[0.04]" 
                    : "border-white/[0.1] bg-black hover:border-white/20 hover:bg-white/[0.02]"
                }`}
              >
                <div className="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
                
                <input
                  ref={inputRef}
                  type="file"
                  accept=".mp4,.mov,.webm,.avi"
                  className="hidden"
                  onChange={(e) => e.target.files?.[0] && validate(e.target.files[0])}
                />
                
                <div className="relative z-10 mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-white/[0.04] border border-white/[0.08] shadow-inner">
                  <UploadCloud className={`h-8 w-8 transition-colors ${isHovering ? "text-white" : "text-[#a1a1aa]"}`} strokeWidth={1.5} />
                </div>

                {file ? (
                  <div className="relative z-10">
                    <p className="font-semibold text-white">{file.name}</p>
                    <p className="mt-2 text-sm text-[#a1a1aa]">
                      {(file.size / 1024 / 1024).toFixed(1)} MB &bull; Ready to upload
                    </p>
                  </div>
                ) : (
                  <div className="relative z-10">
                    <p className="text-base font-medium text-white">
                      Click to upload <span className="text-[#a1a1aa] font-normal">or drag and drop</span>
                    </p>
                    <p className="mt-2 text-sm text-[#a1a1aa]">
                      MP4, MOV, WebM or AVI (max. 500MB)
                    </p>
                  </div>
                )}
              </div>

              {file && (
                <motion.button
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  onClick={handleUpload}
                  disabled={uploading}
                  className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-white px-4 py-3 text-sm font-semibold text-black transition-all hover:bg-white/90 focus:ring-4 focus:ring-white/20 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {uploading ? (
                    <>
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-black/20 border-t-black" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <FileVideo className="h-4 w-4" />
                      Upload and Process Video
                    </>
                  )}
                </motion.button>
              )}
            </div>
          ) : (
            <form onSubmit={handleYouTubeSubmit} className="flex flex-col gap-5 rounded-xl border border-white/[0.08] bg-black p-6 shadow-xl">
              <div>
                <label htmlFor="youtube-url" className="mb-2 block text-sm font-medium text-[#a1a1aa]">
                  YouTube Video URL
                </label>
                <div className="relative">
                  <LinkIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#a1a1aa]" />
                  <input
                    id="youtube-url"
                    type="url"
                    required
                    value={youtubeUrl}
                    onChange={(e) => setYoutubeUrl(e.target.value)}
                    className="w-full rounded-lg border border-white/[0.1] bg-white/[0.03] pl-10 pr-4 py-2.5 text-sm text-white outline-none transition-all focus:border-white/30 focus:bg-white/[0.05] focus:ring-4 focus:ring-white/5"
                    placeholder="https://youtube.com/watch?v=..."
                  />
                </div>
              </div>
              <div>
                <label htmlFor="youtube-title" className="mb-2 block text-sm font-medium text-[#a1a1aa]">
                  Custom Title <span className="text-[#a1a1aa]/50 font-normal">(Optional)</span>
                </label>
                <input
                  id="youtube-title"
                  type="text"
                  value={youtubeTitle}
                  onChange={(e) => setYoutubeTitle(e.target.value)}
                  className="w-full rounded-lg border border-white/[0.1] bg-white/[0.03] px-4 py-2.5 text-sm text-white outline-none transition-all focus:border-white/30 focus:bg-white/[0.05] focus:ring-4 focus:ring-white/5"
                  placeholder="Leave blank to auto-fetch"
                />
              </div>
              
              <button
                type="submit"
                disabled={uploading || !youtubeUrl}
                className="mt-2 flex w-full items-center justify-center gap-2 rounded-lg bg-white px-4 py-3 text-sm font-semibold text-black transition-all hover:bg-white/90 focus:ring-4 focus:ring-white/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {uploading ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-black/20 border-t-black" />
                    Importing...
                  </>
                ) : (
                  <>
                    <UploadCloud className="h-4 w-4" />
                    Import and Process
                  </>
                )}
              </button>
            </form>
          )}
        </motion.div>
      </AnimatePresence>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 overflow-hidden"
          >
            <div className="flex items-center gap-3 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-500">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <p>{error}</p>
            </div>
          </motion.div>
        )}

        {status && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 overflow-hidden"
          >
            <div className="flex items-center gap-3 rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-500">
              <CheckCircle2 className="h-4 w-4 flex-shrink-0" />
              <p>{status}</p>
            </div>
          </motion.div>
        )}

        {processedVideoId && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 overflow-hidden"
          >
            <Link
              href={`/dashboard/videos/${processedVideoId}`}
              className="group flex items-center justify-between rounded-lg border border-white/[0.1] bg-white/[0.02] px-4 py-3 text-sm font-medium text-white transition-all hover:bg-white/[0.04]"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/[0.08]">
                  <FileVideo className="h-4 w-4" />
                </div>
                <span>View Processing Status</span>
              </div>
              <ArrowRight className="h-4 w-4 text-[#a1a1aa] transition-transform group-hover:translate-x-1 group-hover:text-white" />
            </Link>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
