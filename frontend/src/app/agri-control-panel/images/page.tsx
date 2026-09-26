"use client";

import React, { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Image as ImageIcon,
  Search,
  Sprout,
  Upload,
  Check,
  AlertCircle,
  ExternalLink,
  Loader2,
  Sparkles,
  Layers,
  ArrowRight,
} from "lucide-react";
import axios from "axios";
import { useAuth } from "@/context/AuthContext";

interface CropOption {
  id: number;
  crop_name: string;
  scientific_name?: string;
  category?: string;
  image?: string;
  image_url?: string;
  gallery_urls?: any[];
}

interface WikimediaImage {
  page_id: string;
  title: string;
  thumbnail_url: string;
  original_url: string;
  width: number;
  height: number;
  mime: string;
  description_url: string;
  artist: string;
  license: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

function ImageStudioContent() {
  const searchParams = useSearchParams();
  const initialCropParam = searchParams.get("crop") || "";
  const { getToken } = useAuth();

  const [crops, setCrops] = useState<CropOption[]>([]);
  const [selectedCrop, setSelectedCrop] = useState<CropOption | null>(null);
  const [cropsLoading, setCropsLoading] = useState(true);

  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchingWiki, setSearchingWiki] = useState(false);
  const [candidateImages, setCandidateImages] = useState<WikimediaImage[]>([]);
  const [wikiError, setWikiError] = useState<string | null>(null);

  // Upload state
  const [uploadingUrl, setUploadingUrl] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Current crop detailed state
  const [currentCropDetails, setCurrentCropDetails] = useState<any | null>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  // Load all crops on mount
  useEffect(() => {
    async function loadCrops() {
      setCropsLoading(true);
      try {
        const res = await axios.get(`${API_BASE}/crops`);
        const allCrops: CropOption[] = res.data || [];
        setCrops(allCrops);

        if (initialCropParam) {
          const match = allCrops.find(
            (c) => c.crop_name.toLowerCase() === initialCropParam.toLowerCase()
          );
          if (match) {
            handleSelectCrop(match);
          }
        } else if (allCrops.length > 0) {
          handleSelectCrop(allCrops[0]);
        }
      } catch (err) {
        console.error("Failed to load crops:", err);
      } finally {
        setCropsLoading(false);
      }
    }
    loadCrops();
  }, [initialCropParam]);

  const handleSelectCrop = async (crop: CropOption) => {
    setSelectedCrop(crop);
    setSearchQuery(crop.scientific_name ? `${crop.crop_name} ${crop.scientific_name}` : crop.crop_name);
    fetchCropDetails(crop.crop_name);
    searchWikimedia(crop.scientific_name ? `${crop.crop_name} ${crop.scientific_name}` : crop.crop_name);
  };

