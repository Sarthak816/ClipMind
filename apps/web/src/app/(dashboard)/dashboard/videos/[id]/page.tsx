"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";

interface Segment {
  id: string;
  sequence: number;
  startMs: number;
  endMs: number;
  text: string;
  confidence: number | null;
}

interface TranscriptData {
  id: string;
  version: number;
  language: string;
  source: string;
  body: string;
  segments: Segment[];
}

interface SummaryData {
  id: string;
  kind: string;
  content: string;
  modelName: string;
  version: number;
  createdAt: string;
}

interface KeyMomentData {
  id: string;
  startMs: number;
  endMs: number;
  title: string;
  rationale: string;
  score: number;
  rank: number;
}

interface VideoData {
  id: string;
  title: string;
  status: string;
  originalName: string;
  durationSeconds: number | null;
  mimeType?: string;
  objectKey?: string;
}

function formatMs(ms: number) {
  const totalSec = Math.floor(ms / 1000);
  const m = Math.floor(totalSec / 60);
  const s = totalSec % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function VideoDetailPage() {
  const params = useParams();
  const videoId = params.id as string;
  const [video, setVideo] = useState<VideoData | null>(null);
  const [transcript, setTranscript] = useState<TranscriptData | null>(null);
  const [summaries, setSummaries] = useState<SummaryData[]>([]);
  const [moments, setMoments] = useState<KeyMomentData[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Segment[]>([]);
  const [activeTab, setActiveTab] = useState<"summary" | "transcript">("summary");
  const [summaryKind, setSummaryKind] = useState<"short" | "detailed">("short");
  const [isBookmarked, setIsBookmarked] = useState(false);

  useEffect(() => {
    // Reset state for the new video ID to prevent UI bleed
    setVideo(null);
    setTranscript(null);
    setSummaries([]);
    setMoments([]);
    setSearchQuery("");
    setSearchResults([]);
    setIsBookmarked(false);

    let active = true;
    let intervalId: NodeJS.Timeout | null = null;

    api(`/history/view`, {
      method: "POST",
      body: { videoId },
    }).catch(() => {});

    const fetchAllData = async () => {
      try {
        const v = await api<VideoData>(`/videos/${videoId}`);
        if (!active) return;
        setVideo(v);

        if (v.status === "ready") {
          api<TranscriptData>(`/videos/${videoId}/transcripts/current`)
            .then((t) => active && setTranscript(t))
            .catch(() => {});
          api<{ summaries: SummaryData[] }>(`/videos/${videoId}/summaries`)
            .then((d) => active && setSummaries(d.summaries))
            .catch(() => {});
          api<{ moments: KeyMomentData[] }>(`/videos/${videoId}/key-moments`)
            .then((d) => active && setMoments(d.moments))
            .catch(() => {});
          
          if (intervalId) {
            clearInterval(intervalId);
            intervalId = null;
          }
        }
      } catch {
        // ignore
      }
    };

    // Fetch immediately
    fetchAllData();

    // Start polling, and we will clear it inside fetchAllData once it is ready
    intervalId = setInterval(fetchAllData, 3000);

    return () => {
      active = false;
      if (intervalId) clearInterval(intervalId);
    };
  }, [videoId]);


  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    try {
      const data = await api<{ results: Segment[] }>(
        `/videos/${videoId}/search?q=${encodeURIComponent(searchQuery)}`,
      );
      setSearchResults(data.results);
    } catch {
      setSearchResults([]);
    }
  };

  const activeSummary = summaries.find((s) => s.kind === summaryKind);

  return (
    <div className="mx-auto max-w-5xl">
      {video?.mimeType === "video/youtube" && video?.objectKey && (
        <div className="mb-6 aspect-video w-full overflow-hidden rounded-lg border border-clipmind-border">
          <iframe
            className="h-full w-full"
            src={`https://www.youtube.com/embed/${new URL(video.objectKey).searchParams.get("v")}`}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      )}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-semibold">{video?.title || "Loading..."}</h2>
            {video && (
              <button
                onClick={async () => {
                  try {
                    await api("/bookmarks", {
                      method: "POST",
                      body: { videoId: video.id },
                    });
                    setIsBookmarked(!isBookmarked);
                  } catch (e) {
                    console.error(e);
                  }
                }}
                className={`transition-colors ${isBookmarked ? "text-clipmind-primary" : "text-clipmind-text-muted hover:text-clipmind-primary"}`}
                title="Bookmark"
              >
                <svg className="w-5 h-5" fill={isBookmarked ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                </svg>
              </button>
            )}
          </div>
          {video && (
            <p className="mt-1 text-sm text-clipmind-text-muted">
              {video.originalName}
              {video.durationSeconds &&
                ` \u2022 ${Math.floor(video.durationSeconds / 60)}:${String(video.durationSeconds % 60).padStart(2, "0")}`}
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab("summary")}
            className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === "summary"
                ? "bg-clipmind-primary text-clipmind-bg"
                : "border border-clipmind-border text-clipmind-text-muted hover:bg-clipmind-surface-raised"
            }`}
          >
            Summary
          </button>
          <button
            onClick={() => setActiveTab("transcript")}
            className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === "transcript"
                ? "bg-clipmind-primary text-clipmind-bg"
                : "border border-clipmind-border text-clipmind-text-muted hover:bg-clipmind-surface-raised"
            }`}
          >
            Transcript
          </button>
        </div>
      </div>

      {activeTab === "summary" && (
        <div>
          {/* Key moments */}
          {moments.length > 0 && (
            <div className="mb-6">
              <h3 className="mb-3 text-lg font-semibold">Key moments</h3>
              <div className="flex flex-col gap-2">
                {moments.map((m) => (
                  <button
                    key={m.id}
                    className="flex items-start gap-3 rounded-lg border border-clipmind-border bg-clipmind-surface p-3 text-left transition-colors hover:bg-clipmind-surface-raised"
                  >
                    <span className="mt-0.5 rounded bg-clipmind-primary/20 px-2 py-0.5 text-xs font-mono font-medium text-clipmind-primary">
                      {formatMs(m.startMs)}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{m.title}</p>
                      <p className="mt-1 text-xs text-clipmind-text-muted line-clamp-2">
                        {m.rationale}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Summary */}
          <div className="rounded-lg border border-clipmind-border bg-clipmind-surface p-6">
            <div className="mb-4 flex gap-2">
              <button
                onClick={() => setSummaryKind("short")}
                className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                  summaryKind === "short"
                    ? "bg-clipmind-surface-raised text-clipmind-text"
                    : "text-clipmind-text-muted hover:text-clipmind-text"
                }`}
              >
                Short summary
              </button>
              <button
                onClick={() => setSummaryKind("detailed")}
                className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                  summaryKind === "detailed"
                    ? "bg-clipmind-surface-raised text-clipmind-text"
                    : "text-clipmind-text-muted hover:text-clipmind-text"
                }`}
              >
                Detailed summary
              </button>
            </div>
            {activeSummary ? (
              <div>
                <p className="text-sm leading-relaxed text-clipmind-text whitespace-pre-wrap">
                  {activeSummary.content}
                </p>
                <p className="mt-4 text-xs text-clipmind-text-muted">
                  AI-generated ({activeSummary.modelName}) &bull; v{activeSummary.version}
                </p>
              </div>
            ) : video?.status === "processing" || video?.status === "queued" ? (
              <div className="flex flex-col items-center justify-center py-8">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-clipmind-primary border-t-transparent mb-3"></div>
                <p className="text-sm text-clipmind-text-muted">
                  AI processing in progress... Generating transcripts and summaries.
                </p>
              </div>
            ) : (
              <p className="text-sm text-clipmind-text-muted">
                No summary available yet. Process the video to generate a summary.
              </p>
            )}
          </div>
        </div>
      )}

      {activeTab === "transcript" && (
        <div>
          {/* Search */}
          <div className="mb-4 flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Search transcript..."
              className="flex-1 rounded-md border border-clipmind-border bg-clipmind-surface-raised px-4 py-2.5 text-sm text-clipmind-text outline-none focus:border-clipmind-focus focus:shadow-focus"
            />
            <button
              onClick={handleSearch}
              className="rounded-md border border-clipmind-border px-4 py-2.5 text-sm font-medium text-clipmind-text-muted transition-colors hover:bg-clipmind-surface-raised"
            >
              Search
            </button>
          </div>

          {/* Segments */}
          <div className="rounded-lg border border-clipmind-border bg-clipmind-surface">
            {searchResults.length > 0 && (
              <div className="border-b border-clipmind-border px-4 py-2">
                <p className="text-xs text-clipmind-text-muted">
                  {searchResults.length} result{searchResults.length !== 1 ? "s" : ""} found
                </p>
              </div>
            )}
            {transcript && transcript.segments.length > 0 ? (
              <div className="divide-y divide-clipmind-border">
                {(searchResults.length > 0 ? searchResults : transcript.segments).map(
                  (seg) => (
                    <div key={seg.id} className="flex gap-3 px-4 py-3">
                      <span className="mt-0.5 text-xs font-mono text-clipmind-text-muted whitespace-nowrap">
                        {formatMs(seg.startMs)}
                      </span>
                      <p className="text-sm leading-relaxed">{seg.text}</p>
                    </div>
                  ),
                )}
              </div>
            ) : video?.status === "processing" || video?.status === "queued" ? (
              <div className="p-10 text-center flex flex-col items-center justify-center">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-clipmind-primary border-t-transparent mb-3"></div>
                <p className="text-sm text-clipmind-text-muted">
                  Transcribing audio in progress... Please wait.
                </p>
              </div>
            ) : (
              <div className="p-10 text-center">
                <p className="text-sm text-clipmind-text-muted">
                  No transcript available yet. Process the video to generate a transcript.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
