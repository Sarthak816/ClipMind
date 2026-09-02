"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface AdminUser {
  id: string;
  email: string;
  displayName: string;
  role: string;
  status: string;
  createdAt: string;
}

const roleColors: Record<string, string> = {
  administrator: "bg-clipmind-danger text-clipmind-bg",
  creator: "bg-clipmind-primary text-clipmind-bg",
  educator: "bg-clipmind-warning text-clipmind-bg",
  learner: "bg-clipmind-success text-clipmind-bg",
};

const statusColors: Record<string, string> = {
  active: "bg-clipmind-success text-clipmind-bg",
  suspended: "bg-clipmind-danger text-clipmind-bg",
};

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<{ users: AdminUser[] }>("/admin/users")
      .then((data) => setUsers(data.users || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="p-6 text-clipmind-text-muted">Loading users...</p>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-clipmind-text mb-6">Manage Users</h1>
      <div className="bg-clipmind-surface border border-clipmind-border rounded-lg overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-clipmind-border bg-clipmind-surface-raised">
              <th className="p-4 text-sm font-semibold text-clipmind-text-muted">Name</th>
              <th className="p-4 text-sm font-semibold text-clipmind-text-muted">Email</th>
              <th className="p-4 text-sm font-semibold text-clipmind-text-muted">Role</th>
              <th className="p-4 text-sm font-semibold text-clipmind-text-muted">Status</th>
              <th className="p-4 text-sm font-semibold text-clipmind-text-muted">Joined Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-clipmind-border">
            {users.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-4 text-center text-clipmind-text-muted">
                  No users found.
                </td>
              </tr>
            ) : (
              users.map((user) => (
                <tr key={user.id} className="hover:bg-clipmind-surface-raised transition-colors">
                  <td className="p-4 text-sm font-medium text-clipmind-text">{user.displayName || "Unknown"}</td>
                  <td className="p-4 text-sm text-clipmind-text-muted">{user.email}</td>
                  <td className="p-4 text-sm">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${roleColors[user.role] || "bg-clipmind-text-muted text-clipmind-bg"}`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="p-4 text-sm">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${statusColors[user.status] || "bg-clipmind-text-muted text-clipmind-bg"}`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="p-4 text-sm text-clipmind-text-muted">
                    {new Date(user.createdAt).toLocaleDateString()}
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
