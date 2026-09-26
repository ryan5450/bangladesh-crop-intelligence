"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowUpRight, Leaf, Wheat, Apple, Carrot, Flower2, Sparkles } from "lucide-react";
import { CropSummary } from "@/lib/types";

interface CropCardProps {
  crop: CropSummary;
  index?: number;
}

// Category color and icon mapping for rich visual cues
const getCategoryDetails = (category: string | null) => {
  const cat = (category || "").toLowerCase();
  if (cat.includes("cereal")) {
    return {
      icon: Wheat,
      color: "text-amber-400 bg-amber-400/10 border-amber-400/20",
      accent: "from-amber-500/10 to-transparent",
    };
  }
  if (cat.includes("fruit")) {
    return {
      icon: Apple,
      color: "text-rose-400 bg-rose-400/10 border-rose-400/20",
      accent: "from-rose-500/10 to-transparent",
    };
  }
  if (cat.includes("vegetable")) {
    return {
      icon: Carrot,
      color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
      accent: "from-emerald-500/10 to-transparent",
    };
  }
  if (cat.includes("spice") || cat.includes("cash")) {
    return {
      icon: Sparkles,
      color: "text-purple-400 bg-purple-400/10 border-purple-400/20",
      accent: "from-purple-500/10 to-transparent",
    };
  }
  return {
    icon: Leaf,
    color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
    accent: "from-emerald-500/10 to-transparent",
  };
};

export default function CropCard({ crop, index = 0 }: CropCardProps) {
  const { icon: CategoryIcon, color, accent } = getCategoryDetails(crop.category);

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.04 }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className="group relative"
    >
      <Link href={`/crops/${encodeURIComponent(crop.crop_name)}`}>
        <div className="relative overflow-hidden rounded-2xl border border-white/[0.08] bg-[#0c130f]/80 p-5 backdrop-blur-xl transition-all duration-300 group-hover:border-emerald-500/40 group-hover:bg-[#101a14]/90 group-hover:shadow-glow">
          {/* Subtle ambient gradient overlay */}
          <div
            className={`pointer-events-none absolute -top-12 -right-12 h-32 w-32 rounded-full bg-gradient-to-br ${accent} blur-2xl transition-opacity group-hover:opacity-100 opacity-50`}
          />

          {/* Top row: Category tag & Action Icon */}
          <div className="flex items-center justify-between gap-2">
            <span
              className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${color}`}
            >
              <CategoryIcon className="h-3.5 w-3.5" />
              <span>{crop.category || "Crop"}</span>
            </span>

            <div className="flex h-8 w-8 items-center justify-center rounded-full border border-white/[0.08] bg-white/[0.03] text-zinc-400 group-hover:border-emerald-500/40 group-hover:bg-emerald-500/20 group-hover:text-emerald-300 transition-all">
              <ArrowUpRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
            </div>
          </div>

          {/* Middle: Crop Name */}
          <div className="mt-4 mb-2">
            <h3 className="text-lg font-bold tracking-tight text-white group-hover:text-emerald-300 transition-colors">
              {crop.crop_name}
            </h3>
            <p className="text-xs text-zinc-400 mt-1 flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
              Verified Database Record
            </p>
          </div>

          {/* Footer of Card */}
          <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between text-xs text-zinc-400">
            <span>ID #{crop.id}</span>
            <span className="text-emerald-400 font-medium group-hover:underline flex items-center gap-1">
              Intelligence Details &rarr;
            </span>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}

