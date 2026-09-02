"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Logo from "@/components/Logo";
import { useAuth } from "@/lib/auth-context";
import { motion } from "framer-motion";
import { LayoutDashboard, Video, UploadCloud, Bookmark, History, Users, Settings, LogOut, Search } from "lucide-react";

const navItems = [
  { label: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { label: "My Videos", href: "/dashboard/videos", icon: Video },
  { label: "Upload", href: "/dashboard/upload", icon: UploadCloud },
  { label: "Bookmarks", href: "/dashboard/bookmarks", icon: Bookmark },
  { label: "History", href: "/dashboard/history", icon: History },
];

const adminItems = [
  { label: "Users", href: "/dashboard/admin/users", icon: Users },
  { label: "System Jobs", href: "/dashboard/admin/jobs", icon: Settings },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading, logout } = useAuth();
  const [hovered, setHovered] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [user, loading, router]);

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-white/20 border-t-white" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-black text-[#ededed] selection:bg-white/20">
      <aside className="hidden w-64 flex-shrink-0 border-r border-white/[0.08] bg-[#000000] p-4 lg:flex lg:flex-col">
        <div className="mb-6 px-3 pt-2">
          <Logo />
        </div>
        
        <nav className="flex-1 space-y-1">
          {navItems.map((item) => {
            const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.label}
                href={item.href}
                onMouseEnter={() => setHovered(item.label)}
                onMouseLeave={() => setHovered(null)}
                className={`group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  active ? "text-white" : "text-[#a1a1aa] hover:text-white"
                }`}
              >
                {active && (
                  <motion.div
                    layoutId="active-nav"
                    className="absolute inset-0 rounded-lg bg-white/[0.08]"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  />
                )}
                {hovered === item.label && !active && (
                  <motion.div
                    layoutId="hover-nav"
                    className="absolute inset-0 rounded-lg bg-white/[0.04]"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.15 }}
                  />
                )}
                <item.icon className={`relative z-10 h-[18px] w-[18px] ${active ? "text-white" : "text-[#a1a1aa] group-hover:text-white"}`} strokeWidth={active ? 2.5 : 2} />
                <span className="relative z-10">{item.label}</span>
              </Link>
            );
          })}
          
          {user?.role === "administrator" && (
            <div className="mt-8">
              <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-[#a1a1aa]/60">
                Administration
              </p>
              {adminItems.map((item) => {
                const active = pathname === item.href || pathname.startsWith(item.href);
                return (
                  <Link
                    key={item.label}
                    href={item.href}
                    onMouseEnter={() => setHovered(item.label)}
                    onMouseLeave={() => setHovered(null)}
                    className={`group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                      active ? "text-white" : "text-[#a1a1aa] hover:text-white"
                    }`}
                  >
                    {active && (
                      <motion.div
                        layoutId="active-nav"
                        className="absolute inset-0 rounded-lg bg-white/[0.08]"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.2 }}
                      />
                    )}
                    {hovered === item.label && !active && (
                      <motion.div
                        layoutId="hover-nav"
                        className="absolute inset-0 rounded-lg bg-white/[0.04]"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.15 }}
                      />
                    )}
                    <item.icon className={`relative z-10 h-[18px] w-[18px] ${active ? "text-white" : "text-[#a1a1aa] group-hover:text-white"}`} strokeWidth={active ? 2.5 : 2} />
                    <span className="relative z-10">{item.label}</span>
                  </Link>
                );
              })}
            </div>
          )}
        </nav>

        <div className="mt-auto border-t border-white/[0.08] pt-4">
          <div className="flex items-center gap-3 px-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-tr from-white/20 to-white/5 shadow-inner border border-white/10">
              <span className="text-xs font-bold text-white tracking-widest pl-[1px]">
                {user.displayName?.charAt(0).toUpperCase() || "U"}
              </span>
            </div>
            <div className="flex flex-1 flex-col overflow-hidden">
              <span className="truncate text-sm font-medium text-white">{user.displayName || "Welcome"}</span>
              <span className="truncate text-xs text-[#a1a1aa]">{user.role}</span>
            </div>
            <button
              onClick={() => logout()}
              className="rounded-md p-2 text-[#a1a1aa] transition-colors hover:bg-white/[0.08] hover:text-white"
              title="Log out"
            >
              <LogOut className="h-[18px] w-[18px]" strokeWidth={2} />
            </button>
          </div>
        </div>
      </aside>

      <div className="flex flex-1 flex-col min-w-0">
        <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-white/[0.08] bg-black/50 px-8 backdrop-blur-xl">
          <div className="flex flex-1 items-center gap-2 text-[#a1a1aa]">
            <Search className="h-4 w-4" />
            <input 
              type="text" 
              placeholder="Search videos, transcripts, or notes..." 
              className="h-full w-full max-w-md bg-transparent text-sm text-white placeholder-[#a1a1aa]/50 outline-none"
            />
          </div>
        </header>
        <main className="flex-1 p-8">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: [0.32, 0.72, 0, 1] }}
            className="mx-auto max-w-6xl"
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  );
}
