"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Save,
  Sprout,
  Image as ImageIcon,
  Check,
  AlertTriangle,
  Loader2,
  ExternalLink,
  Plus,
  Trash2,
} from "lucide-react";
import axios from "axios";
import { useAuth } from "@/context/AuthContext";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const CATEGORIES = [
  "Cereal",
  "Fruit",
  "Vegetable",
  "Cash Crop",
  "Spice",
  "Pulse",
  "Oil Crop",
];

export default function EditCropPage() {
  const params = useParams();
  const router = useRouter();
  const { getToken } = useAuth();
  const cropId = params?.id as string;

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form State
  const [cropName, setCropName] = useState("");
  const [scientificName, setScientificName] = useState("");
  const [category, setCategory] = useState("Cereal");
  const [growingSeason, setGrowingSeason] = useState("");
  const [plantingTime, setPlantingTime] = useState("");
  const [harvestTime, setHarvestTime] = useState("");
  const [soilRequirement, setSoilRequirement] = useState("");
  const [waterRequirement, setWaterRequirement] = useState("");
  const [fertilizer, setFertilizer] = useState("");
  const [cropDuration, setCropDuration] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [growthStages, setGrowthStages] = useState<Array<{ stage_number: number; stage_name: string }>>([]);
  const [diseases, setDiseases] = useState<string[]>([]);
  const [regions, setRegions] = useState<string[]>([]);
  const [newDisease, setNewDisease] = useState("");
  const [newRegion, setNewRegion] = useState("");
  const [newStage, setNewStage] = useState("");

  useEffect(() => {
    async function loadCrop() {
      setLoading(true);
      setErrorMsg(null);
      try {
        // Fetch all crops to find by ID
        const allRes = await axios.get(`${API_BASE}/crops`);
        const targetCrop = (allRes.data || []).find((c: any) => String(c.id) === String(cropId));

        if (!targetCrop) {
          setErrorMsg(`Crop with ID ${cropId} was not found.`);
          setLoading(false);
          return;
        }

        // Fetch deep details by name
        const detailRes = await axios.get(`${API_BASE}/crops/${encodeURIComponent(targetCrop.crop_name)}`);
        const data = detailRes.data;

        setCropName(data.crop_name || "");
        setScientificName(data.scientific_name || "");
        setCategory(data.category || "Cereal");
        setGrowingSeason(data.growing_season || "");
        setPlantingTime(data.planting_time || "");
        setHarvestTime(data.harvest_time || "");
        setSoilRequirement(data.soil_requirement || "");
        setWaterRequirement(data.water_requirement || "");
        setFertilizer(data.fertilizer || "");
        setCropDuration(data.crop_duration_days || "");
        setImageUrl(data.image_url || data.image || "");
        setGrowthStages(data.growth_stages || []);
        setDiseases(data.diseases || []);
        setRegions(data.regions || []);
      } catch (err: any) {
        console.error("Failed to load crop details:", err);
        setErrorMsg("Failed to load crop information from the backend.");
      } finally {
        setLoading(false);
      }
    }

    if (cropId) {
      loadCrop();
    }
  }, [cropId]);

  const handleAddDisease = () => {
    if (!newDisease.trim()) return;
    if (!diseases.includes(newDisease.trim())) {
      setDiseases([...diseases, newDisease.trim()]);
    }
    setNewDisease("");
  };

  const handleRemoveDisease = (index: number) => {
    setDiseases(diseases.filter((_, i) => i !== index));
  };

  const handleAddRegion = () => {
    if (!newRegion.trim()) return;
    if (!regions.includes(newRegion.trim())) {
      setRegions([...regions, newRegion.trim()]);
    }
    setNewRegion("");
  };

  const handleRemoveRegion = (index: number) => {
    setRegions(regions.filter((_, i) => i !== index));
  };

  const handleAddStage = () => {
    if (!newStage.trim()) return;
    const nextNumber = growthStages.length + 1;
    setGrowthStages([...growthStages, { stage_number: nextNumber, stage_name: newStage.trim() }]);
    setNewStage("");
  };

  const handleRemoveStage = (index: number) => {
    const updated = growthStages.filter((_, i) => i !== index).map((s, idx) => ({
      stage_number: idx + 1,
      stage_name: s.stage_name,
    }));
    setGrowthStages(updated);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    try {
      const payload = {
        crop_name: cropName.trim(),
        scientific_name: scientificName.trim() || null,
        category,
        growing_season: growingSeason.trim() || null,
        planting_time: plantingTime.trim() || null,
        harvest_time: harvestTime.trim() || null,
        soil_requirement: soilRequirement.trim() || null,
        water_requirement: waterRequirement.trim() || null,
        fertilizer: fertilizer.trim() || null,
        crop_duration_days: cropDuration.trim() || null,
        image_url: imageUrl.trim() || null,
        growth_stages: growthStages,
        diseases: diseases,
        regions: regions,
      };

      const token = await getToken();
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      await axios.put(`${API_BASE}/admin/crops/${cropId}`, payload, { headers });

      setSuccessMsg("Crop information updated successfully!");
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: any) {
      console.error("Failed to update crop:", err);
      setErrorMsg(err.response?.data?.detail || "Failed to update crop records.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center text-zinc-500 text-sm flex flex-col items-center justify-center gap-3">
        <Loader2 className="h-6 w-6 animate-spin text-emerald-400" />
        <span>Loading crop details...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/[0.08] pb-6">
        <div className="flex items-center gap-3">
          <Link
            href="/agri-control-panel/crops"
            className="h-9 w-9 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] flex items-center justify-center text-zinc-300 hover:text-white transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <span>Edit Crop: {cropName}</span>
            </h1>
            <p className="text-xs text-zinc-400">
              ID #{cropId} &bull; Botanical &amp; Phenological Attributes
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href={`/agri-control-panel/images?crop=${encodeURIComponent(cropName)}`}
            className="flex items-center gap-2 rounded-xl bg-white/[0.04] hover:bg-emerald-500/20 border border-white/[0.08] hover:border-emerald-500/30 px-3.5 py-2 text-xs font-medium text-emerald-300 transition-colors"
          >
            <ImageIcon className="h-4 w-4" />
            <span>Search Wikimedia Photos</span>
          </Link>
          <Link
            href={`/crops/${encodeURIComponent(cropName)}`}
            target="_blank"
            className="flex items-center gap-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] px-3.5 py-2 text-xs font-medium text-zinc-300 hover:text-white transition-colors"
          >
            <ExternalLink className="h-4 w-4" />
            <span>View Public</span>
          </Link>
        </div>
      </div>

      {/* Alerts */}
      {successMsg && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl bg-emerald-500/10 border border-emerald-500/30 p-4 text-xs text-emerald-300 flex items-center gap-3"
        >
          <Check className="h-4 w-4 text-emerald-400 shrink-0" />
          <span>{successMsg}</span>
        </motion.div>
      )}

      {errorMsg && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl bg-red-500/10 border border-red-500/30 p-4 text-xs text-red-300 flex items-center gap-3"
        >
          <AlertTriangle className="h-4 w-4 text-red-400 shrink-0" />
          <span>{errorMsg}</span>
        </motion.div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Section 1: Botanical & Taxonomic Identity */}
        <div className="glass-panel rounded-2xl p-6 border border-white/[0.08]">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
            <Sprout className="h-4 w-4 text-emerald-400" />
            <span>Botanical &amp; General Information</span>
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-zinc-300 font-medium mb-1">
                Crop Common Name *
              </label>
              <input
                type="text"
                required
                value={cropName}
                onChange={(e) => setCropName(e.target.value)}
                className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3.5 py-2.5 text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-zinc-300 font-medium mb-1">
                Scientific Name
              </label>
              <input
                type="text"
                value={scientificName}
                onChange={(e) => setScientificName(e.target.value)}
                className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3.5 py-2.5 text-white italic focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-zinc-300 font-medium mb-1">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full rounded-xl bg-[#0a100c] border border-white/[0.1] px-3.5 py-2.5 text-white focus:border-emerald-500 focus:outline-none"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Section 2: Cultivation & Agronomic Inputs */}
        <div className="glass-panel rounded-2xl p-6 border border-white/[0.08]">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
            Cultivation Calendar &amp; Requirements
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs mb-4">
            <div>
              <label className="block text-zinc-300 font-medium mb-1">
                Growing Season
              </label>
              <input
                type="text"
                value={growingSeason}
                onChange={(e) => setGrowingSeason(e.target.value)}
                className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-zinc-300 font-medium mb-1">
                Planting Time
              </label>
              <input
                type="text"
                value={plantingTime}
                onChange={(e) => setPlantingTime(e.target.value)}
                className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-zinc-300 font-medium mb-1">
                Harvest Time
              </label>
              <input
                type="text"
                value={harvestTime}
                onChange={(e) => setHarvestTime(e.target.value)}
                className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-zinc-300 font-medium mb-1">
                Crop Duration
              </label>
              <input
                type="text"
                value={cropDuration}
                onChange={(e) => setCropDuration(e.target.value)}
                className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-zinc-300 font-medium mb-1">
                Water Requirement
              </label>
              <input
                type="text"
                value={waterRequirement}
                onChange={(e) => setWaterRequirement(e.target.value)}
                className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-zinc-300 font-medium mb-1">
                Soil Requirement
              </label>
              <input
                type="text"
                value={soilRequirement}
                onChange={(e) => setSoilRequirement(e.target.value)}
                className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-zinc-300 font-medium mb-1">
                Fertilizer Regimen
              </label>
              <input
                type="text"
                value={fertilizer}
                onChange={(e) => setFertilizer(e.target.value)}
                className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Section 3: Media & Primary Image */}
        <div className="glass-panel rounded-2xl p-6 border border-white/[0.08]">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
            <ImageIcon className="h-4 w-4 text-cyan-400" />
            <span>Crop Media &amp; Image URL</span>
          </h2>
          <div className="flex flex-col sm:flex-row items-start gap-6 text-xs">
            <div className="h-28 w-28 rounded-2xl bg-black/40 border border-white/[0.1] overflow-hidden flex items-center justify-center shrink-0">
              {imageUrl ? (
                /* eslint-disable-next-line @next/next/no-img-element */
                <img
                  src={imageUrl}
                  alt={cropName}
                  className="h-full w-full object-cover"
                />
              ) : (
                <ImageIcon className="h-8 w-8 text-zinc-600" />
              )}
            </div>

            <div className="flex-1 w-full space-y-3">
              <div>
                <label className="block text-zinc-300 font-medium mb-1">
                  Primary Image URL (Supabase Storage / External)
                </label>
                <input
                  type="text"
                  value={imageUrl}
                  onChange={(e) => setImageUrl(e.target.value)}
                  placeholder="https://braiwlsjyczorxuxtifi.supabase.co/storage/v1/object/public/crops/..."
                  className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3.5 py-2 text-white font-mono text-[11px] focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center gap-3">
                <Link
                  href={`/agri-control-panel/images?crop=${encodeURIComponent(cropName)}`}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 px-3 py-1.5 text-xs text-emerald-300 font-medium transition-colors"
                >
                  <ImageIcon className="h-3.5 w-3.5" />
                  <span>Find Image via Wikimedia Auto-Search</span>
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Section 4: Phenological Growth Stages */}
        <div className="glass-panel rounded-2xl p-6 border border-white/[0.08]">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
              Phenological Growth Stages Timeline
            </h2>
            <span className="text-xs text-zinc-400 font-mono">
              {growthStages.length} Stages
            </span>
          </div>

          <div className="space-y-2 mb-4">
            {growthStages.map((stage, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between rounded-xl bg-black/30 border border-white/[0.06] px-4 py-2.5 text-xs"
              >
                <div className="flex items-center gap-3">
                  <span className="h-5 w-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-[10px]">
                    {stage.stage_number}
                  </span>
                  <span className="text-white font-medium">{stage.stage_name}</span>
                </div>
                <button
                  type="button"
                  onClick={() => handleRemoveStage(idx)}
                  className="text-red-400 hover:text-red-300 transition-colors"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={newStage}
              onChange={(e) => setNewStage(e.target.value)}
              placeholder="Add next growth stage (e.g. Grain Filling, Tillering)..."
              className="flex-1 rounded-xl bg-black/40 border border-white/[0.1] px-3.5 py-2 text-xs text-white focus:border-emerald-500 focus:outline-none"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  handleAddStage();
                }
              }}
            />
            <button
              type="button"
              onClick={handleAddStage}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white/[0.06] hover:bg-white/[0.1] border border-white/[0.1] text-xs text-zinc-200 transition-colors"
            >
              <Plus className="h-3.5 w-3.5" />
              <span>Add Stage</span>
            </button>
          </div>
        </div>

        {/* Section 5: Diseases & Regional Distribution */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Diseases */}
          <div className="glass-panel rounded-2xl p-6 border border-white/[0.08]">
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">
              Common Plant Pathologies / Diseases
            </h2>
            <div className="flex flex-wrap gap-1.5 mb-4 min-h-[40px]">
              {diseases.map((d, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs bg-red-500/10 text-red-300 border border-red-500/20"
                >
                  <span>{d}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveDisease(idx)}
                    className="hover:text-red-100"
                  >
                    &times;
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newDisease}
                onChange={(e) => setNewDisease(e.target.value)}
                placeholder="Add disease..."
                className="flex-1 rounded-xl bg-black/40 border border-white/[0.1] px-3 py-1.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddDisease();
                  }
                }}
              />
              <button
                type="button"
                onClick={handleAddDisease}
                className="px-3 py-1.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.1] text-xs text-zinc-300"
              >
                Add
              </button>
            </div>
          </div>

          {/* Regions */}
          <div className="glass-panel rounded-2xl p-6 border border-white/[0.08]">
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">
              Cultivation Regions (Divisions / Districts)
            </h2>
            <div className="flex flex-wrap gap-1.5 mb-4 min-h-[40px]">
              {regions.map((r, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs bg-emerald-500/10 text-emerald-300 border border-emerald-500/20"
                >
                  <span>{r}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveRegion(idx)}
                    className="hover:text-emerald-100"
                  >
                    &times;
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newRegion}
                onChange={(e) => setNewRegion(e.target.value)}
                placeholder="Add region..."
                className="flex-1 rounded-xl bg-black/40 border border-white/[0.1] px-3 py-1.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddRegion();
                  }
                }}
              />
              <button
                type="button"
                onClick={handleAddRegion}
                className="px-3 py-1.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.1] text-xs text-zinc-300"
              >
                Add
              </button>
            </div>
          </div>
        </div>

        {/* Save Bar */}
        <div className="flex items-center justify-end gap-4 pt-4 border-t border-white/[0.08]">
          <Link
            href="/agri-control-panel/crops"
            className="px-5 py-2.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] text-xs font-medium text-zinc-300 transition-colors"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-semibold text-xs transition-all shadow-glow hover:shadow-glow-lg disabled:opacity-50"
          >
            {saving ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Saving Changes...</span>
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                <span>Save Crop Changes</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