  const fetchCropDetails = async (cropName: string) => {
    setDetailsLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/crops/${encodeURIComponent(cropName)}`);
      setCurrentCropDetails(res.data);
    } catch (err) {
      console.error("Failed to load crop details:", err);
    } finally {
      setDetailsLoading(false);
    }
  };

  const searchWikimedia = async (term: string) => {
    if (!term.trim()) return;
    setSearchingWiki(true);
    setWikiError(null);
    try {
      const res = await axios.get(`${API_BASE}/admin/search-images`, {
        params: { query: term.trim(), limit: 16 },
      });
      const images: WikimediaImage[] = res.data.images || [];
      setCandidateImages(images);
      if (images.length === 0) {
        setWikiError(`No suitable images found on Wikimedia Commons for "${term}". Try searching with alternative keywords.`);
      }
    } catch (err: any) {
      console.error("Wikimedia search failed:", err);
      setWikiError(err.response?.data?.detail || "Failed to query Wikimedia Commons API.");
      setCandidateImages([]);
    } finally {
      setSearchingWiki(false);
    }
  };

  const handleSelectImageForCrop = async (
    image: WikimediaImage,
    imageType: "main" | "gallery"
  ) => {
    if (!selectedCrop) return;

    setUploadingUrl(image.original_url);
    setUploadSuccess(null);
    setUploadError(null);

    try {
      const formData = new FormData();
      formData.append("image_url", image.original_url);
      formData.append("crop_id", String(selectedCrop.id));
      formData.append("image_type", imageType);
      formData.append("caption", image.title || selectedCrop.crop_name);

      const token = await getToken();
      const headers: Record<string, string> = {
        "Content-Type": "multipart/form-data",
      };
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const res = await axios.post(`${API_BASE}/admin/upload-image`, formData, { headers });

      const uploadedUrl = res.data.url || res.data.image_url;

      setUploadSuccess(
        `Successfully downloaded & stored in Supabase as ${
          imageType === "main" ? "Main Image" : "Gallery Image"
        }!`
      );

      // Refresh local crop details and crops list
      fetchCropDetails(selectedCrop.crop_name);

      // Update selected crop state
      if (imageType === "main") {
        setSelectedCrop({
          ...selectedCrop,
          image_url: uploadedUrl,
          image: uploadedUrl,
        });
      }

      setTimeout(() => setUploadSuccess(null), 5000);
    } catch (err: any) {
      console.error("Failed to upload image:", err);
      setUploadError(
        err.response?.data?.detail || "Storage upload failed. Ensure the 'crops' bucket exists in Supabase."
      );
    } finally {
      setUploadingUrl(null);
    }
  };

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/[0.08] pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <span className="flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-emerald-400" />
              <span>Automated Crop Image Management</span>
            </span>
          </h1>
          <p className="mt-1 text-sm text-zinc-400">
            Automated image discovery via Wikimedia Commons API &bull; 1-click sync to Supabase Storage
          </p>
        </div>

        {selectedCrop && (
          <Link
            href={`/crops/${encodeURIComponent(selectedCrop.crop_name)}`}
            target="_blank"
            className="flex items-center gap-2 rounded-xl bg-white/[0.04] hover:bg-emerald-500/20 border border-white/[0.08] px-4 py-2 text-xs font-medium text-emerald-300 transition-colors self-start sm:self-auto"
          >
            <span>Preview on Public Site</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </Link>
        )}
      </div>

      {/* Notifications */}
      {uploadSuccess && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl bg-emerald-500/15 border border-emerald-500/40 p-4 text-xs text-emerald-200 flex items-center gap-3 shadow-glow"
        >
          <Check className="h-5 w-5 text-emerald-400 shrink-0" />
          <span className="font-medium">{uploadSuccess}</span>
        </motion.div>
      )}

      {uploadError && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl bg-red-500/15 border border-red-500/40 p-4 text-xs text-red-200 flex items-center gap-3"
        >
          <AlertCircle className="h-5 w-5 text-red-400 shrink-0" />
          <div>
            <p className="font-semibold">Storage Upload Failed</p>
            <p className="mt-0.5 text-zinc-400">{uploadError}</p>
          </div>
        </motion.div>
      )}

      {/* Crop Selector & Search Toolbar */}
      <div className="glass-panel rounded-2xl p-6 border border-white/[0.08] space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Crop Selector */}
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-zinc-400 mb-1.5">
              1. Select Crop to Update
            </label>
            <div className="relative">
              <select
                disabled={cropsLoading}
                value={selectedCrop?.id || ""}
                onChange={(e) => {
                  const crop = crops.find((c) => String(c.id) === e.target.value);
                  if (crop) handleSelectCrop(crop);
                }}
                className="w-full rounded-xl bg-black/50 border border-white/[0.1] px-4 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 font-medium"
              >
                {crops.map((crop) => (
                  <option key={crop.id} value={crop.id} className="bg-[#0c120e]">
                    {crop.crop_name} {crop.scientific_name ? `(${crop.scientific_name})` : ""} &bull; {crop.category}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Wikimedia Search Input */}
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-zinc-400 mb-1.5">
              2. Wikimedia Commons Search Term
            </label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="e.g. Mangifera indica tree, Rice paddy..."
                  className="w-full rounded-xl bg-black/50 border border-white/[0.1] pl-10 pr-4 py-2 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-emerald-500"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      searchWikimedia(searchQuery);
                    }
                  }}
                />
              </div>
              <button
                type="button"
                onClick={() => searchWikimedia(searchQuery)}
                disabled={searchingWiki || !searchQuery.trim()}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-semibold text-xs shadow-glow transition-all disabled:opacity-50"
              >
                {searchingWiki ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
                <span>Search</span>
              </button>
            </div>
          </div>
        </div>

        {/* Selected Crop Current Media Bar */}
        {selectedCrop && (
          <div className="pt-4 border-t border-white/[0.06] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="h-14 w-14 rounded-xl bg-black/40 border border-white/[0.1] overflow-hidden shrink-0 flex items-center justify-center">
                {currentCropDetails?.image_url || currentCropDetails?.image ? (
                  /* eslint-disable-next-line @next/next/no-img-element */
                  <img
                    src={currentCropDetails.image_url || currentCropDetails.image}
                    alt={selectedCrop.crop_name}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <Sprout className="h-6 w-6 text-emerald-400" />
                )}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-white text-base">
                    {selectedCrop.crop_name}
                  </h3>
                  <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {selectedCrop.category}
                  </span>
                </div>
                <p className="text-xs text-zinc-400 italic">
                  {selectedCrop.scientific_name || "Taxonomy unassigned"}
                </p>
                <div className="flex items-center gap-4 mt-1 text-[11px] text-zinc-400">
                  <span>
                    Gallery Photos:{" "}
                    <strong className="text-white">
                      {currentCropDetails?.gallery_images?.length || 0}
                    </strong>
                  </span>
                  <span>&bull;</span>
                  <span>
                    Primary Image:{" "}
                    {currentCropDetails?.image_url ? (
                      <span className="text-emerald-400 font-semibold">Supabase Storage</span>
                    ) : (
                      <span className="text-amber-400">Local Asset</span>
                    )}
                  </span>
                </div>
              </div>
            </div>

            <div className="text-xs text-zinc-400">
              <span>Select any photo below to automatically download and sync.</span>
            </div>
          </div>
        )}
      </div>

      {/* Candidate Wikimedia Images Gallery */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <ImageIcon className="h-4 w-4 text-emerald-400" />
            <span>Wikimedia Commons Candidate Results</span>
            {candidateImages.length > 0 && (
              <span className="text-xs font-mono font-normal text-zinc-400">
                ({candidateImages.length} found)
              </span>
            )}
          </h2>
          {searchingWiki && (
            <div className="flex items-center gap-2 text-xs text-emerald-400">
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              <span>Querying Wikimedia Commons API...</span>
            </div>
          )}
        </div>

        {wikiError && (
          <div className="rounded-xl bg-amber-500/10 border border-amber-500/20 p-4 text-xs text-amber-300">
            {wikiError}
          </div>
        )}

        {candidateImages.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {candidateImages.map((img) => {
              const isCurrentlyUploading = uploadingUrl === img.original_url;

              return (
                <div
                  key={img.page_id}
                  className="glass-panel rounded-2xl border border-white/[0.08] overflow-hidden flex flex-col group hover:border-emerald-500/30 transition-all shadow-lg"
                >
                  {/* Image Preview Container */}
                  <div className="relative aspect-[4/3] bg-black/60 overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={img.thumbnail_url}
                      alt={img.title}
                      loading="lazy"
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />

                    {/* Resolution Pill */}
                    <div className="absolute top-2.5 right-2.5 px-2 py-0.5 rounded-md bg-black/70 backdrop-blur-md text-[10px] font-mono text-zinc-300 border border-white/[0.1]">
                      {img.width} &times; {img.height}
                    </div>

                    {/* Source Attribution Link */}
                    <a
                      href={img.description_url}
                      target="_blank"
                      rel="noreferrer"
                      title="View on Wikimedia Commons"
                      className="absolute bottom-2.5 left-2.5 p-1.5 rounded-lg bg-black/70 backdrop-blur-md text-zinc-300 hover:text-white transition-colors"
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>

                  {/* Card Metadata */}
                  <div className="p-4 flex-1 flex flex-col justify-between text-xs space-y-3">
                    <div>
                      <h4
                        className="font-semibold text-white line-clamp-2 leading-snug"
                        title={img.title}
                      >
                        {img.title}
                      </h4>
                      <p className="mt-1 text-[11px] text-zinc-400 line-clamp-1">
                        Author: {img.artist} &bull; {img.license}
                      </p>
                    </div>

                    {/* Action Buttons */}
                    <div className="pt-2 border-t border-white/[0.06] space-y-1.5">
                      <button
                        type="button"
                        disabled={isCurrentlyUploading || !selectedCrop}
                        onClick={() => handleSelectImageForCrop(img, "main")}
                        className="w-full flex items-center justify-center gap-1.5 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-300 hover:text-emerald-200 font-semibold py-2 px-3 text-[11px] transition-all disabled:opacity-50"
                      >
                        {isCurrentlyUploading ? (
                          <>
                            <Loader2 className="h-3.5 w-3.5 animate-spin" />
                            <span>Uploading to Storage...</span>
                          </>
                        ) : (
                          <>
                            <Check className="h-3.5 w-3.5 text-emerald-400" />
                            <span>Set as Main Image</span>
                          </>
                        )}
                      </button>

                      <button
                        type="button"
                        disabled={isCurrentlyUploading || !selectedCrop}
                        onClick={() => handleSelectImageForCrop(img, "gallery")}
                        className="w-full flex items-center justify-center gap-1.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-zinc-300 hover:text-white font-medium py-1.5 px-3 text-[11px] transition-all disabled:opacity-50"
                      >
                        <Layers className="h-3.5 w-3.5 text-zinc-400" />
                        <span>Add to Crop Gallery</span>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          !searchingWiki && (
            <div className="glass-panel rounded-2xl p-12 text-center border border-white/[0.08]">
              <ImageIcon className="h-10 w-10 text-zinc-600 mx-auto mb-3" />
              <p className="text-sm text-zinc-400 font-medium">
                No Wikimedia photos loaded.
              </p>
              <p className="text-xs text-zinc-500 mt-1">
                Select a crop from the dropdown above and click Search to discover authentic agricultural photos.
              </p>
            </div>
          )
        )}
      </div>

      {/* Current Stored Gallery for Selected Crop */}
      {selectedCrop && currentCropDetails && currentCropDetails.gallery_images?.length > 0 && (
        <div className="glass-panel rounded-2xl p-6 border border-white/[0.08]">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
            <Layers className="h-4 w-4 text-emerald-400" />
            <span>Currently Linked Photos for {selectedCrop.crop_name}</span>
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
            {currentCropDetails.gallery_images.map((item: any, idx: number) => (
              <div
                key={idx}
                className="relative rounded-xl overflow-hidden aspect-square border border-white/[0.08] bg-black/40 group"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={item.image_url}
                  alt={item.caption || selectedCrop.crop_name}
                  className="h-full w-full object-cover"
                />
                {item.is_primary && (
                  <span className="absolute top-1.5 left-1.5 bg-emerald-500 text-black font-bold text-[9px] px-1.5 py-0.5 rounded uppercase">
                    Main
                  </span>
                )}
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center p-2 text-center text-[10px] text-zinc-300">
                  <span className="line-clamp-2">{item.caption || "Crop Photo"}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function AutomatedImageManagementPage() {
  return (
    <Suspense
      fallback={
        <div className="py-24 text-center text-zinc-500 text-sm flex flex-col items-center justify-center gap-3">
          <Loader2 className="h-6 w-6 animate-spin text-emerald-400" />
          <span>Loading Automated Image Studio...</span>
        </div>
      }
    >
      <ImageStudioContent />
    </Suspense>
  );
}

