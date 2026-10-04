"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Sprout,
  Image as ImageIcon,
  ExternalLink,
  LogOut,
  ShieldAlert,
  Menu,
  X,
  ChevronRight,
  Database,
  Leaf,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function AdminControlPanelLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAdmin, loading, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    if (!loading && (!user || !isAdmin)) {
      router.push("/login");
    }
  }, [user, isAdmin, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#060907] flex flex-col items-center justify-center text-zinc-400">
        <div className="relative">
          <div className="h-16 w-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 animate-pulse">
            <Sprout className="h-8 w-8" />
          </div>
          <div className="absolute inset-0 rounded-2xl border-2 border-emerald-500 border-t-transparent animate-spin" />
        </div>
        <p className="mt-6 text-sm tracking-wide text-zinc-300">
          Authenticating Administrator Session...
        </p>
      </div>
    );
  }

  if (!user || !isAdmin) {
    return (
      <div className="min-h-screen bg-[#060907] flex flex-col items-center justify-center p-6 text-center">
        <div className="h-14 w-14 rounded-2xl bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400 mb-4">
          <ShieldAlert className="h-7 w-7" />
        </div>
        <h2 className="text-xl font-bold text-white">Access Denied</h2>
        <p className="mt-2 max-w-sm text-sm text-zinc-400">
          You must be authenticated with an authorized administrator account to access the control panel.
        </p>
        <button
          onClick={() => router.push("/login")}
          className="mt-6 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black px-5 py-2.5 text-xs font-semibold uppercase tracking-wider transition-all"
        >
          Proceed to Login
        </button>
      </div>
    );
  }

  const navItems = [
    {
      label: "Dashboard",
      href: "/agri-control-panel/dashboard",
      icon: LayoutDashboard,
      badge: null,
    },
    {
      label: "Crop Management",
      href: "/agri-control-panel/crops",
      icon: Sprout,
      badge: "25",
    },
    {
      label: "Automated Images",
      href: "/agri-control-panel/images",
      icon: ImageIcon,
      badge: "Wikimedia",
    },
  ];

  return (
    <div className="min-h-screen bg-[#060907] text-zinc-100 flex flex-col md:flex-row">
      {/* Sidebar (Desktop) */}
      <aside className="hidden md:flex md:w-64 flex-col border-r border-white/[0.08] bg-[#070c09]/95 backdrop-blur-xl shrink-0 z-30">
        {/* Brand Header */}
        <div className="h-16 px-6 flex items-center gap-3 border-b border-white/[0.08]">
          <div className="h-9 w-9 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shadow-glow">
            <Leaf className="h-5 w-5" />
          </div>
          <div>
            <span className="font-bold text-sm tracking-tight text-white block">
              AgriControl CMS
            </span>
            <span className="text-[10px] uppercase font-mono text-emerald-400 tracking-wider block">
              Control Panel v2.0
            </span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-400">
            System Modules
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              pathname === item.href ||
              (item.href !== "/agri-control-panel/dashboard" && pathname.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 shadow-sm"
                    : "text-zinc-300 hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`h-4 w-4 ${
                      isActive ? "text-emerald-400" : "text-zinc-400"
                    }`}
                  />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                      isActive
                        ? "bg-emerald-500/30 text-emerald-200"
                        : "bg-white/[0.06] text-zinc-300"
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}

          <div className="pt-6 px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-400">
            External Links
          </div>
          <Link
            href="/"
            target="_blank"
            className="flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium text-zinc-300 hover:text-emerald-300 hover:bg-white/[0.04] transition-colors"
          >
            <div className="flex items-center gap-3">
              <ExternalLink className="h-4 w-4 text-zinc-400" />
              <span>Public Website</span>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-zinc-400" />
          </Link>

          <a
            href={`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/docs`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium text-zinc-300 hover:text-emerald-300 hover:bg-white/[0.04] transition-colors"
          >
            <div className="flex items-center gap-3">
              <Database className="h-4 w-4 text-zinc-400" />
              <span>Swagger API Docs</span>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-zinc-400" />
          </a>
        </nav>

        {/* User Account / Sign Out Footer */}
        <div className="p-4 border-t border-white/[0.08] bg-black/40 space-y-3">
          <div className="rounded-xl bg-white/[0.03] border border-white/[0.08] p-3">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-semibold text-white truncate block">
                {user.email}
              </span>
            </div>
            <div className="mt-1 flex items-center justify-between text-[10px]">
              <span className="text-emerald-400 font-mono tracking-wider font-semibold">
                ROLE: ADMIN
              </span>
              <span className="text-zinc-500 font-mono">SUPABASE AUTH</span>
            </div>
          </div>

          <button
            onClick={() => logout()}
            className="w-full flex items-center justify-center gap-2 rounded-xl bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-300 hover:text-red-200 py-2.5 px-3 text-xs font-semibold transition-all shadow-sm"
          >
            <LogOut className="h-4 w-4" />
            <span>Sign Out of Admin</span>
          </button>
        </div>
      </aside>

      {/* Mobile Top Header */}
      <div className="md:hidden h-16 border-b border-white/[0.08] bg-[#070c09] px-4 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
            <Leaf className="h-4 w-4" />
          </div>
          <span className="font-bold text-sm text-white">AgriControl CMS</span>
        </div>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="h-9 w-9 rounded-lg bg-white/[0.05] border border-white/[0.08] flex items-center justify-center text-zinc-300"
        >
          {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-white/[0.08] bg-[#070c09] px-4 py-4 space-y-2 z-40">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-zinc-300 hover:text-emerald-300 hover:bg-white/[0.04]"
            >
              <item.icon className="h-4 w-4 text-emerald-400" />
              <span>{item.label}</span>
            </Link>
          ))}
          <div className="pt-2 border-t border-white/[0.08] flex items-center justify-between">
            <span className="text-xs text-zinc-400 truncate max-w-[200px]">{user.email}</span>
            <button
              onClick={() => logout()}
              className="text-xs text-red-400 flex items-center gap-1.5"
            >
              <LogOut className="h-3.5 w-3.5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      )}

      {/* Main Admin Workspace */}
      <main className="flex-1 min-w-0 overflow-y-auto">
        <div className="p-4 sm:p-8 max-w-7xl mx-auto">{children}</div>
      </main>
    </div>
  );
}

