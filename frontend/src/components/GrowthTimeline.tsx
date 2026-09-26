"use client";

import React from "react";
import { motion } from "framer-motion";
import { CheckCircle2, Sprout, Clock } from "lucide-react";
import { GrowthStage } from "@/lib/types";

interface GrowthTimelineProps {
  stages: GrowthStage[];
}

export default function GrowthTimeline({ stages }: GrowthTimelineProps) {
  if (!stages || stages.length === 0) {
    return (
      <div className="rounded-2xl border border-white/[0.08] bg-[#0c130f]/60 p-6 text-center text-sm text-zinc-400">
        No growth stages recorded for this crop.
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Mobile & Desktop Responsive Step Container */}
      <div className="relative pl-6 sm:pl-8 before:absolute before:top-3 before:bottom-3 before:left-[11px] sm:before:left-[15px] before:w-[2px] before:bg-gradient-to-b before:from-emerald-500 before:via-emerald-500/40 before:to-emerald-950/20 space-y-6">
        {stages.map((stage, index) => {
          const isFirst = index === 0;
          const isLast = index === stages.length - 1;

          return (
            <motion.div
              key={stage.stage_number}
              initial={{ opacity: 0, x: -16 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.35, delay: index * 0.06 }}
              className="relative group"
            >
              {/* Timeline Marker Dot */}
              <div
                className={`absolute -left-[30px] sm:-left-[38px] top-1 flex h-7 w-7 sm:h-8 sm:w-8 items-center justify-center rounded-full border text-xs font-bold transition-all duration-300 ${
                  isFirst
                    ? "border-emerald-400 bg-emerald-500/20 text-emerald-300 shadow-glow"
                    : isLast
                    ? "border-lime-400 bg-lime-500/20 text-lime-300 shadow-glow"
                    : "border-white/[0.15] bg-[#0c1410] text-zinc-300 group-hover:border-emerald-400/60 group-hover:text-emerald-300"
                }`}
              >
                {stage.stage_number}
              </div>

              {/* Stage Card */}
              <div className="rounded-xl border border-white/[0.08] bg-[#0c1410]/70 p-4 backdrop-blur-md transition-all duration-300 group-hover:border-emerald-500/30 group-hover:bg-[#101c15]/80">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
                      Phase {stage.stage_number}
                    </span>
                    {isFirst && (
                      <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-300 border border-emerald-500/20">
                        Initial Phase
                      </span>
                    )}
                    {isLast && (
                      <span className="rounded-full bg-lime-500/10 px-2 py-0.5 text-[10px] font-medium text-lime-300 border border-lime-500/20">
                        Harvest Readiness
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-zinc-500 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    <span>Sequential Stage</span>
                  </div>
                </div>

                <h4 className="mt-1.5 text-base font-semibold text-white group-hover:text-emerald-300 transition-colors">
                  {stage.stage_name}
                </h4>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

