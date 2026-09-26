"use client";

import React from "react";
import { motion } from "framer-motion";
import { ShieldAlert, AlertTriangle, Bug, Stethoscope } from "lucide-react";

interface DiseaseCardProps {
  diseaseName: string;
  index?: number;
}

export default function DiseaseCard({ diseaseName, index = 0 }: DiseaseCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      className="group relative overflow-hidden rounded-xl border border-rose-500/15 bg-[#120e10]/70 p-4 backdrop-blur-md transition-all duration-300 hover:border-rose-500/40 hover:bg-[#181114]/90 hover:shadow-lg"
    >
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-rose-500/20 bg-rose-500/10 text-rose-400 group-hover:border-rose-400 group-hover:shadow-[0_0_15px_rgba(244,63,94,0.3)] transition-all">
          <ShieldAlert className="h-4 w-4" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-rose-400/90">
              Pathology Alert
            </span>
            <span className="inline-flex items-center gap-1 rounded-full bg-rose-500/10 px-2 py-0.5 text-[10px] font-medium text-rose-300 border border-rose-500/20">
              High Risk
            </span>
          </div>
          <h4 className="mt-1 text-sm font-semibold text-zinc-100 group-hover:text-rose-200 transition-colors">
            {diseaseName}
          </h4>
          <p className="mt-1 text-xs text-zinc-400 leading-relaxed">
            Monitor crop foliage, stems, and soil moisture regularly during active vegetative and flowering periods.
          </p>
        </div>
      </div>
    </motion.div>
  );
}

