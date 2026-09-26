import React from "react";

export function CropCardSkeleton() {
  return (
    <div className="rounded-2xl border border-white/[0.08] bg-[#0c130f]/60 p-5 backdrop-blur-xl animate-pulse">
      <div className="flex items-center justify-between">
        <div className="h-6 w-20 rounded-full bg-white/[0.06]" />
        <div className="h-8 w-8 rounded-full bg-white/[0.06]" />
      </div>
      <div className="mt-4 mb-2 space-y-2">
        <div className="h-5 w-3/4 rounded-md bg-white/[0.08]" />
        <div className="h-3 w-1/2 rounded-md bg-white/[0.04]" />
      </div>
      <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between">
        <div className="h-3 w-12 rounded bg-white/[0.04]" />
        <div className="h-3 w-24 rounded bg-white/[0.06]" />
      </div>
    </div>
  );
}

export function CropDetailSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      {/* Top Banner Skeleton */}
      <div className="rounded-3xl border border-white/[0.08] bg-[#0c130f]/80 p-8 space-y-4">
        <div className="h-6 w-28 rounded-full bg-white/[0.06]" />
        <div className="h-10 w-2/3 rounded-lg bg-white/[0.08]" />
        <div className="h-5 w-1/3 rounded-md bg-white/[0.04]" />
      </div>

      {/* Grid Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="h-28 rounded-2xl border border-white/[0.08] bg-[#0c130f]/60 p-4" />
        ))}
      </div>
    </div>
  );
}

