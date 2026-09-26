"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Sprout, Filter, SlidersHorizontal, RefreshCw, X } from "lucide-react";
import { getFilteredCrops } from "@/lib/api";
import { CropSummary, FilterState } from "@/lib/types";
import CropCard from "@/components/CropCard";
import FilterSidebar from "@/components/FilterSidebar";
import { CropCardSkeleton } from "@/components/LoadingSkeleton";

function CropsListingContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";
  const initialCategory = searchParams.get("category") || "All";

  const [filters, setFilters] = useState<FilterState>({
    query: initialQuery,
    category: initialCategory,
    season: "All",
    region: "All",
    waterRequirement: "All",
    minDuration: undefined,
    maxDuration: undefined,
  });

  const [crops, setCrops] = useState<CropSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);

  const fetchCrops = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getFilteredCrops(filters);
      setCrops(data);
    } catch (err: any) {
      setError(
        "Unable to fetch crops from FastAPI backend. Please ensure the backend is running at http://127.0.0.1:8000."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCrops();
  }, [filters]);

  const handleResetFilters = () => {
    setFilters({
      query: "",
      category: "All",
      season: "All",
      region: "All",
      waterRequirement: "All",
      minDuration: undefined,
      maxDuration: undefined,
    });
  };

  const activeFilterList = [
    filters.query ? { label: `Search: "${filters.query}"`, clear: () => setFilters((f) => ({ ...f, query: "" })) } : null,
    filters.category && filters.category !== "All" ? { label: `Category: ${filters.category}`, clear: () => setFilters((f) => ({ ...f, category: "All" })) } : null,
    filters.season && filters.season !== "All" ? { label: `Season: ${filters.season}`, clear: () => setFilters((f) => ({ ...f, season: "All" })) } : null,
    filters.region && filters.region !== "All" ? { label: `Region: ${filters.region}`, clear: () => setFilters((f) => ({ ...f, region: "All" })) } : null,
    filters.waterRequirement && filters.waterRequirement !== "All" ? { label: `Water: ${filters.waterRequirement}`, clear: () => setFilters((f) => ({ ...f, waterRequirement: "All" })) } : null,
    filters.maxDuration ? { label: `Max ${filters.maxDuration} days`, clear: () => setFilters((f) => ({ ...f, maxDuration: undefined })) } : null,
  ].filter(Boolean) as { label: string; clear: () => void }[];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-20 space-y-8">
      {/* Top Banner Header */}
      <div className="border-b border-white/[0.08] pb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 text-xs font-semibold text-emerald-400 mb-1">
            <Sprout className="h-4 w-4" />
            <span>Precision Discovery System</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Explore Bangladesh Agriculture
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Advanced multi-facet filtering across taxonomy, agro-ecological zones, phenology, and pathology.
          </p>
        </div>

        {/* Mobile Filter Toggle Button */}
        <button
          onClick={() => setMobileFilterOpen(!mobileFilterOpen)}
          className="lg:hidden flex items-center justify-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-2.5 text-xs font-semibold text-emerald-300"
        >
          <SlidersHorizontal className="h-4 w-4" />
          <span>Filters ({activeFilterList.length})</span>
        </button>
      </div>

      {/* Main Two-Column Layout (Sidebar + Crop Grid) */}
      <div className="flex flex-col lg:flex-row gap-8 items-start">
        {/* Desktop Filter Sidebar */}
        <div className="hidden lg:block">
          <FilterSidebar
            filters={filters}
            onFilterChange={setFilters}
            onReset={handleResetFilters}
            totalResults={crops.length}
          />
        </div>

        {/* Mobile Filter Modal / Drawer */}
        {mobileFilterOpen && (
          <div className="fixed inset-0 z-50 flex bg-black/80 backdrop-blur-md lg:hidden p-4">
            <div className="relative w-full max-w-sm rounded-3xl border border-white/[0.1] bg-[#0c1410] p-6 shadow-2xl overflow-y-auto max-h-[90vh] my-auto">
              <div className="flex items-center justify-between pb-4 border-b border-white/[0.08] mb-4">
                <h3 className="font-bold text-white text-base">Filter Crops</h3>
                <button
                  onClick={() => setMobileFilterOpen(false)}
                  className="rounded-lg p-1.5 text-zinc-400 hover:text-white"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              <FilterSidebar
                filters={filters}
                onFilterChange={setFilters}
                onReset={handleResetFilters}
                totalResults={crops.length}
              />
              <button
                onClick={() => setMobileFilterOpen(false)}
                className="mt-6 w-full rounded-xl bg-emerald-500 py-3 text-xs font-bold text-black"
              >
                Apply Filters ({crops.length} crops)
              </button>
            </div>
          </div>
        )}

        {/* Right Side: Results Section */}
        <div className="flex-1 w-full space-y-6">
          {/* Active Filter Pills Bar */}
          {activeFilterList.length > 0 && (
            <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-white/[0.06] bg-[#0c1410]/50 p-3">
              <span className="text-xs text-zinc-400 font-medium mr-1">Active Filters:</span>
              {activeFilterList.map((item, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-300"
                >
                  <span>{item.label}</span>
                  <button onClick={item.clear} className="hover:text-white">
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
              <button
                onClick={handleResetFilters}
                className="text-xs text-zinc-500 hover:text-zinc-300 ml-auto font-medium"
              >
                Clear all
              </button>
            </div>
          )}

          {/* Grid Content */}
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => (
                <CropCardSkeleton key={i} />
              ))}
            </div>
          ) : error ? (
            <div className="rounded-2xl border border-rose-500/30 bg-[#140b0d]/80 p-8 text-center backdrop-blur-xl">
              <h3 className="text-base font-bold text-white mb-2">Backend Connection Error</h3>
              <p className="text-xs text-zinc-400 max-w-md mx-auto">{error}</p>
              <button
                onClick={fetchCrops}
                className="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-emerald-500 px-4 py-2 text-xs font-semibold text-black hover:bg-emerald-400 transition-all shadow-glow"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                <span>Retry</span>
              </button>
            </div>
          ) : crops.length === 0 ? (
            <div className="rounded-2xl border border-white/[0.08] bg-[#0c1410]/60 p-12 text-center">
              <Sprout className="h-8 w-8 text-zinc-500 mx-auto mb-2" />
              <h3 className="text-sm font-semibold text-zinc-300">No matching crops discovered</h3>
              <p className="text-xs text-zinc-500 mt-1 max-w-sm mx-auto">
                No crops match your current criteria. Try adjusting the category, region, or search keywords.
              </p>
              <button
                onClick={handleResetFilters}
                className="mt-4 inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 hover:underline"
              >
                Reset All Filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
              {crops.map((crop, index) => (
                <CropCard key={crop.id} crop={crop} index={index} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function CropsListingPage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <CropCardSkeleton key={i} />
          ))}
        </div>
      }
    >
      <CropsListingContent />
    </Suspense>
  );
}
