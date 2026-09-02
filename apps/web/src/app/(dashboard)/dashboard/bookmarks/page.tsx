"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface Bookmark {
  id: string;
  videoId: string;
  videoTitle: string;
  momentId: string | null;
  note: string | null;
  createdAt: string;
}

export default function BookmarksPage() {
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBookmarks();
  }, []);

  const fetchBookmarks = () => {
    setLoading(true);
    api<{ bookmarks: Bookmark[] }>("/bookmarks")
      .then((data) => setBookmarks(data.bookmarks || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    if (!confirm("Remove this bookmark?")) return;
    try {
      await api(`/bookmarks/${id}`, { method: "DELETE" });
      setBookmarks(bookmarks.filter((b) => b.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <p className="p-6 text-clipmind-text-muted">Loading bookmarks...</p>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-clipmind-text mb-6">Bookmarks</h1>
      {bookmarks.length === 0 ? (
        <div className="bg-clipmind-surface border border-dashed border-clipmind-border rounded-lg p-10 text-center">
          <p className="text-clipmind-text-muted">No bookmarks found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {bookmarks.map((bookmark) => (
            <Link
              key={bookmark.id}
              href={`/dashboard/videos/${bookmark.videoId}`}
              className="block bg-clipmind-surface border border-clipmind-border rounded-lg p-5 transition-colors hover:bg-clipmind-surface-raised relative group"
            >
              <h3 className="font-semibold text-clipmind-text truncate pr-8">{bookmark.videoTitle}</h3>
              <p className="text-sm text-clipmind-text-muted mt-2 mb-4 line-clamp-2">
                {bookmark.note || "No note provided"}
              </p>
              <p className="text-xs text-clipmind-text-muted">
                {new Date(bookmark.createdAt).toLocaleDateString()}
              </p>
              <button
                onClick={(e) => handleDelete(e, bookmark.id)}
                className="absolute top-4 right-4 text-clipmind-text-muted hover:text-clipmind-danger opacity-0 group-hover:opacity-100 transition-opacity"
                title="Remove Bookmark"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
