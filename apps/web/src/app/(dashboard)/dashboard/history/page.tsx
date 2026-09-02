"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface HistoryItem {
  videoId: string;
  title: string;
  status: string;
  durationSeconds: number | null;
  lastViewed: string;
}

const statusColors: Record<string, string> = {
  uploading: "bg-clipmind-warning text-clipmind-bg",
  queued: "bg-clipmind-text-muted text-clipmind-bg",
  processing: "bg-clipmind-focus text-clipmind-bg",
  ready: "bg-clipmind-success text-clipmind-bg",
  failed: "bg-clipmind-danger text-clipmind-bg",
};

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<{ history: HistoryItem[] }>("/history")
      .then((data) => setHistory(data.history || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="p-6 text-clipmind-text-muted">Loading history...</p>;
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-clipmind-text mb-6">Watch History</h1>
      {history.length === 0 ? (
        <div className="bg-clipmind-surface border border-dashed border-clipmind-border rounded-lg p-10 text-center">
          <p className="text-clipmind-text-muted">No viewing history found.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {history.map((item) => (
            <Link
              key={item.videoId}
              href={`/dashboard/videos/${item.videoId}`}
              className="flex items-center justify-between bg-clipmind-surface border border-clipmind-border rounded-lg p-4 transition-colors hover:bg-clipmind-surface-raised"
            >
              <div>
                <h3 className="font-semibold text-clipmind-text">{item.title}</h3>
                <p className="text-sm text-clipmind-text-muted mt-1">
                  Viewed on {new Date(item.lastViewed).toLocaleString()}
                </p>
              </div>
              <div className="flex items-center gap-4">
                {item.durationSeconds && (
                  <span className="text-sm text-clipmind-text-muted">
                    {Math.floor(item.durationSeconds / 60)}:
                    {String(item.durationSeconds % 60).padStart(2, "0")}
                  </span>
                )}
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                    statusColors[item.status] || "bg-clipmind-text-muted text-clipmind-bg"
                  }`}
                >
                  {item.status}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
