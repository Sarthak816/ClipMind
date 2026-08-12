"use client";

import { useState, useRef } from "react";
import { api } from "@/lib/api";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const allowed = ["video/mp4", "video/quicktime", "video/webm", "video/x-msvideo"];
  const maxSize = 500 * 1024 * 1024;

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    validate(f);
  };

  const validate = (f: File) => {
    setError("");
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
    try {
      const intent = await api<{
        videoId: string;
        objectKey: string;
      }>("/videos/upload-intent", {
        method: "POST",
        body: {
          fileName: file.name,
          mimeType: file.type,
          byteSize: file.size,
        },
      });

      await api(`/videos/${intent.videoId}/complete-upload`, {
        method: "POST",
      });

      await api(`/videos/${intent.videoId}/process`, {
        method: "POST",
      });

      setStatus("Upload complete! Processing started.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-lg">
      <h2 className="mb-6 text-xl font-semibold">Upload a video</h2>
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => inputRef.current?.click()}
        className="cursor-pointer rounded-lg border-2 border-dashed border-clipmind-border bg-clipmind-surface p-10 text-center transition-colors hover:border-clipmind-primary"
      >
        <input
          ref={inputRef}
          type="file"
          accept=".mp4,.mov,.webm,.avi"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && validate(e.target.files[0])}
        />
        {file ? (
          <div>
            <p className="font-medium">{file.name}</p>
            <p className="mt-1 text-sm text-clipmind-text-muted">
              {(file.size / 1024 / 1024).toFixed(1)} MB
            </p>
          </div>
        ) : (
          <div>
            <p className="font-medium">
              Drop MP4, MOV, WebM or AVI here, or choose a file
            </p>
            <p className="mt-2 text-sm text-clipmind-text-muted">
              Up to 500 MB &bull; Up to 60 minutes &bull; Your video stays
              private
            </p>
          </div>
        )}
      </div>

      {error && (
        <div
          role="alert"
          className="mt-4 rounded-md border border-clipmind-danger/30 bg-clipmind-danger/10 px-4 py-3 text-sm text-clipmind-danger"
        >
          {error}
        </div>
      )}

      {status && (
        <div className="mt-4 rounded-md border border-clipmind-success/30 bg-clipmind-success/10 px-4 py-3 text-sm text-clipmind-success">
          {status}
        </div>
      )}

      {file && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="mt-6 w-full rounded-md bg-clipmind-primary px-4 py-3 font-semibold text-clipmind-bg transition-colors hover:bg-clipmind-primary-hover disabled:cursor-not-allowed disabled:opacity-45"
        >
          {uploading ? "Uploading..." : "Upload and summarize"}
        </button>
      )}
    </div>
  );
}
