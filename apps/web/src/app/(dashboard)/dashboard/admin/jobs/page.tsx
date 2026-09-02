"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface AdminJob {
  id: string;
  videoId: string;
  videoTitle: string;
  kind: string;
  status: string;
  attempt: number;
  progress: number;
  errorMessage: string | null;
  startedAt: string | null;
  finishedAt: string | null;
  createdAt: string;
}

const statusColors: Record<string, string> = {
  completed: "bg-clipmind-success text-clipmind-bg",
  running: "bg-clipmind-warning text-clipmind-bg",
  queued: "bg-clipmind-text-muted text-clipmind-bg",
  failed: "bg-clipmind-danger text-clipmind-bg",
};

const kindColors: Record<string, string> = {
  extract_audio: "text-blue-400 border-blue-400",
  transcribe: "text-purple-400 border-purple-400",
  summarize: "text-green-400 border-green-400",
  key_moments: "text-yellow-400 border-yellow-400",
};

export default function AdminJobsPage() {
  const [jobs, setJobs] = useState<AdminJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    const fetchJobs = () => {
      api<{ jobs: AdminJob[] }>("/admin/jobs")
        .then((data) => {
          if (active) setJobs(data.jobs || []);
        })
        .catch(() => {})
        .finally(() => {
          if (active) setLoading(false);
        });
    };

    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  if (loading) {
    return <p className="p-6 text-clipmind-text-muted">Loading jobs...</p>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-clipmind-text mb-6">Job Queue Monitor</h1>
      <div className="bg-clipmind-surface border border-clipmind-border rounded-lg overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-clipmind-border bg-clipmind-surface-raised">
              <th className="p-4 text-sm font-semibold text-clipmind-text-muted">Video Title</th>
              <th className="p-4 text-sm font-semibold text-clipmind-text-muted">Job Type</th>
              <th className="p-4 text-sm font-semibold text-clipmind-text-muted">Status</th>
              <th className="p-4 text-sm font-semibold text-clipmind-text-muted">Progress</th>
              <th className="p-4 text-sm font-semibold text-clipmind-text-muted">Attempts</th>
              <th className="p-4 text-sm font-semibold text-clipmind-text-muted">Started</th>
              <th className="p-4 text-sm font-semibold text-clipmind-text-muted">Finished / Error</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-clipmind-border">
            {jobs.length === 0 ? (
              <tr>
                <td colSpan={7} className="p-4 text-center text-clipmind-text-muted">
                  No jobs found.
                </td>
              </tr>
            ) : (
              jobs.map((job) => (
                <tr key={job.id} className="hover:bg-clipmind-surface-raised transition-colors">
                  <td className="p-4 text-sm font-medium text-clipmind-text truncate max-w-xs" title={job.videoTitle}>
                    {job.videoTitle}
                  </td>
                  <td className="p-4 text-sm">
                    <span className={`px-2 py-0.5 rounded border text-xs font-semibold ${kindColors[job.kind] || "text-clipmind-text border-clipmind-border"}`}>
                      {job.kind}
                    </span>
                  </td>
                  <td className="p-4 text-sm">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${statusColors[job.status] || "bg-clipmind-text-muted text-clipmind-bg"}`}>
                      {job.status}
                    </span>
                  </td>
                  <td className="p-4 text-sm">
                    <div className="w-full bg-clipmind-surface-raised rounded-full h-2">
                      <div
                        className="bg-clipmind-primary h-2 rounded-full transition-all duration-500"
                        style={{ width: `${job.progress}%` }}
                      ></div>
                    </div>
                  </td>
                  <td className="p-4 text-sm text-clipmind-text-muted">{job.attempt}</td>
                  <td className="p-4 text-sm text-clipmind-text-muted">
                    {job.startedAt ? new Date(job.startedAt).toLocaleTimeString() : "-"}
                  </td>
                  <td className="p-4 text-sm text-clipmind-text-muted truncate max-w-xs">
                    {job.errorMessage ? (
                      <span className="text-clipmind-danger" title={job.errorMessage}>
                        {job.errorMessage}
                      </span>
                    ) : job.finishedAt ? (
                      new Date(job.finishedAt).toLocaleTimeString()
                    ) : (
                      "-"
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
