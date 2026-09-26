"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { Activity, Menu, X, Sparkles, Layers, ShieldCheck, LogOut } from "lucide-react";
import { checkApiHealth } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function Navbar() {
  const pathname = usePathname();
  const { user, isAdmin, logout } = useAuth();
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const verifyBackend = async () => {
      const isHealthy = await checkApiHealth();
      if (isMounted) {
        setApiConnected(isHealthy);
      }
    };

    verifyBackend();
    const interval = setInterval(verifyBackend, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const navLinks = [
    { name: "Home", href: "/" },
    { name: "All Crops", href: "/crops" },
    { name: "AI Assistant", href: "/assistant" },
    { name: "Categories", href: "/#categories" },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/[0.08] bg-[#060907]/80 backdrop-blur-xl transition-all">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="relative flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-950/40 border border-emerald-500/30 group-hover:border-emerald-400/60 group-hover:shadow-glow transition-all overflow-hidden p-1">
            <Image
              src="/logo.png"
              alt="Bangladesh Crop Intelligence Logo"
              width={40}
              height={40}
              className="object-contain"
              priority
            />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight text-white group-hover:text-emerald-300 transition-colors">
                CropIntel
              </span>
              <span className="rounded-md bg-emerald-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-400 border border-emerald-500/20">
                BD AI
              </span>
            </div>
            <p className="text-[11px] text-zinc-400 hidden sm:block">Bangladesh Precision Agriculture</p>
          </div>
        </Link>

        {/* Desktop Nav Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.name}
                href={link.href}
                className={`rounded-lg px-3.5 py-2 text-sm font-medium transition-all ${
                  isActive
                    ? "text-emerald-400 bg-emerald-500/10 border border-emerald-500/20"
                    : "text-zinc-300 hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                {link.name}
              </Link>
            );
          })}
        </nav>

        {/* Right Side Actions */}
        <div className="hidden sm:flex items-center gap-3">
          {/* API Health Pill */}
          <div className="flex items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.02] px-3 py-1.5 text-xs text-zinc-300">
            <span className="relative flex h-2 w-2">
              {apiConnected ? (
                <>
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </>
              ) : apiConnected === false ? (
                <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
              ) : (
                <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-400 animate-pulse"></span>
              )}
            </span>
            <span className="font-mono text-[11px]">
              {apiConnected ? "System Live" : apiConnected === false ? "Connecting..." : "Checking..."}
            </span>
          </div>

          <Link
            href="/crops"
            className="flex items-center gap-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 px-3.5 py-2 text-xs font-semibold text-black transition-all shadow-glow hover:shadow-glow-lg"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>Explore</span>
          </Link>
        </div>

        {/* Mobile Menu Toggle */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden rounded-lg p-2 text-zinc-400 hover:bg-white/[0.05] hover:text-white"
          aria-label="Toggle Navigation"
        >
          {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-white/[0.08] bg-[#090d0b] px-4 pt-3 pb-5 space-y-2">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className="block rounded-lg px-3 py-2 text-base font-medium text-zinc-200 hover:bg-emerald-500/10 hover:text-emerald-400"
            >
              {link.name}
            </Link>
          ))}
          <div className="pt-2 border-t border-white/[0.08] flex items-center justify-between text-xs text-zinc-400">
            <span>Agronomic Engine:</span>
            <span className={apiConnected ? "text-emerald-400" : "text-rose-400"}>
              {apiConnected ? "Operational" : "Connecting"}
            </span>
          </div>
        </div>
      )}
    </header>
  );
}

