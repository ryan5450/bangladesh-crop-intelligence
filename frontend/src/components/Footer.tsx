import React from "react";
import Link from "next/link";
import Image from "next/image";
import { ShieldCheck, Database, Compass } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-white/[0.08] bg-[#040605] text-zinc-400 mt-20">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center gap-2.5">
              <div className="relative flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-950/40 border border-emerald-500/30 overflow-hidden p-1">
                <Image
                  src="/logo.png"
                  alt="CropIntel Bangladesh Logo"
                  width={32}
                  height={32}
                  className="object-contain"
                />
              </div>
              <span className="font-bold text-base text-white">CropIntel Bangladesh</span>
            </div>
            <p className="text-sm leading-relaxed max-w-md text-zinc-400">
              A comprehensive national agricultural intelligence platform combining real-time crop taxonomy,
              phenological growth stages, pathology management, and agro-ecological zone mapping across all 8 divisions of Bangladesh.
            </p>
            <div className="flex items-center gap-4 text-xs text-zinc-400">
              <div className="flex items-center gap-1.5">
                <Database className="h-3.5 w-3.5 text-emerald-400" />
                <span>Supabase PostgreSQL</span>
              </div>
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
                <span>FastAPI Microservice</span>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-sm font-semibold text-white tracking-wider uppercase mb-3">
              Explore
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/" className="hover:text-emerald-400 transition-colors">
                  Home Overview
                </Link>
              </li>
              <li>
                <Link href="/crops" className="hover:text-emerald-400 transition-colors">
                  All 25 Crops
                </Link>
              </li>
              <li>
                <Link href="/#categories" className="hover:text-emerald-400 transition-colors">
                  Crop Categories
                </Link>
              </li>
              <li>
                <Link href="/assistant" className="hover:text-emerald-400 transition-colors">
                  AI Agronomic Advisor &rarr;
                </Link>
              </li>
            </ul>
          </div>

          {/* Regional Agro-Ecological Zones */}
          <div>
            <h3 className="text-sm font-semibold text-white tracking-wider uppercase mb-3">
              Divisional Zones
            </h3>
            <div className="flex flex-wrap gap-1.5 text-xs">
              {["Dhaka", "Rajshahi", "Rangpur", "Mymensingh", "Sylhet", "Chattogram", "Khulna", "Barisal"].map((div) => (
                <span
                  key={div}
                  className="rounded-md border border-white/[0.08] bg-white/[0.02] px-2 py-1 text-zinc-400 hover:text-emerald-300 hover:border-emerald-500/30 transition-all"
                >
                  {div}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-10 border-t border-white/[0.06] pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-zinc-400 gap-4">
          <p>&copy; {new Date().getFullYear()} Bangladesh Crop Intelligence Assistant. Powered by Next.js & FastAPI.</p>
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
            <span>Agronomic Intelligence System v2.0</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

