"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface Video {
  id: string;
  title: string;
  originalName: string;
  status: string;
  durationSeconds: number | null;
  mimeType: string;
  byteSize: number;
  createdAt: string;
}

const statusColors: Record<string, string> = {
  uploading: "text-clipmind-warning",
  queued: "text-clipmind-text-muted",
  processing: "text-clipmind-focus",
  ready: "text-clipmind-success",
  failed: "text-clipmind-danger",
};

export default function VideosPage() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<{ videos: Video[] }>("/videos")
      .then((data) => setVideos(data.videos))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-semibold">My videos</h2>
        <a
          href="/dashboard/upload"
          className="rounded-md bg-clipmind-primary px-4 py-2 text-sm font-semibold text-clipmind-bg transition-colors hover:bg-clipmind-primary-hover"
        >
          Upload video
        </a>
      </div>
      {loading ? (
        <p className="text-clipmind-text-muted">Loading...</p>
      ) : videos.length === 0 ? (
        <div className="rounded-lg border border-dashed border-clipmind-border bg-clipmind-surface p-10 text-center">
          <p className="text-clipmind-text-muted">
            No videos yet. Upload your first video to get started.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {videos.map((v) => (
            <a
              key={v.id}
              href={`/dashboard/videos/${v.id}`}
              className="rounded-lg border border-clipmind-border bg-clipmind-surface p-4 transition-colors hover:bg-clipmind-surface-raised"
            >
              <p className="font-medium truncate">{v.title}</p>
              <p className="mt-1 text-sm text-clipmind-text-muted truncate">
                {v.originalName}
              </p>
              <div className="mt-3 flex items-center justify-between">
                <span
                  className={`text-xs font-medium capitalize ${statusColors[v.status] || "text-clipmind-text-muted"}`}
                >
                  {v.status}
                </span>
                {v.durationSeconds && (
                  <span className="text-xs text-clipmind-text-muted">
                    {Math.floor(v.durationSeconds / 60)}:
                    {String(v.durationSeconds % 60).padStart(2, "0")}
                  </span>
                )}
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
