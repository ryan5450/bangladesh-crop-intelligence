export interface CropImage {
  id?: number;
  image_url: string;
  caption?: string | null;
  is_primary?: boolean;
}

export interface CropSummary {
  id: number;
  crop_name: string;
  scientific_name?: string | null;
  category: string | null;
  growing_season?: string | null;
  water_requirement?: string | null;
  crop_duration_days?: string | null;
  image?: string | null;
  image_url?: string | null;
  gallery_urls?: any[];
}

export interface GrowthStage {
  stage_number: number;
  stage_name: string;
}

export interface CropDetail {
  id: number;
  crop_name: string;
  scientific_name?: string | null;
  category?: string | null;
  growing_season?: string | null;
  planting_time?: string | null;
  harvest_time?: string | null;
  soil_requirement?: string | null;
  water_requirement?: string | null;
  fertilizer?: string | null;
  image?: string | null;
  image_url?: string | null;
  crop_duration_days?: string | null;
  growth_stages: GrowthStage[];
  diseases: string[];
  regions: string[];
  gallery_images?: CropImage[];
  gallery_urls?: any[];
}

export interface FilterState {
  query?: string;
  category?: string;
  season?: string;
  region?: string;
  waterRequirement?: string;
  minDuration?: number;
  maxDuration?: number;
}

export interface AdminStats {
  total_crops: number;
  categories_count: number;
  categories: string[];
  total_images: number;
  total_diseases: number;
  total_growth_stages: number;
  status: string;
}

export interface CropCreateInput {
  crop_name: string;
  scientific_name?: string;
  category?: string;
  growing_season?: string;
  planting_time?: string;
  harvest_time?: string;
  soil_requirement?: string;
  water_requirement?: string;
  fertilizer?: string;
  image?: string;
  crop_duration_days?: string;
  growth_stages?: { stage_number: number; stage_name: string }[];
  diseases?: string[];
  regions?: string[];
  gallery_images?: CropImage[];
}

export interface CropUpdateInput extends Partial<CropCreateInput> {}
