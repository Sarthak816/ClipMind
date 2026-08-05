import Link from "next/link";
import Logo from "@/components/Logo";

const navItems = [
  { label: "Dashboard", href: "/dashboard", active: true },
  { label: "My videos", href: "/dashboard/videos" },
  { label: "Upload", href: "/dashboard/upload" },
  { label: "Bookmarks", href: "/dashboard/bookmarks" },
  { label: "History", href: "/dashboard/history" },
];

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
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
                item.active
                  ? "bg-clipmind-surface-raised text-clipmind-text"
                  : "text-clipmind-text-muted hover:bg-clipmind-surface-raised hover:text-clipmind-text"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col">
        {/* Top bar */}
        <header className="flex items-center justify-between border-b border-clipmind-border px-6 py-4">
          <h1 className="text-lg font-semibold">Dashboard</h1>
          <div className="flex items-center gap-3">
            <span className="text-sm text-clipmind-text-muted">
              Welcome back
            </span>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-clipmind-primary text-xs font-bold text-clipmind-bg">
              U
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 p-6">
          <p className="mb-6 text-clipmind-text-muted">
            Turn a long video into something you can read.
          </p>
          <Link
            href="/dashboard/upload"
            className="mb-8 inline-block rounded-md bg-clipmind-primary px-5 py-3 text-sm font-semibold text-clipmind-bg transition-colors hover:bg-clipmind-primary-hover"
          >
            Summarize a video
          </Link>

          <h2 className="mb-4 text-lg font-semibold">Recent videos</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {/* Empty state */}
            <div className="col-span-full rounded-lg border border-dashed border-clipmind-border bg-clipmind-surface p-10 text-center">
              <p className="text-clipmind-text-muted">
                No videos yet. Upload your first video to get started.
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
