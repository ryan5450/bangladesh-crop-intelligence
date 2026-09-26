"use client";

import React from "react";
import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";

interface InfoCardProps {
  title: string;
  value: string | React.ReactNode;
  icon?: LucideIcon;
  description?: string;
  colorScheme?: "emerald" | "amber" | "lime" | "teal" | "sky" | "rose" | "purple";
  index?: number;
  className?: string;
}

const colorStyles = {
  emerald: {
    border: "border-emerald-500/20 group-hover:border-emerald-500/40",
    bg: "bg-emerald-500/10 text-emerald-400",
    glow: "group-hover:shadow-[0_0_20px_rgba(16,185,129,0.15)]",
  },
  amber: {
    border: "border-amber-400/20 group-hover:border-amber-400/40",
    bg: "bg-amber-400/10 text-amber-400",
    glow: "group-hover:shadow-[0_0_20px_rgba(251,191,36,0.15)]",
  },
  lime: {
    border: "border-lime-400/20 group-hover:border-lime-400/40",
    bg: "bg-lime-400/10 text-lime-400",
    glow: "group-hover:shadow-[0_0_20px_rgba(163,230,53,0.15)]",
  },
  teal: {
    border: "border-teal-400/20 group-hover:border-teal-400/40",
    bg: "bg-teal-400/10 text-teal-400",
    glow: "group-hover:shadow-[0_0_20px_rgba(45,212,191,0.15)]",
  },
  sky: {
    border: "border-sky-400/20 group-hover:border-sky-400/40",
    bg: "bg-sky-400/10 text-sky-400",
    glow: "group-hover:shadow-[0_0_20px_rgba(56,189,248,0.15)]",
  },
  rose: {
    border: "border-rose-400/20 group-hover:border-rose-400/40",
    bg: "bg-rose-400/10 text-rose-400",
    glow: "group-hover:shadow-[0_0_20px_rgba(251,113,133,0.15)]",
  },
  purple: {
    border: "border-purple-400/20 group-hover:border-purple-400/40",
    bg: "bg-purple-400/10 text-purple-400",
    glow: "group-hover:shadow-[0_0_20px_rgba(192,132,252,0.15)]",
  },
};

export default function InfoCard({
  title,
  value,
  icon: Icon,
  description,
  colorScheme = "emerald",
  index = 0,
  className = "",
}: InfoCardProps) {
  const currentStyle = colorStyles[colorScheme] || colorStyles.emerald;

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.35, delay: index * 0.05 }}
      whileHover={{ y: -3, transition: { duration: 0.2 } }}
      className={`group relative overflow-hidden rounded-2xl border border-white/[0.08] bg-[#0c1410]/80 p-5 backdrop-blur-xl transition-all duration-300 ${currentStyle.border} ${currentStyle.glow} ${className}`}
    >
      <div className="flex items-center gap-3 mb-2.5">
        {Icon && (
          <div
            className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border ${currentStyle.border} ${currentStyle.bg} transition-transform group-hover:scale-110`}
          >
            <Icon className="h-4 w-4" />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-400 block truncate">
            {title}
          </span>
          {description && (
            <span className="text-[10px] text-zinc-400 block truncate">{description}</span>
          )}
        </div>
      </div>

      <div className="text-sm font-semibold text-white leading-relaxed tracking-tight group-hover:text-emerald-300 transition-colors">
        {value || "Not specified"}
      </div>
    </motion.div>
  );
}

