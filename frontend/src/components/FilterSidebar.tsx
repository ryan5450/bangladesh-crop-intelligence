"use client";

import React, { useState } from "react";
import {
  Filter,
  RotateCcw,
  Search,
  Droplets,
  Calendar,
  Layers,
  MapPin,
  Clock,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { FilterState } from "@/lib/types";

interface FilterSidebarProps {
  filters: FilterState;
  onFilterChange: (newFilters: FilterState) => void;
  onReset: () => void;
  totalResults: number;
}

const CATEGORIES = [
  "All",
  "Fruit",
  "Vegetable",
  "Cereal",
  "Cash Crop",
  "Spice",
  "Pulse",
];

const SEASONS = ["All", "Rabi", "Kharif-1", "Kharif-2", "Summer"];

const REGIONS = [
  "All",
  "Rajshahi",
  "Rangpur",
  "Mymensingh",
  "Sylhet",
  "Barisal",
  "Khulna",
  "Dhaka",
  "Chattogram",
];

const WATER_LEVELS = ["All", "Low", "Moderate", "High"];

export default function FilterSidebar({
  filters,
  onFilterChange,
  onReset,
  totalResults,
}: FilterSidebarProps) {
  const [openSections, setOpenSections] = useState({
    category: true,
    season: true,
    region: true,
    water: true,
    duration: true,
  });

  const toggleSection = (section: keyof typeof openSections) => {
    setOpenSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const handleTextSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({ ...filters, query: e.target.value });
  };

  const hasActiveFilters =
    Boolean(filters.query) ||
    (filters.category && filters.category !== "All") ||
    (filters.season && filters.season !== "All") ||
    (filters.region && filters.region !== "All") ||
    (filters.waterRequirement && filters.waterRequirement !== "All") ||
    (filters.maxDuration && filters.maxDuration < 365);

  return (
    <aside className="w-full lg:w-72 shrink-0 space-y-6">
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            <Filter className="h-3.5 w-3.5" />
          </div>
          <h2 className="text-sm font-bold text-white tracking-wide uppercase">
            Discovery Filters
          </h2>
        </div>

        {hasActiveFilters && (
          <button
            onClick={onReset}
            className="flex items-center gap-1 text-[11px] font-semibold text-emerald-400 hover:text-emerald-300 transition-colors"
          >
            <RotateCcw className="h-3 w-3" />
            <span>Reset All</span>
          </button>
        )}
      </div>

      {/* 1. Universal Search Input */}
      <div className="space-y-2">
        <label className="text-xs font-semibold text-zinc-300 flex items-center gap-1.5">
          <Search className="h-3.5 w-3.5 text-emerald-400" />
          <span>Cross-Field Search</span>
        </label>
        <div className="relative">
          <input
            type="text"
            value={filters.query || ""}
            onChange={handleTextSearch}
            placeholder="Search crop, disease, region..."
            className="w-full rounded-xl border border-white/[0.1] bg-[#0c1410]/90 py-2.5 pl-3 pr-3 text-xs text-white placeholder-zinc-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500/20 transition-all shadow-inner"
          />
        </div>
      </div>

      {/* 2. Category Filter */}
      <div className="border-t border-white/[0.06] pt-4">
        <button
          onClick={() => toggleSection("category")}
          className="flex w-full items-center justify-between text-xs font-semibold text-zinc-200 hover:text-emerald-400 transition-colors"
        >
          <span className="flex items-center gap-1.5">
            <Layers className="h-3.5 w-3.5 text-emerald-400" />
            <span>Category</span>
          </span>
          {openSections.category ? <ChevronUp className="h-3.5 w-3.5 text-zinc-500" /> : <ChevronDown className="h-3.5 w-3.5 text-zinc-500" />}
        </button>

        {openSections.category && (
          <div className="mt-3 space-y-1.5 max-h-48 overflow-y-auto pr-1">
            {CATEGORIES.map((cat) => {
              const isSelected = (filters.category || "All") === cat;
              return (
                <button
                  key={cat}
                  onClick={() => onFilterChange({ ...filters, category: cat })}
                  className={`w-full flex items-center justify-between rounded-lg px-2.5 py-1.5 text-xs text-left transition-all ${
                    isSelected
                      ? "bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/30"
                      : "text-zinc-400 hover:bg-white/[0.04] hover:text-zinc-200"
                  }`}
                >
                  <span>{cat}</span>
                  {isSelected && <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* 3. Season Filter */}
      <div className="border-t border-white/[0.06] pt-4">
        <button
          onClick={() => toggleSection("season")}
          className="flex w-full items-center justify-between text-xs font-semibold text-zinc-200 hover:text-emerald-400 transition-colors"
        >
          <span className="flex items-center gap-1.5">
            <Calendar className="h-3.5 w-3.5 text-amber-400" />
            <span>Growing Season</span>
          </span>
          {openSections.season ? <ChevronUp className="h-3.5 w-3.5 text-zinc-500" /> : <ChevronDown className="h-3.5 w-3.5 text-zinc-500" />}
        </button>

        {openSections.season && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {SEASONS.map((season) => {
              const isSelected = (filters.season || "All") === season;
              return (
                <button
                  key={season}
                  onClick={() => onFilterChange({ ...filters, season })}
                  className={`rounded-lg px-2.5 py-1 text-xs transition-all border ${
                    isSelected
                      ? "border-amber-400/40 bg-amber-400/15 text-amber-300 font-semibold shadow-glow"
                      : "border-white/[0.08] bg-[#0c1410]/70 text-zinc-400 hover:text-zinc-200 hover:border-white/[0.15]"
                  }`}
                >
                  {season}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* 4. Region Suitability */}
      <div className="border-t border-white/[0.06] pt-4">
        <button
          onClick={() => toggleSection("region")}
          className="flex w-full items-center justify-between text-xs font-semibold text-zinc-200 hover:text-emerald-400 transition-colors"
        >
          <span className="flex items-center gap-1.5">
            <MapPin className="h-3.5 w-3.5 text-lime-400" />
            <span>Regional Zone</span>
          </span>
          {openSections.region ? <ChevronUp className="h-3.5 w-3.5 text-zinc-500" /> : <ChevronDown className="h-3.5 w-3.5 text-zinc-500" />}
        </button>

        {openSections.region && (
          <div className="mt-3 space-y-1.5 max-h-40 overflow-y-auto pr-1">
            {REGIONS.map((region) => {
              const isSelected = (filters.region || "All") === region;
              return (
                <button
                  key={region}
                  onClick={() => onFilterChange({ ...filters, region })}
                  className={`w-full flex items-center justify-between rounded-lg px-2.5 py-1.5 text-xs text-left transition-all ${
                    isSelected
                      ? "bg-lime-500/20 text-lime-300 font-semibold border border-lime-500/30"
                      : "text-zinc-400 hover:bg-white/[0.04] hover:text-zinc-200"
                  }`}
                >
                  <span>{region}</span>
                  {isSelected && <span className="h-1.5 w-1.5 rounded-full bg-lime-400"></span>}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* 5. Water Requirement */}
      <div className="border-t border-white/[0.06] pt-4">
        <button
          onClick={() => toggleSection("water")}
          className="flex w-full items-center justify-between text-xs font-semibold text-zinc-200 hover:text-emerald-400 transition-colors"
        >
          <span className="flex items-center gap-1.5">
            <Droplets className="h-3.5 w-3.5 text-sky-400" />
            <span>Water Requirement</span>
          </span>
          {openSections.water ? <ChevronUp className="h-3.5 w-3.5 text-zinc-500" /> : <ChevronDown className="h-3.5 w-3.5 text-zinc-500" />}
        </button>

        {openSections.water && (
          <div className="mt-3 grid grid-cols-2 gap-1.5">
            {WATER_LEVELS.map((level) => {
              const isSelected = (filters.waterRequirement || "All") === level;
              return (
                <button
                  key={level}
                  onClick={() => onFilterChange({ ...filters, waterRequirement: level })}
                  className={`rounded-lg px-2.5 py-1.5 text-xs text-center transition-all border ${
                    isSelected
                      ? "border-sky-400/40 bg-sky-400/15 text-sky-300 font-semibold shadow-glow"
                      : "border-white/[0.08] bg-[#0c1410]/70 text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  {level}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* 6. Crop Duration Range Slider */}
      <div className="border-t border-white/[0.06] pt-4">
        <button
          onClick={() => toggleSection("duration")}
          className="flex w-full items-center justify-between text-xs font-semibold text-zinc-200 hover:text-emerald-400 transition-colors"
        >
          <span className="flex items-center gap-1.5">
            <Clock className="h-3.5 w-3.5 text-teal-400" />
            <span>Max Duration (Days)</span>
          </span>
          {openSections.duration ? <ChevronUp className="h-3.5 w-3.5 text-zinc-500" /> : <ChevronDown className="h-3.5 w-3.5 text-zinc-500" />}
        </button>

        {openSections.duration && (
          <div className="mt-3 space-y-2">
            <div className="flex items-center justify-between text-xs text-zinc-400">
              <span>Up to:</span>
              <span className="font-mono text-emerald-400 font-bold">
                {filters.maxDuration ? `${filters.maxDuration} days` : "Any (365+)"}
              </span>
            </div>
            <input
              type="range"
              min="30"
              max="365"
              step="15"
              value={filters.maxDuration || 365}
              onChange={(e) =>
                onFilterChange({
                  ...filters,
                  maxDuration: Number(e.target.value) === 365 ? undefined : Number(e.target.value),
                })
              }
              className="w-full accent-emerald-500 bg-white/[0.08] rounded-lg h-1.5 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-zinc-500">
              <span>30 d</span>
              <span>180 d</span>
              <span>365+ d</span>
            </div>
          </div>
        )}
      </div>

      {/* Results Count Footer in Sidebar */}
      <div className="pt-2 text-center text-xs text-zinc-400 border-t border-white/[0.06]">
        Matching Crops: <strong className="text-emerald-400 font-bold">{totalResults}</strong>
      </div>
    </aside>
  );
}

