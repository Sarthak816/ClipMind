"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import Logo from "@/components/Logo";
import { useAuth } from "@/lib/auth-context";

const navItems = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "My videos", href: "/dashboard/videos" },
  { label: "Upload", href: "/dashboard/upload" },
  { label: "Bookmarks", href: "/dashboard/bookmarks" },
  { label: "History", href: "/dashboard/history" },
];

const adminItems = [
  { label: "Users", href: "/dashboard/admin/users" },
  { label: "Jobs", href: "/dashboard/admin/jobs" },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-60 flex-shrink-0 border-r border-clipmind-border bg-clipmind-surface p-4 lg:block">
        <div className="mb-8 px-2">
          <Logo />
        </div>
        <nav className="flex flex-col gap-1">
          {navItems.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                pathname === item.href
                  ? "bg-clipmind-surface-raised text-clipmind-text"
                  : "text-clipmind-text-muted hover:bg-clipmind-surface-raised hover:text-clipmind-text"
              }`}
            >
              {item.label}
            </Link>
          ))}
          {user?.role === "administrator" && (
            <>
              <div className="my-2 border-t border-clipmind-border" />
              <p className="px-3 py-1 text-xs font-semibold uppercase text-clipmind-text-muted">
                Admin
              </p>
              {adminItems.map((item) => (
                <Link
                  key={item.label}
                  href={item.href}
                  className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                    pathname === item.href
                      ? "bg-clipmind-surface-raised text-clipmind-text"
                      : "text-clipmind-text-muted hover:bg-clipmind-surface-raised hover:text-clipmind-text"
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </>
          )}
        </nav>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-clipmind-border px-6 py-4">
          <h1 className="text-lg font-semibold">Dashboard</h1>
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard/profile"
              className="text-sm text-clipmind-text-muted hover:text-clipmind-text"
            >
              {user?.displayName || "Welcome"}
            </Link>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-clipmind-primary text-xs font-bold text-clipmind-bg">
              {user?.displayName?.charAt(0)?.toUpperCase() || "U"}
            </div>
            <button
              onClick={() => logout()}
              className="rounded-md px-3 py-1.5 text-xs font-medium text-clipmind-text-muted transition-colors hover:bg-clipmind-surface-raised hover:text-clipmind-text"
            >
              Log out
            </button>
          </div>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
