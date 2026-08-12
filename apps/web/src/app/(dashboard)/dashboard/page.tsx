"use client";

import { useAuth } from "@/lib/auth-context";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div>
      <p className="mb-6 text-clipmind-text-muted">
        Turn a long video into something you can read.
      </p>
      <a
        href="/dashboard/upload"
        className="mb-8 inline-block rounded-md bg-clipmind-primary px-5 py-3 text-sm font-semibold text-clipmind-bg transition-colors hover:bg-clipmind-primary-hover"
      >
        Summarize a video
      </a>

      <h2 className="mb-4 text-lg font-semibold">Recent videos</h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <div className="col-span-full rounded-lg border border-dashed border-clipmind-border bg-clipmind-surface p-10 text-center">
          <p className="text-clipmind-text-muted">
            No videos yet. Upload your first video to get started.
          </p>
        </div>
      </div>
    </div>
  );
}
