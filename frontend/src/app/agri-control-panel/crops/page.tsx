"use client";

import React, { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sprout,
  Search,
  Plus,
  Edit,
  Trash2,
  Image as ImageIcon,
  Check,
  AlertTriangle,
  X,
  ExternalLink,
  Filter,
  Loader2,
} from "lucide-react";
import axios from "axios";
import { useAuth } from "@/context/AuthContext";

interface CropItem {
  id: number;
  crop_name: string;
  scientific_name?: string;
  category?: string;
  growing_season?: string;
  water_requirement?: string;
  crop_duration_days?: string;
  image?: string;
  image_url?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const CATEGORIES = [
  "All",
  "Cereal",
  "Fruit",
  "Vegetable",
  "Cash Crop",
  "Spice",
  "Pulse",
  "Oil Crop",
];

export default function AdminCropsPage() {
  const { getToken } = useAuth();
  const [crops, setCrops] = useState<CropItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");

  // Modal states
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<CropItem | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  // Add Crop Form State
  const [formName, setFormName] = useState("");
  const [formScientific, setFormScientific] = useState("");
  const [formCategory, setFormCategory] = useState("Cereal");
  const [formSeason, setFormSeason] = useState("Rabi");
  const [formPlanting, setFormPlanting] = useState("");
  const [formHarvest, setFormHarvest] = useState("");
  const [formSoil, setFormSoil] = useState("");
  const [formWater, setFormWater] = useState("Moderate");
  const [formFertilizer, setFormFertilizer] = useState("");
  const [formDuration, setFormDuration] = useState("");
  const [formRegions, setFormRegions] = useState("Dhaka, Rajshahi, Rangpur");
  const [formDiseases, setFormDiseases] = useState("Leaf Blight");
  const [formStages, setFormStages] = useState("Seedling, Vegetative, Flowering, Maturity");
  const [isSaving, setIsSaving] = useState(false);

  const fetchCrops = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/crops`);
      setCrops(res.data || []);
    } catch (err) {
      console.error("Failed to load crops:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCrops();
  }, []);

  const filteredCrops = useMemo(() => {
    return crops.filter((crop) => {
      const matchesSearch =
        !searchQuery.trim() ||
        crop.crop_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (crop.scientific_name || "").toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCat =
        selectedCategory === "All" ||
        (crop.category || "").toLowerCase() === selectedCategory.toLowerCase();

      return matchesSearch && matchesCat;
    });
  }, [crops, searchQuery, selectedCategory]);

  const handleCreateCrop = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    setIsSaving(true);

    try {
      const stagesArray = formStages
        .split(",")
        .map((s, idx) => ({ stage_number: idx + 1, stage_name: s.trim() }))
        .filter((s) => s.stage_name);

      const diseasesArray = formDiseases
        .split(",")
        .map((d) => d.trim())
        .filter(Boolean);

      const regionsArray = formRegions
        .split(",")
        .map((r) => r.trim())
        .filter(Boolean);

      const payload = {
        crop_name: formName.trim(),
        scientific_name: formScientific.trim() || null,
        category: formCategory,
        growing_season: formSeason,
        planting_time: formPlanting.trim() || null,
        harvest_time: formHarvest.trim() || null,
        soil_requirement: formSoil.trim() || null,
        water_requirement: formWater.trim() || null,
        fertilizer: formFertilizer.trim() || null,
        crop_duration_days: formDuration.trim() || null,
        growth_stages: stagesArray,
        diseases: diseasesArray,
        regions: regionsArray,
      };

      const token = await getToken();
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      await axios.post(`${API_BASE}/admin/crops`, payload, { headers });

      setActionSuccess(`Successfully added crop '${formName}'!`);
      setIsAddModalOpen(false);
      resetForm();
      fetchCrops();
      setTimeout(() => setActionSuccess(null), 4000);
    } catch (err: any) {
      console.error("Failed to add crop:", err);
      setActionError(
        err.response?.data?.detail || "Failed to create crop. Please verify unique name."
      );
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    setIsDeleting(true);
    setActionError(null);

    try {
      const token = await getToken();
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      await axios.delete(`${API_BASE}/admin/crops/${deleteTarget.id}`, { headers });
      setActionSuccess(`Successfully deleted '${deleteTarget.crop_name}'`);
      setDeleteTarget(null);
      fetchCrops();
      setTimeout(() => setActionSuccess(null), 4000);
    } catch (err: any) {
      console.error("Failed to delete crop:", err);
      setActionError(err.response?.data?.detail || "Failed to delete crop.");
    } finally {
      setIsDeleting(false);
    }
  };

  const resetForm = () => {
    setFormName("");
    setFormScientific("");
    setFormCategory("Cereal");
    setFormSeason("Rabi");
    setFormPlanting("");
    setFormHarvest("");
    setFormSoil("");
    setFormWater("Moderate");
    setFormFertilizer("");
    setFormDuration("");
    setFormRegions("Dhaka, Rajshahi, Rangpur");
    setFormDiseases("Leaf Blight");
    setFormStages("Seedling, Vegetative, Flowering, Maturity");
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/[0.08] pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <span>Crop Inventory Management</span>
            <span className="text-xs font-mono font-normal bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-0.5 rounded-full">
              {crops.length} Total
            </span>
          </h1>
          <p className="mt-1 text-sm text-zinc-400">
            Create, modify botanical parameters, link regional distributions, and update media
          </p>
        </div>

        <button
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center justify-center gap-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black px-4 py-2.5 text-xs font-semibold shadow-glow hover:shadow-glow-lg transition-all"
        >
          <Plus className="h-4 w-4" />
          <span>Add New Crop</span>
        </button>
      </div>

      {/* Success / Error Banners */}
      {actionSuccess && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl bg-emerald-500/10 border border-emerald-500/30 p-4 text-xs text-emerald-300 flex items-center gap-3"
        >
          <Check className="h-4 w-4 text-emerald-400 shrink-0" />
          <span>{actionSuccess}</span>
        </motion.div>
      )}

      {actionError && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl bg-red-500/10 border border-red-500/30 p-4 text-xs text-red-300 flex items-center gap-3"
        >
          <AlertTriangle className="h-4 w-4 text-red-400 shrink-0" />
          <span>{actionError}</span>
        </motion.div>
      )}

      {/* Filter and Search Controls */}
      <div className="glass-panel rounded-2xl p-4 border border-white/[0.08] flex flex-col md:flex-row items-center gap-4">
        {/* Search Input */}
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search crop name, botanical name..."
            className="w-full rounded-xl bg-black/40 border border-white/[0.1] pl-10 pr-4 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
          />
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0">
          <Filter className="h-3.5 w-3.5 text-zinc-500 shrink-0 mr-1" />
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                selectedCategory === cat
                  ? "bg-emerald-500 text-black font-semibold"
                  : "bg-white/[0.04] text-zinc-400 hover:text-white hover:bg-white/[0.08]"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Crops Table */}
      <div className="glass-panel rounded-2xl border border-white/[0.08] overflow-hidden">
        {loading ? (
          <div className="py-20 text-center text-zinc-500 text-sm flex flex-col items-center justify-center gap-3">
            <Loader2 className="h-6 w-6 animate-spin text-emerald-400" />
            <span>Loading crop database...</span>
          </div>
        ) : filteredCrops.length === 0 ? (
          <div className="py-16 text-center text-zinc-500 text-sm">
            No crops matched the selected criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-white/[0.08] bg-black/30 text-zinc-400 uppercase tracking-wider font-semibold">
                  <th className="py-3.5 pl-4">Photo</th>
                  <th className="py-3.5">Crop Name</th>
                  <th className="py-3.5">Category</th>
                  <th className="py-3.5">Growing Season</th>
                  <th className="py-3.5">Duration</th>
                  <th className="py-3.5">Water Needs</th>
                  <th className="py-3.5 text-right pr-4">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filteredCrops.map((crop) => (
                  <tr
                    key={crop.id}
                    className="hover:bg-white/[0.02] transition-colors group"
                  >
                    <td className="py-3 pl-4">
                      <div className="h-10 w-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 overflow-hidden flex items-center justify-center shrink-0">
                        {crop.image_url || crop.image ? (
                          /* eslint-disable-next-line @next/next/no-img-element */
                          <img
                            src={crop.image_url || crop.image}
                            alt={crop.crop_name}
                            className="h-full w-full object-cover"
                            onError={(e) => {
                              (e.target as HTMLElement).style.display = "none";
                            }}
                          />
                        ) : (
                          <Sprout className="h-4 w-4 text-emerald-400" />
                        )}
                      </div>
                    </td>
                    <td className="py-3 font-semibold text-white">
                      <div>{crop.crop_name}</div>
                      <div className="text-[11px] font-normal text-zinc-400 italic">
                        {crop.scientific_name || "—"}
                      </div>
                    </td>
                    <td className="py-3">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {crop.category || "Uncategorized"}
                      </span>
                    </td>
                    <td className="py-3 text-zinc-300">
                      {crop.growing_season || "—"}
                    </td>
                    <td className="py-3 text-zinc-400 font-mono">
                      {crop.crop_duration_days || "—"}
                    </td>
                    <td className="py-3 text-zinc-400">
                      {crop.water_requirement || "—"}
                    </td>
                    <td className="py-3 text-right pr-4 space-x-1.5 whitespace-nowrap">
                      {/* Automated image search button */}
                      <Link
                        href={`/agri-control-panel/images?crop=${encodeURIComponent(crop.crop_name)}`}
                        title="Automated Wikimedia Image Search"
                        className="inline-flex items-center gap-1 text-[11px] rounded-lg bg-emerald-500/10 hover:bg-emerald-500/25 border border-emerald-500/20 text-emerald-300 px-2 py-1 transition-colors"
                      >
                        <ImageIcon className="h-3 w-3" />
                        <span>Images</span>
                      </Link>

                      {/* Edit full details */}
                      <Link
                        href={`/agri-control-panel/crops/edit/${crop.id}`}
                        title="Edit Crop Record"
                        className="inline-flex items-center gap-1 text-[11px] rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-zinc-300 hover:text-white px-2 py-1 transition-colors"
                      >
                        <Edit className="h-3 w-3" />
                        <span>Edit</span>
                      </Link>

                      {/* View live public page */}
                      <Link
                        href={`/crops/${encodeURIComponent(crop.crop_name)}`}
                        target="_blank"
                        title="View Public Page"
                        className="inline-flex items-center gap-1 text-[11px] rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-zinc-400 hover:text-zinc-200 px-2 py-1 transition-colors"
                      >
                        <ExternalLink className="h-3 w-3" />
                      </Link>

                      {/* Delete */}
                      <button
                        onClick={() => setDeleteTarget(crop)}
                        title="Delete Crop"
                        className="inline-flex items-center text-[11px] rounded-lg bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-400 px-2 py-1 transition-colors"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ADD CROP MODAL */}
      <AnimatePresence>
        {isAddModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="glass-panel w-full max-w-2xl rounded-2xl p-6 border border-white/[0.1] shadow-2xl relative max-h-[90vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between pb-4 border-b border-white/[0.08]">
                <div className="flex items-center gap-2">
                  <div className="h-8 w-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                    <Sprout className="h-4 w-4" />
                  </div>
                  <h2 className="text-base font-bold text-white">Add New Crop Record</h2>
                </div>
                <button
                  onClick={() => setIsAddModalOpen(false)}
                  className="h-8 w-8 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-zinc-400 hover:text-white flex items-center justify-center"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              <form onSubmit={handleCreateCrop} className="mt-5 space-y-4 text-xs">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-zinc-300 font-medium mb-1">
                      Crop Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={formName}
                      onChange={(e) => setFormName(e.target.value)}
                      placeholder="e.g. Mustard (Shorisha)"
                      className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white placeholder-zinc-500 focus:border-emerald-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-zinc-300 font-medium mb-1">
                      Scientific Name
                    </label>
                    <input
                      type="text"
                      value={formScientific}
                      onChange={(e) => setFormScientific(e.target.value)}
                      placeholder="e.g. Brassica juncea"
                      className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white placeholder-zinc-500 focus:border-emerald-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-zinc-300 font-medium mb-1">
                      Category
                    </label>
                    <select
                      value={formCategory}
                      onChange={(e) => setFormCategory(e.target.value)}
                      className="w-full rounded-xl bg-[#0a100c] border border-white/[0.1] px-3 py-2 text-white focus:border-emerald-500 focus:outline-none"
                    >
                      {CATEGORIES.filter((c) => c !== "All").map((cat) => (
                        <option key={cat} value={cat}>
                          {cat}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-zinc-300 font-medium mb-1">
                      Growing Season
                    </label>
                    <input
                      type="text"
                      value={formSeason}
                      onChange={(e) => setFormSeason(e.target.value)}
                      placeholder="e.g. Rabi season (Winter)"
                      className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white placeholder-zinc-500 focus:border-emerald-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-zinc-300 font-medium mb-1">
                      Planting Time
                    </label>
                    <input
                      type="text"
                      value={formPlanting}
                      onChange={(e) => setFormPlanting(e.target.value)}
                      placeholder="e.g. Mid-October to Mid-November"
                      className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white placeholder-zinc-500 focus:border-emerald-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-zinc-300 font-medium mb-1">
                      Harvest Time
                    </label>
                    <input
                      type="text"
                      value={formHarvest}
                      onChange={(e) => setFormHarvest(e.target.value)}
                      placeholder="e.g. January to February"
                      className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white placeholder-zinc-500 focus:border-emerald-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-zinc-300 font-medium mb-1">
                      Duration (Days)
                    </label>
                    <input
                      type="text"
                      value={formDuration}
                      onChange={(e) => setFormDuration(e.target.value)}
                      placeholder="e.g. 80-110 days"
                      className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white placeholder-zinc-500 focus:border-emerald-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-zinc-300 font-medium mb-1">
                      Water Requirement
                    </label>
                    <input
                      type="text"
                      value={formWater}
                      onChange={(e) => setFormWater(e.target.value)}
                      placeholder="e.g. Low to moderate irrigation"
                      className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white placeholder-zinc-500 focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-zinc-300 font-medium mb-1">
                    Soil Requirement
                  </label>
                  <input
                    type="text"
                    value={formSoil}
                    onChange={(e) => setFormSoil(e.target.value)}
                    placeholder="e.g. Well-drained sandy loam to clay loam"
                    className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white placeholder-zinc-500 focus:border-emerald-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-zinc-300 font-medium mb-1">
                    Fertilizer Regimen
                  </label>
                  <input
                    type="text"
                    value={formFertilizer}
                    onChange={(e) => setFormFertilizer(e.target.value)}
                    placeholder="e.g. Urea, TSP, MoP, Gypsum, Zinc sulphate"
                    className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white placeholder-zinc-500 focus:border-emerald-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-zinc-300 font-medium mb-1">
                    Cultivation Regions (comma separated)
                  </label>
                  <input
                    type="text"
                    value={formRegions}
                    onChange={(e) => setFormRegions(e.target.value)}
                    placeholder="e.g. Rajshahi, Rangpur, Dinajpur, Jashore"
                    className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white placeholder-zinc-500 focus:border-emerald-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-zinc-300 font-medium mb-1">
                    Common Diseases (comma separated)
                  </label>
                  <input
                    type="text"
                    value={formDiseases}
                    onChange={(e) => setFormDiseases(e.target.value)}
                    placeholder="e.g. Alternaria Blight, Downy Mildew, White Rust"
                    className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white placeholder-zinc-500 focus:border-emerald-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-zinc-300 font-medium mb-1">
                    Growth Stages (comma separated in sequence)
                  </label>
                  <input
                    type="text"
                    value={formStages}
                    onChange={(e) => setFormStages(e.target.value)}
                    placeholder="e.g. Germination, Vegetative, Flowering, Siliqua formation, Maturity"
                    className="w-full rounded-xl bg-black/40 border border-white/[0.1] px-3 py-2 text-white placeholder-zinc-500 focus:border-emerald-500 focus:outline-none"
                  />
                </div>

                <div className="pt-4 border-t border-white/[0.08] flex items-center justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setIsAddModalOpen(false)}
                    className="px-4 py-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] text-zinc-300 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSaving}
                    className="flex items-center gap-2 px-5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-semibold transition-all disabled:opacity-50"
                  >
                    {isSaving ? (
                      <>
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                        <span>Saving Crop...</span>
                      </>
                    ) : (
                      <>
                        <Check className="h-3.5 w-3.5" />
                        <span>Create Crop Record</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* DELETE CONFIRMATION MODAL */}
      <AnimatePresence>
        {deleteTarget && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="glass-panel w-full max-w-md rounded-2xl p-6 border border-red-500/20 shadow-2xl"
            >
              <div className="flex items-center gap-3 text-red-400 mb-3">
                <AlertTriangle className="h-6 w-6" />
                <h3 className="text-base font-bold text-white">Delete Crop Record?</h3>
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Are you sure you want to delete <strong className="text-white">{deleteTarget.crop_name}</strong>?
                This will permanently remove the crop, its growth stages, diseases, and regional mappings.
              </p>

              <div className="mt-6 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setDeleteTarget(null)}
                  disabled={isDeleting}
                  className="px-4 py-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] text-xs text-zinc-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleDeleteConfirm}
                  disabled={isDeleting}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-500 hover:bg-red-400 text-black text-xs font-semibold transition-all disabled:opacity-50"
                >
                  {isDeleting ? (
                    <>
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      <span>Deleting...</span>
                    </>
                  ) : (
                    <>
                      <Trash2 className="h-3.5 w-3.5" />
                      <span>Delete Record</span>
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

