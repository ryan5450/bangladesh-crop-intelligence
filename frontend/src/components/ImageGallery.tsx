"use client";

import React, { useState } from "react";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { Image as ImageIcon, Sparkles, ZoomIn, Check } from "lucide-react";
import { CropImage } from "@/lib/types";

interface ImageGalleryProps {
  mainImage?: string | null;
  cropName: string;
  galleryImages?: CropImage[];
}

export default function ImageGallery({
  mainImage,
  cropName,
  galleryImages = [],
}: ImageGalleryProps) {
  // Consolidate images into unified list
  const allImages: CropImage[] = [];

  if (mainImage) {
    allImages.push({
      id: 0,
      image_url: mainImage,
      caption: `${cropName} - Primary View`,
      is_primary: true,
    });
  }

  // Add remaining gallery items if not duplicate
  galleryImages.forEach((img, idx) => {
    if (img.image_url && img.image_url !== mainImage) {
      allImages.push({
        id: img.id || idx + 1,
        image_url: img.image_url,
        caption: img.caption || `${cropName} View #${idx + 2}`,
        is_primary: img.is_primary,
      });
    }
  });

  const [activeIndex, setActiveIndex] = useState(0);
  const activeImage = allImages[activeIndex] || null;

  if (allImages.length === 0) {
    return (
      <div className="relative flex aspect-video w-full flex-col items-center justify-center rounded-3xl border border-white/[0.08] bg-[#0c1410]/70 p-8 text-center backdrop-blur-xl">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mb-3">
          <ImageIcon className="h-6 w-6" />
        </div>
        <h4 className="text-sm font-semibold text-white">Visual Profile for {cropName}</h4>
        <p className="text-xs text-zinc-400 mt-1 max-w-xs">
          High-resolution imagery can be managed and uploaded via the Admin Portal.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 1. Main Display Image */}
      <div className="relative aspect-[16/9] w-full overflow-hidden rounded-3xl border border-white/[0.1] bg-[#0a100c] shadow-glass group">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeImage?.image_url || activeIndex}
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="relative h-full w-full"
          >
            {activeImage?.image_url && (activeImage.image_url.startsWith("http") || activeImage.image_url.startsWith("/")) ? (
              <img
                src={activeImage.image_url}
                alt={activeImage.caption || cropName}
                className="h-full w-full object-cover object-center transition-transform duration-700 group-hover:scale-105"
              />
            ) : (
              <div className="flex h-full w-full flex-col items-center justify-center bg-gradient-to-br from-emerald-950/40 via-[#0a100c] to-black p-6 text-center">
                <ImageIcon className="h-16 w-16 text-emerald-500/40 mb-2" />
                <span className="text-sm font-bold text-white">{cropName}</span>
                <span className="text-xs text-zinc-400 font-mono mt-1">{activeImage?.image_url}</span>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Ambient overlay & caption pill */}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
        <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between text-xs">
          <span className="rounded-xl border border-white/[0.1] bg-black/60 px-3 py-1.5 font-medium text-white backdrop-blur-md">
            {activeImage?.caption || cropName}
          </span>
          <span className="rounded-xl border border-white/[0.1] bg-black/60 px-2.5 py-1 text-[11px] text-zinc-300 font-mono backdrop-blur-md">
            {activeIndex + 1} / {allImages.length}
          </span>
        </div>
      </div>

      {/* 2. Gallery Thumbnails Strip (if multiple images) */}
      {allImages.length > 1 && (
        <div className="flex items-center gap-3 overflow-x-auto pb-1 scrollbar-none">
          {allImages.map((img, idx) => {
            const isSelected = activeIndex === idx;
            return (
              <button
                key={img.id || idx}
                onClick={() => setActiveIndex(idx)}
                className={`relative h-16 w-24 shrink-0 overflow-hidden rounded-xl border transition-all duration-200 ${
                  isSelected
                    ? "border-emerald-400 shadow-glow ring-2 ring-emerald-500/30 scale-105"
                    : "border-white/[0.1] opacity-60 hover:opacity-100"
                }`}
              >
                {img.image_url && (img.image_url.startsWith("http") || img.image_url.startsWith("/")) ? (
                  <img
                    src={img.image_url}
                    alt={img.caption || `Thumbnail ${idx}`}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center bg-[#0c1410] text-[10px] text-zinc-400 font-mono">
                    #{idx + 1}
                  </div>
                )}
                {isSelected && (
                  <div className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-emerald-500 text-black">
                    <Check className="h-2.5 w-2.5 stroke-[3]" />
                  </div>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

