"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Search, Loader2, X, ArrowRight, Sprout } from "lucide-react";
import { searchCrops } from "@/lib/api";
import { CropSummary } from "@/lib/types";

interface SearchBarProps {
  placeholder?: string;
  className?: string;
  onSelectCrop?: (crop: CropSummary) => void;
}

export default function SearchBar({
  placeholder = "Search 25+ crops (e.g. Rice, Mango, Potato)...",
  className = "",
  onSelectCrop,
}: SearchBarProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<CropSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  // Debounced search query
  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    const timeoutId = setTimeout(async () => {
      try {
        const data = await searchCrops(query.trim());
        setResults(data);
        setIsOpen(true);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleSelect = (crop: CropSummary) => {
    setIsOpen(false);
    setQuery("");
    if (onSelectCrop) {
      onSelectCrop(crop);
    } else {
      router.push(`/crops/${encodeURIComponent(crop.crop_name)}`);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setIsOpen(false);
    // If only one exact result, navigate to it, otherwise go to /crops with query
    if (results.length === 1) {
      handleSelect(results[0]);
    } else {
      router.push(`/crops?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <div ref={containerRef} className={`relative w-full ${className}`}>
      <form onSubmit={handleFormSubmit} className="relative flex items-center">
        <div className="pointer-events-none absolute left-4 text-emerald-400">
          {loading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Search className="h-5 w-5" />
          )}
        </div>

        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            if (!isOpen) setIsOpen(true);
          }}
          onFocus={() => {
            if (results.length > 0) setIsOpen(true);
          }}
          placeholder={placeholder}
          className="w-full rounded-2xl border border-white/[0.1] bg-[#0c1410]/90 py-3.5 pl-12 pr-11 text-sm text-white placeholder-zinc-500 backdrop-blur-xl transition-all focus:border-emerald-500 focus:bg-[#101b15] focus:outline-none focus:ring-2 focus:ring-emerald-500/20 shadow-glass"
        />

        {query && (
          <button
            type="button"
            onClick={() => {
              setQuery("");
              setResults([]);
              setIsOpen(false);
            }}
            className="absolute right-3.5 rounded-lg p-1 text-zinc-400 hover:bg-white/[0.05] hover:text-white"
            aria-label="Clear search"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </form>

      {/* Live Suggestion Dropdown */}
      {isOpen && query.trim().length > 0 && (
        <div className="absolute top-full left-0 z-50 mt-2 w-full overflow-hidden rounded-2xl border border-white/[0.1] bg-[#0c1410]/95 backdrop-blur-2xl shadow-2xl">
          {loading ? (
            <div className="flex items-center justify-center py-6 text-sm text-zinc-400 gap-2">
              <Loader2 className="h-4 w-4 animate-spin text-emerald-400" />
              <span>Searching Bangladesh crop registry...</span>
            </div>
          ) : results.length > 0 ? (
            <div className="py-2">
              <div className="px-3.5 py-1.5 text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
                Matching Crops ({results.length})
              </div>
              <div className="max-h-72 overflow-y-auto divide-y divide-white/[0.04]">
                {results.map((crop) => (
                  <button
                    key={crop.id}
                    onClick={() => handleSelect(crop)}
                    className="w-full flex items-center justify-between px-4 py-2.5 text-left text-sm text-zinc-200 hover:bg-emerald-500/10 hover:text-emerald-300 transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 group-hover:border-emerald-400">
                        <Sprout className="h-3.5 w-3.5" />
                      </div>
                      <div>
                        <span className="font-semibold text-white group-hover:text-emerald-300">
                          {crop.crop_name}
                        </span>
                        <span className="ml-2 text-xs text-zinc-400">
                          ({crop.category || "General"})
                        </span>
                      </div>
                    </div>
                    <ArrowRight className="h-4 w-4 text-zinc-500 group-hover:text-emerald-400 transition-transform group-hover:translate-x-1" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="py-6 text-center text-sm text-zinc-400">
              No crops found matching &quot;<span className="text-zinc-200">{query}</span>&quot;
            </div>
          )}
        </div>
      )}
    </div>
  );
}

