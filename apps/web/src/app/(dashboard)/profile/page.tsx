"use client";

import { useAuth } from "@/lib/auth-context";

export default function ProfilePage() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="max-w-lg">
      <h2 className="mb-6 text-xl font-semibold">Profile</h2>
      <div className="rounded-lg border border-clipmind-border bg-clipmind-surface p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-clipmind-primary text-xl font-bold text-clipmind-bg">
            {user.displayName.charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="font-semibold">{user.displayName}</p>
            <p className="text-sm text-clipmind-text-muted">{user.email}</p>
          </div>
        </div>
        <div className="space-y-3 border-t border-clipmind-border pt-4">
          <div className="flex justify-between">
            <span className="text-sm text-clipmind-text-muted">Role</span>
            <span className="text-sm font-medium capitalize">{user.role}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-clipmind-text-muted">Status</span>
            <span className="text-sm font-medium capitalize">{user.status}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-clipmind-text-muted">User ID</span>
            <span className="font-mono text-xs text-clipmind-text-muted">
              {user.id}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
