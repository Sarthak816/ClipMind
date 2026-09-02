"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface OverviewData {
  totalVideos: number;
  totalProcessed: number;
  totalDuration: number;
  totalTranscripts: number;
  totalSummaries: number;
  recentVideos: Array<{
    id: string;
    title: string;
    status: string;
    createdAt: string;
    durationSeconds: number | null;
  }>;
  processingStats: {
    queued: number;
    running: number;
    completed: number;
    failed: number;
  };
}

const statusColors: Record<string, string> = {
  uploading: "bg-clipmind-warning text-clipmind-bg",
  queued: "bg-clipmind-text-muted text-clipmind-bg",
  processing: "bg-clipmind-focus text-clipmind-bg",
  ready: "bg-clipmind-success text-clipmind-bg",
  failed: "bg-clipmind-danger text-clipmind-bg",
};

export default function DashboardOverviewPage() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<OverviewData>("/analytics/overview")
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const formatDuration = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hrs}h ${mins}m`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-clipmind-primary border-t-transparent"></div>
      </div>
    );
  }

  if (!data) return <p className="text-clipmind-danger">Failed to load overview data.</p>;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-clipmind-text">Dashboard</h1>
        <div className="flex gap-4">
          <Link
            href="/dashboard/videos"
            className="rounded-md border border-clipmind-border px-4 py-2 text-sm font-semibold text-clipmind-text transition-colors hover:bg-clipmind-surface-raised"
          >
            My Videos
          </Link>
          <Link
            href="/dashboard/upload"
            className="rounded-md bg-clipmind-primary px-4 py-2 text-sm font-semibold text-clipmind-bg transition-colors hover:bg-opacity-90"
          >
            Upload Video
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[
          { label: "Total Videos", value: data.totalVideos },
          { label: "Processed", value: data.totalProcessed },
          { label: "Total Duration", value: formatDuration(data.totalDuration) },
          { label: "Transcripts", value: data.totalTranscripts },
        ].map((stat, i) => (
          <div key={i} className="bg-clipmind-surface border border-clipmind-border rounded-lg p-6">
            <h3 className="text-sm font-medium text-clipmind-text-muted mb-2">{stat.label}</h3>
            <p className="text-3xl font-bold text-clipmind-text">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-clipmind-surface border border-clipmind-border rounded-lg p-6">
          <h2 className="text-lg font-semibold text-clipmind-text mb-4">Recent Videos</h2>
          {data.recentVideos.length === 0 ? (
            <p className="text-clipmind-text-muted">No recent videos.</p>
          ) : (
            <div className="divide-y divide-clipmind-border">
              {data.recentVideos.map((video) => (
                <div key={video.id} className="py-4 flex items-center justify-between">
                  <div className="flex flex-col">
                    <Link
                      href={`/dashboard/videos/${video.id}`}
                      className="font-medium text-clipmind-text hover:text-clipmind-primary transition-colors"
                    >
                      {video.title}
                    </Link>
                    <span className="text-xs text-clipmind-text-muted mt-1">
                      {new Date(video.createdAt).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    {video.durationSeconds && (
                      <span className="text-sm text-clipmind-text-muted">
                        {Math.floor(video.durationSeconds / 60)}:
                        {String(video.durationSeconds % 60).padStart(2, "0")}
                      </span>
                    )}
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                        statusColors[video.status] || "bg-clipmind-text-muted text-clipmind-bg"
                      }`}
                    >
                      {video.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-clipmind-surface border border-clipmind-border rounded-lg p-6">
          <h2 className="text-lg font-semibold text-clipmind-text mb-4">Processing Stats</h2>
          <div className="space-y-4">
            {[
              { label: "Queued", value: data.processingStats.queued, color: "text-clipmind-text-muted" },
              { label: "Running", value: data.processingStats.running, color: "text-clipmind-warning" },
              { label: "Completed", value: data.processingStats.completed, color: "text-clipmind-success" },
              { label: "Failed", value: data.processingStats.failed, color: "text-clipmind-danger" },
            ].map((stat, i) => (
              <div key={i} className="flex justify-between items-center">
                <span className="text-sm text-clipmind-text-muted">{stat.label}</span>
                <span className={`text-sm font-semibold ${stat.color}`}>{stat.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
