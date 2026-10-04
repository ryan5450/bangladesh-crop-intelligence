"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Calendar,
  Clock,
  Droplets,
  Layers,
  MapPin,
  ShieldAlert,
  Sprout,
  Wheat,
  FlaskConical,
  RefreshCw,
  Sparkles,
  Images,
} from "lucide-react";
import { getCropByName } from "@/lib/api";
import { CropDetail } from "@/lib/types";
import GrowthTimeline from "@/components/GrowthTimeline";
import DiseaseCard from "@/components/DiseaseCard";
import ImageGallery from "@/components/ImageGallery";
import InfoCard from "@/components/InfoCard";
import { CropDetailSkeleton } from "@/components/LoadingSkeleton";

export default function CropDetailPage() {
  const params = useParams();
  const rawName = params?.name as string;
  const cropName = decodeURIComponent(rawName || "");

  const [crop, setCrop] = useState<CropDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDetail = async () => {
    if (!cropName) return;
    try {
      setLoading(true);
      setError(null);
      const data = await getCropByName(cropName);
      setCrop(data);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError(`Crop '${cropName}' was not found in the Bangladesh crop registry.`);
      } else {
        setError(
          "Unable to load crop details at this time. Please check your connection or try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [cropName]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <CropDetailSkeleton />
      </div>
    );
  }

  if (error || !crop) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <div className="rounded-3xl border border-rose-500/30 bg-[#140b0d]/80 p-8 backdrop-blur-xl">
          <ShieldAlert className="h-12 w-12 text-rose-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">Crop Intelligence Unavailable</h2>
          <p className="text-sm text-zinc-400 mb-6">{error}</p>
          <div className="flex items-center justify-center gap-4">
            <Link
              href="/crops"
              className="inline-flex items-center gap-1.5 rounded-xl border border-white/[0.1] bg-white/[0.04] px-4 py-2 text-xs font-semibold text-zinc-300 hover:text-white"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Crops</span>
            </Link>
            <button
              onClick={fetchDetail}
              className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-500 px-4 py-2 text-xs font-semibold text-black hover:bg-emerald-400 shadow-glow"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Retry</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  const agronomicParameters = [
    {
      title: "Growing Season",
      value: crop.growing_season || "Unspecified",
      icon: Calendar,
      colorScheme: "amber" as const,
    },
    {
      title: "Planting Window",
      value: crop.planting_time || "Unspecified",
      icon: Sprout,
      colorScheme: "emerald" as const,
    },
    {
      title: "Harvest Time",
      value: crop.harvest_time || "Unspecified",
      icon: Wheat,
      colorScheme: "lime" as const,
    },
    {
      title: "Crop Duration",
      value: crop.crop_duration_days || "Unspecified",
      icon: Clock,
      colorScheme: "teal" as const,
    },
    {
      title: "Water Requirement",
      value: crop.water_requirement || "Unspecified",
      icon: Droplets,
      colorScheme: "sky" as const,
    },
    {
      title: "Soil Requirement",
      value: crop.soil_requirement || "Unspecified",
      icon: Layers,
      colorScheme: "amber" as const,
    },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center justify-between">
        <Link
          href="/crops"
          className="inline-flex items-center gap-2 text-xs font-semibold text-zinc-400 hover:text-emerald-400 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Crop Registry</span>
        </Link>
      </div>

      {/* 1. HERO HEADER CARD */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="relative overflow-hidden rounded-3xl border border-white/[0.1] bg-[#0c1410]/90 p-6 sm:p-10 backdrop-blur-2xl shadow-glass"
      >
        {/* Glow ambient accent */}
        <div className="pointer-events-none absolute -top-24 -right-24 h-64 w-64 rounded-full bg-emerald-500/15 blur-3xl" />

        <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2.5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-0.5 text-xs font-semibold text-emerald-300">
                {crop.category || "Agricultural Crop"}
              </span>
              <span className="rounded-full border border-white/[0.08] bg-white/[0.02] px-3 py-0.5 text-xs text-zinc-400 font-mono">
                Registry ID #{crop.id}
              </span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-white">
              {crop.crop_name}
            </h1>

            {crop.scientific_name && (
              <p className="text-sm sm:text-base italic text-emerald-400/90 font-serif">
                {crop.scientific_name}
              </p>
            )}
          </div>
        </div>
      </motion.div>

      {/* 2. IMAGE GALLERY (Main + Multi-image showcase) */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <Images className="h-4 w-4 text-emerald-400" />
            <span>Visual Identification & Gallery</span>
          </h2>
        </div>
        <ImageGallery
          cropName={crop.crop_name}
          mainImage={crop.image_url || crop.image}
          galleryImages={crop.gallery_images}
        />
      </section>

      {/* 3. SIX AGRONOMIC PARAMETERS GRID */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-emerald-400" />
          <span>Core Agronomic Parameters</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {agronomicParameters.map((param, i) => (
            <InfoCard
              key={param.title}
              title={param.title}
              value={param.value}
              icon={param.icon}
              colorScheme={param.colorScheme}
              index={i}
            />
          ))}
          {crop.fertilizer && (
            <InfoCard
              title="Fertilizer Regime"
              value={crop.fertilizer}
              icon={FlaskConical}
              colorScheme="purple"
              index={agronomicParameters.length}
              className="sm:col-span-2 lg:col-span-3"
            />
          )}
        </div>
      </section>

      {/* 4. GROWTH STAGES TIMELINE */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <Sprout className="h-4 w-4 text-emerald-400" />
              <span>Phenological Growth Stages</span>
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              Sequential developmental milestones from sowing to harvest
            </p>
          </div>
          <span className="rounded-md border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-xs text-emerald-400 font-semibold">
            {crop.growth_stages.length} Distinct Phases
          </span>
        </div>

        <div className="rounded-3xl border border-white/[0.08] bg-[#0a100c]/60 p-6 sm:p-8 backdrop-blur-xl">
          <GrowthTimeline stages={crop.growth_stages} />
        </div>
      </section>

      {/* 5. COMMON DISEASES (PATHOLOGY) */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-rose-400" />
              <span>Common Diseases & Pathologies</span>
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              Identified biotic threats documented in Bangladesh agricultural research
            </p>
          </div>
          <span className="rounded-md border border-rose-500/20 bg-rose-500/10 px-2 py-0.5 text-xs text-rose-400 font-semibold">
            {crop.diseases.length} Pathologies Recorded
          </span>
        </div>

        {crop.diseases.length === 0 ? (
          <div className="rounded-2xl border border-white/[0.08] bg-[#0c1410]/60 p-6 text-center text-sm text-zinc-400">
            No specific diseases cataloged for this crop.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {crop.diseases.map((disease, idx) => (
              <DiseaseCard key={idx} diseaseName={disease} index={idx} />
            ))}
          </div>
        )}
      </section>

      {/* 6. BANGLADESH REGIONS */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <MapPin className="h-4 w-4 text-lime-400" />
              <span>Suitable Growing Regions in Bangladesh</span>
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              Agro-ecological zones and districts optimal for cultivation
            </p>
          </div>
          <span className="rounded-md border border-lime-500/20 bg-lime-500/10 px-2 py-0.5 text-xs text-lime-400 font-semibold">
            {crop.regions.length} Regions Mapped
          </span>
        </div>

        <div className="rounded-3xl border border-white/[0.08] bg-[#0a100c]/60 p-6 backdrop-blur-xl">
          <div className="flex flex-wrap gap-2.5">
            {crop.regions.map((region, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 rounded-xl border border-white/[0.1] bg-[#0f1712] px-3.5 py-2 text-xs font-semibold text-zinc-200 hover:border-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 transition-all"
              >
                <MapPin className="h-3.5 w-3.5 text-emerald-400" />
                <span>{region}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
