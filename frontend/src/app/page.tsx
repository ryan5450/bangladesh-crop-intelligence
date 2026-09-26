"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import {
  Sprout,
  Sparkles,
  Layers,
  ShieldAlert,
  MapPin,
  ArrowRight,
  RefreshCw,
  Wheat,
  Apple,
  Carrot,
  Leaf,
} from "lucide-react";
import { getAllCrops } from "@/lib/api";
import { CropSummary } from "@/lib/types";
import CropCard from "@/components/CropCard";
import SearchBar from "@/components/SearchBar";
import { CropCardSkeleton } from "@/components/LoadingSkeleton";

const CATEGORIES = [
  { name: "All", icon: Sprout },
  { name: "Fruit", icon: Apple },
  { name: "Vegetable", icon: Carrot },
  { name: "Cereal", icon: Wheat },
  { name: "Cash Crop", icon: Sparkles },
  { name: "Spice", icon: Layers },
  { name: "Pulse", icon: Leaf },
];

export default function HomePage() {
  const [crops, setCrops] = useState<CropSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState("All");

  const loadCrops = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getAllCrops();
      setCrops(data);
    } catch (err: any) {
      setError(
        "Could not connect to FastAPI backend at http://127.0.0.1:8000. Please ensure the backend server is running."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCrops();
  }, []);

  const filteredCrops = crops.filter((crop) => {
    if (selectedCategory === "All") return true;
    return (crop.category || "").toLowerCase() === selectedCategory.toLowerCase();
  });

  return (
    <div className="space-y-20 pb-16">
      {/* 1. HERO SECTION */}
      <section className="relative pt-12 pb-8 sm:pt-20 sm:pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-6 max-w-3xl mx-auto"
        >
          {/* Badge */}
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3.5 py-1 text-xs font-semibold text-emerald-300 backdrop-blur-md shadow-glow">
            <Sparkles className="h-3.5 w-3.5" />
            <span>AI-Powered National Agriculture Platform</span>
          </div>

          {/* Logo Showcase */}
          <div className="flex justify-center pt-2">
            <div className="relative group">
              <div className="absolute -inset-1.5 rounded-3xl bg-gradient-to-r from-emerald-500/30 to-lime-500/20 blur-xl opacity-75 group-hover:opacity-100 transition duration-700"></div>
              <div className="relative flex items-center justify-center p-3 rounded-3xl bg-[#08100c]/90 border border-emerald-500/30 shadow-2xl backdrop-blur-xl group-hover:border-emerald-400/60 transition-all">
                <Image
                  src="/logo.png"
                  alt="Bangladesh Crop Intelligence Logo"
                  width={110}
                  height={110}
                  className="object-contain drop-shadow-[0_0_25px_rgba(16,185,129,0.35)]"
                  priority
                />
              </div>
            </div>
          </div>

          {/* Main Title */}
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-[1.15]">
            Bangladesh{" "}
            <span className="bg-gradient-to-r from-emerald-400 via-emerald-300 to-lime-400 bg-clip-text text-transparent">
              Crop Intelligence
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-zinc-400 leading-relaxed max-w-2xl mx-auto">
            AI-powered agriculture knowledge platform for Bangladeshi crops.
          </p>

          {/* Hero Search Bar */}
          <div className="pt-4 max-w-2xl mx-auto">
            <SearchBar placeholder="Search crops (e.g. Boro Rice, Mango, Potato, Jute)..." />
          </div>

          {/* Quick Tag Recommendations */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-2 text-xs text-zinc-400">
            <span>Popular Searches:</span>
            {["Boro Rice", "Mango", "Potato", "Jute", "Mustard"].map((term) => (
              <Link
                key={term}
                href={`/crops/${encodeURIComponent(term)}`}
                className="rounded-md border border-white/[0.08] bg-white/[0.02] px-2.5 py-1 text-zinc-300 hover:border-emerald-500/40 hover:text-emerald-300 hover:bg-emerald-500/10 transition-all"
              >
                {term}
              </Link>
            ))}
          </div>
        </motion.div>

        {/* Quick Stats Metrics Grid */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-14 grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 max-w-4xl mx-auto"
        >
          <div className="rounded-2xl border border-white/[0.08] bg-[#0c1410]/60 p-4 backdrop-blur-xl">
            <div className="flex items-center justify-center text-emerald-400 mb-1">
              <Sprout className="h-5 w-5" />
            </div>
            <div className="text-2xl font-bold text-white">25+</div>
            <div className="text-xs text-zinc-400">National Crops</div>
          </div>

          <div className="rounded-2xl border border-white/[0.08] bg-[#0c1410]/60 p-4 backdrop-blur-xl">
            <div className="flex items-center justify-center text-emerald-400 mb-1">
              <Layers className="h-5 w-5" />
            </div>
            <div className="text-2xl font-bold text-white">130+</div>
            <div className="text-xs text-zinc-400">Growth Phases</div>
          </div>

          <div className="rounded-2xl border border-white/[0.08] bg-[#0c1410]/60 p-4 backdrop-blur-xl">
            <div className="flex items-center justify-center text-rose-400 mb-1">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div className="text-2xl font-bold text-white">50+</div>
            <div className="text-xs text-zinc-400">Disease Profiles</div>
          </div>

          <div className="rounded-2xl border border-white/[0.08] bg-[#0c1410]/60 p-4 backdrop-blur-xl">
            <div className="flex items-center justify-center text-lime-400 mb-1">
              <MapPin className="h-5 w-5" />
            </div>
            <div className="text-2xl font-bold text-white">8</div>
            <div className="text-xs text-zinc-400">Divisional Zones</div>
          </div>
        </motion.div>
      </section>

      {/* 2. CATEGORIES SECTION */}
      <section id="categories" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Agricultural Categories</h2>
            <p className="text-xs text-zinc-400 mt-0.5">Filter national crops by classification</p>
          </div>
          <Link
            href="/crops"
            className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1 group"
          >
            <span>View all 25 crops</span>
            <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-1" />
          </Link>
        </div>

        {/* Category Filter Chips */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          {CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            const isSelected = selectedCategory === cat.name;
            return (
              <button
                key={cat.name}
                onClick={() => setSelectedCategory(cat.name)}
                className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-semibold whitespace-nowrap transition-all duration-200 border ${
                  isSelected
                    ? "border-emerald-400 bg-emerald-500/20 text-emerald-300 shadow-glow"
                    : "border-white/[0.08] bg-[#0c1410]/60 text-zinc-300 hover:border-emerald-500/30 hover:bg-[#101c15]"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{cat.name}</span>
              </button>
            );
          })}
        </div>
      </section>

      {/* 3. FEATURED CROPS GRID */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">
              {selectedCategory === "All" ? "Featured Bangladesh Crops" : `${selectedCategory} Crops`}
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              Showing {filteredCrops.length} {filteredCrops.length === 1 ? "crop" : "crops"}
            </p>
          </div>
        </div>

        {/* Content State */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <CropCardSkeleton key={i} />
            ))}
          </div>
        ) : error ? (
          <div className="rounded-2xl border border-rose-500/30 bg-[#140b0d]/70 p-8 text-center backdrop-blur-xl">
            <ShieldAlert className="h-10 w-10 text-rose-400 mx-auto mb-3" />
            <h3 className="text-base font-bold text-white">Backend Connection Unavailable</h3>
            <p className="text-xs text-zinc-400 mt-1 max-w-md mx-auto">{error}</p>
            <button
              onClick={loadCrops}
              className="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-emerald-500 px-4 py-2 text-xs font-semibold text-black hover:bg-emerald-400 transition-all shadow-glow"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Retry Connection</span>
            </button>
          </div>
        ) : filteredCrops.length === 0 ? (
          <div className="rounded-2xl border border-white/[0.08] bg-[#0c1410]/60 p-12 text-center">
            <Sprout className="h-8 w-8 text-zinc-500 mx-auto mb-2" />
            <h3 className="text-sm font-semibold text-zinc-300">No crops in this category</h3>
            <p className="text-xs text-zinc-500 mt-1">Try selecting another category or view all crops.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {filteredCrops.map((crop, index) => (
              <CropCard key={crop.id} crop={crop} index={index} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

