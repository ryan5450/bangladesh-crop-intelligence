import axios from "axios";
import {
  AdminStats,
  CropCreateInput,
  CropDetail,
  CropSummary,
  CropUpdateInput,
  FilterState,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Fetch crops with multi-faceted filtering.
 */
export async function getFilteredCrops(filters: FilterState = {}): Promise<CropSummary[]> {
  try {
    const params: Record<string, any> = {};
    if (filters.query?.trim()) params.query = filters.query.trim();
    if (filters.category && filters.category !== "All") params.category = filters.category;
    if (filters.season && filters.season !== "All") params.season = filters.season;
    if (filters.region && filters.region !== "All") params.region = filters.region;
    if (filters.waterRequirement && filters.waterRequirement !== "All") {
      params.water_requirement = filters.waterRequirement;
    }
    if (filters.minDuration !== undefined) params.min_duration = filters.minDuration;
    if (filters.maxDuration !== undefined) params.max_duration = filters.maxDuration;

    const response = await apiClient.get<CropSummary[]>("/crops", { params });
    return response.data;
  } catch (error) {
    console.error("Failed to fetch filtered crops:", error);
    throw error;
  }
}

/**
 * Fetch all crops as summary items.
 */
export async function getAllCrops(): Promise<CropSummary[]> {
  return getFilteredCrops({});
}

/**
 * Fetch detailed information for a single crop by name.
 */
export async function getCropByName(cropName: string): Promise<CropDetail> {
  try {
    const response = await apiClient.get<CropDetail>(`/crops/${encodeURIComponent(cropName)}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch crop details for '${cropName}':`, error);
    throw error;
  }
}

/**
 * Search crops by substring query.
 */
export async function searchCrops(query: string): Promise<CropSummary[]> {
  return getFilteredCrops({ query });
}

/**
 * Fetch crops filtered by category name.
 */
export async function getCropsByCategory(category: string): Promise<CropSummary[]> {
  return getFilteredCrops({ category });
}

/**
 * Ping backend health endpoint.
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await apiClient.get("/", { timeout: 3000 });
    return response.status === 200;
  } catch {
    return false;
  }
}

/**
 * Get admin analytics stats.
 */
export async function getAdminStats(): Promise<AdminStats> {
  try {
    const response = await apiClient.get<AdminStats>("/admin/stats");
    return response.data;
  } catch (error) {
    console.error("Failed to fetch admin stats:", error);
    throw error;
  }
}

/**
 * Create a new crop.
 */
export async function createCrop(data: CropCreateInput): Promise<CropDetail> {
  try {
    const response = await apiClient.post<CropDetail>("/crops", data);
    return response.data;
  } catch (error) {
    console.error("Failed to create crop:", error);
    throw error;
  }
}

/**
 * Update an existing crop.
 */
export async function updateCrop(id: number, data: CropUpdateInput): Promise<CropDetail> {
  try {
    const response = await apiClient.put<CropDetail>(`/crops/${id}`, data);
    return response.data;
  } catch (error) {
    console.error(`Failed to update crop ${id}:`, error);
    throw error;
  }
}

/**
 * Delete a crop.
 */
export async function deleteCrop(id: number): Promise<{ success: boolean; message: string }> {
  try {
    const response = await apiClient.delete<{ success: boolean; message: string }>(`/crops/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to delete crop ${id}:`, error);
    throw error;
  }
}

/**
 * Upload an image file to Supabase Storage via FastAPI backend.
 */
export async function uploadCropImage(
  file: File,
  cropId?: number,
  caption?: string,
  isPrimary: boolean = false
): Promise<{ success: boolean; url: string; path: string; filename: string }> {
  try {
    const formData = new FormData();
    formData.append("file", file);
    if (cropId) formData.append("crop_id", cropId.toString());
    if (caption) formData.append("caption", caption);
    formData.append("is_primary", isPrimary ? "true" : "false");

    const response = await apiClient.post("/upload-image", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  } catch (error) {
    console.error("Failed to upload crop image:", error);
    throw error;
  }
}

export interface SourceCitation {
  source: string;
  category: string;
  page_number: number;
  language: string;
  document_id: string;
  chunk_id: string;
  relevance_score: number;
  citation_text: string;
}

export interface AssistantChatResponse {
  answer: string;
  sources: SourceCitation[];
  detected_language: string;
  model: string;
  image_url?: string | null;
  crop_name?: string | null;
}

export interface AssistantHealthResponse {
  status: string;
  llm_service: {
    connected: boolean;
    engine: string;
    model: string;
    endpoint: string;
  };
  vector_store: {
    connected: boolean;
    engine: string;
    collection: string;
    total_vectors: number;
    persistence_path: string;
  };
}

/**
 * Send a message to the AI Crop Intelligence Assistant.
 */
export async function chatWithAssistant(
  message: string,
  category?: string,
  conversationHistory?: { role: string; content: string }[]
): Promise<AssistantChatResponse> {
  try {
    const response = await apiClient.post<AssistantChatResponse>(
      "/api/assistant/chat",
      {
        message,
        category: category || null,
        top_k: 4,
        conversation_history: conversationHistory || [],
      },
      { timeout: 60000 }
    );
    return response.data;
  } catch (error) {
    console.error("Assistant chat error:", error);
    throw error;
  }
}

/**
 * Check AI Assistant (LLM + ChromaDB) service health.
 */
export async function getAssistantHealth(): Promise<AssistantHealthResponse> {
  try {
    const response = await apiClient.get<AssistantHealthResponse>(
      "/api/assistant/health",
      { timeout: 5000 }
    );
    return response.data;
  } catch (error) {
    console.error("Assistant health check error:", error);
    throw error;
  }
}

/**
 * Stream a message to the AI Crop Intelligence Assistant with real-time SSE chunks.
 */
export async function streamChatWithAssistant(
  message: string,
  category?: string,
  conversationHistory?: { role: string; content: string }[],
  callbacks?: {
    onMetadata?: (meta: {
      sources: SourceCitation[];
      detected_language: string;
      model: string;
      image_url?: string | null;
      crop_name?: string | null;
    }) => void;
    onDelta?: (delta: string) => void;
    onDone?: () => void;
    onError?: (err: Error) => void;
  }
): Promise<void> {
  const url = `${API_BASE_URL}/api/assistant/chat/stream`;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        category: category || null,
        top_k: 3,
        conversation_history: conversationHistory || [],
      }),
    });

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}: ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error("No response body available for streaming");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith("data:")) continue;
        const jsonStr = trimmed.replace(/^data:\s*/, "");
        if (jsonStr === "[DONE]") {
          callbacks?.onDone?.();
          return;
        }
        try {
          const payload = JSON.parse(jsonStr);
          if (payload.type === "metadata") {
            callbacks?.onMetadata?.(payload);
          } else if (payload.type === "delta") {
            callbacks?.onDelta?.(payload.content || "");
          } else if (payload.type === "done") {
            callbacks?.onDone?.();
            return;
          } else if (payload.type === "error") {
            throw new Error(payload.message || "Streaming error from server");
          }
        } catch (parseErr: any) {
          if (parseErr.message?.includes("Streaming error")) throw parseErr;
        }
      }
    }
    callbacks?.onDone?.();
  } catch (error: any) {
    callbacks?.onError?.(error);
    throw error;
  }
}


