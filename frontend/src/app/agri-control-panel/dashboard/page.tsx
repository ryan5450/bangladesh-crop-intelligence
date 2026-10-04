"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Sprout,
  Layers,
  Image as ImageIcon,
  Clock,
  PlusCircle,
  ExternalLink,
  Edit,
  Sparkles,
  RefreshCw,
  Search,
} from "lucide-react";
import axios from "axios";

interface AdminStats {
  total_crops: number;
  categories_count: number;
  images_count: number;
  categories: string[];
  recent_updates: Array<{
    id: number;
    crop_name: string;
    scientific_name?: string;
    category?: string;
    image_url?: string;
    image?: string;
  }>;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_BASE}/admin/stats`);
      setStats(res.data);
    } catch (err: any) {
      console.error("Failed to load admin stats:", err);
      // Graceful fallback if backend stats endpoint has network delay
      try {
        const cropsRes = await axios.get(`${API_BASE}/crops`);
        const crops = cropsRes.data || [];
        const cats = Array.from(new Set(crops.map((c: any) => c.category).filter(Boolean)));
        const imgCount = crops.filter((c: any) => c.image || c.image_url).length;
        setStats({
          total_crops: crops.length,
          categories_count: cats.length,
          images_count: imgCount,
          categories: cats as string[],
          recent_updates: crops.slice(0, 6),
        });
      } catch (fallbackErr) {
        setError("Unable to connect to the backend server. Please verify network connectivity.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const statCards = [
    {
      title: "Total Registered Crops",
      value: stats?.total_crops ?? 25,
      icon: Sprout,
      desc: "Comprehensive crop entries in PostgreSQL",
      accent: "text-emerald-400",
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
    },
    {
      title: "Agricultural Categories",
      value: stats?.categories_count ?? 7,
      icon: Layers,
      desc: "Cereals, Fruits, Cash Crops, Spices, Pulses",
      accent: "text-lime-400",
      bg: "bg-lime-500/10",
      border: "border-lime-500/20",
    },
    {
      title: "Crops with Active Media",
      value: stats?.images_count ?? 25,
      icon: ImageIcon,
      desc: "Storage objects & Wikimedia Commons linked",
      accent: "text-cyan-400",
      bg: "bg-cyan-500/10",
      border: "border-cyan-500/20",
    },
    {
      title: "Agronomic Zones",
      value: "8 / 8",
      icon: Clock,
      desc: "Divisional coverage across Bangladesh",
      accent: "text-amber-400",
      bg: "bg-amber-500/10",
      border: "border-amber-500/20",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/[0.08] pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <span>Agronomic Intelligence Dashboard</span>
          </h1>
          <p className="mt-1 text-sm text-zinc-400">
            Real-time management for crops, phenological growth stages, and automated Wikimedia assets
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchStats}
            disabled={loading}
            className="flex items-center gap-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.1] px-4 py-2 text-xs font-medium text-zinc-300 transition-colors"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin text-emerald-400" : ""}`} />
            <span>Refresh Data</span>
          </button>
          <Link
            href="/agri-control-panel/crops"
            className="flex items-center gap-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black px-4 py-2 text-xs font-semibold shadow-glow transition-all"
          >
            <PlusCircle className="h-4 w-4" />
            <span>Manage Crops</span>
          </Link>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="rounded-xl bg-red-500/10 border border-red-500/20 p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {statCards.map((card, i) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: i * 0.08 }}
            className={`glass-panel rounded-2xl p-5 border ${card.border} relative overflow-hidden`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium uppercase tracking-wider text-zinc-400">
                {card.title}
              </span>
              <div className={`h-10 w-10 rounded-xl ${card.bg} border ${card.border} flex items-center justify-center ${card.accent}`}>
                <card.icon className="h-5 w-5" />
              </div>
            </div>
            <div className="mt-4">
              <span className="text-3xl font-bold text-white tracking-tight">
                {card.value}
              </span>
              <p className="mt-1.5 text-xs text-zinc-400 leading-relaxed">
                {card.desc}
              </p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Quick Access Actions Bar */}
      <div className="glass-panel rounded-2xl p-6 border border-white/[0.08]">
        <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-emerald-400" />
          <span>Automated Operations &amp; Quick Actions</span>
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Link
            href="/agri-control-panel/images"
            className="group rounded-xl bg-white/[0.02] hover:bg-emerald-500/10 border border-white/[0.08] hover:border-emerald-500/30 p-4 transition-all"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="h-8 w-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                <ImageIcon className="h-4 w-4" />
              </div>
              <span className="text-sm font-semibold text-white group-hover:text-emerald-300">
                Automated Image Studio
              </span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Search Wikimedia Commons API and sync authentic crop photos to Supabase Storage with 1 click.
            </p>
          </Link>

          <Link
            href="/agri-control-panel/crops"
            className="group rounded-xl bg-white/[0.02] hover:bg-lime-500/10 border border-white/[0.08] hover:border-lime-500/30 p-4 transition-all"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="h-8 w-8 rounded-lg bg-lime-500/20 text-lime-400 flex items-center justify-center">
                <Sprout className="h-4 w-4" />
              </div>
              <span className="text-sm font-semibold text-white group-hover:text-lime-300">
                Crop Directory Table
              </span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Add new crop varieties, modify agro-ecological zones, update pathology, or adjust duration sliders.
            </p>
          </Link>

          <Link
            href="/crops"
            target="_blank"
            className="group rounded-xl bg-white/[0.02] hover:bg-cyan-500/10 border border-white/[0.08] hover:border-cyan-500/30 p-4 transition-all"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="h-8 w-8 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center">
                <ExternalLink className="h-4 w-4" />
              </div>
              <span className="text-sm font-semibold text-white group-hover:text-cyan-300">
                Public Live Platform
              </span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Verify the live discovery filters, phenological growth timelines, and high-res image galleries.
            </p>
          </Link>
        </div>
      </div>

      {/* Recent Updates Table */}
      <div className="glass-panel rounded-2xl p-6 border border-white/[0.08]">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <span>Recent Crop Entries</span>
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              Latest botanical and agronomic records managed in the system
            </p>
          </div>
          <Link
            href="/agri-control-panel/crops"
            className="text-xs text-emerald-400 hover:text-emerald-300 font-medium flex items-center gap-1"
          >
            <span>View All Crops</span>
            <ExternalLink className="h-3 w-3" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-white/[0.08] text-zinc-400 uppercase tracking-wider font-semibold">
                <th className="pb-3 pl-2">Crop</th>
                <th className="pb-3">Scientific Name</th>
                <th className="pb-3">Category</th>
                <th className="pb-3">Media Status</th>
                <th className="pb-3 text-right pr-2">Quick Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.04]">
              {stats?.recent_updates?.map((crop) => (
                <tr key={crop.id} className="hover:bg-white/[0.02] transition-colors">
                  <td className="py-3 pl-2 font-medium text-white flex items-center gap-3">
                    <div className="h-9 w-9 rounded-lg bg-emerald-500/10 border border-emerald-500/20 overflow-hidden flex items-center justify-center shrink-0">
                      {crop.image_url || crop.image ? (
                        /* eslint-disable-next-line @next/next/no-img-element */
                        <img
                          src={crop.image_url || crop.image}
                          alt={crop.crop_name}
                          className="h-full w-full object-cover"
                          onError={(e) => {
                            (e.target as HTMLElement).style.display = "none";
                          }}
                        />
                      ) : (
                        <Sprout className="h-4 w-4 text-emerald-400" />
                      )}
                    </div>
                    <span>{crop.crop_name}</span>
                  </td>
                  <td className="py-3 text-zinc-400 italic">
                    {crop.scientific_name || "—"}
                  </td>
                  <td className="py-3">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-white/[0.05] border border-white/[0.08] text-zinc-300">
                      {crop.category || "Uncategorized"}
                    </span>
                  </td>
                  <td className="py-3">
                    {crop.image_url || crop.image ? (
                      <span className="inline-flex items-center gap-1.5 text-emerald-400 text-[11px]">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                        Linked
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-amber-400 text-[11px]">
                        <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />
                        Needs Photo
                      </span>
                    )}
                  </td>
                  <td className="py-3 text-right pr-2 space-x-2">
                    <Link
                      href={`/agri-control-panel/images?crop=${encodeURIComponent(crop.crop_name)}`}
                      className="inline-flex items-center gap-1 text-[11px] rounded-lg bg-white/[0.04] hover:bg-emerald-500/20 border border-white/[0.08] text-zinc-300 hover:text-emerald-300 px-2.5 py-1 transition-colors"
                    >
                      <Search className="h-3 w-3" />
                      <span>Find Image</span>
                    </Link>
                    <Link
                      href={`/agri-control-panel/crops/edit/${crop.id}`}
                      className="inline-flex items-center gap-1 text-[11px] rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-zinc-300 hover:text-white px-2.5 py-1 transition-colors"
                    >
                      <Edit className="h-3 w-3" />
                      <span>Edit</span>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

