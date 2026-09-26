"""API routes for crop intelligence, advanced discovery, and admin management.

Provides public crop search/filtering and administrative endpoints for crop CRUD,
automated Wikimedia Commons image search, and Supabase Storage synchronization.
"""

import datetime
import logging
import os
import re
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, ConfigDict
import httpx
from postgrest.exceptions import APIError

from auth import get_current_admin
from supabase_client import SUPABASE_URL, supabase

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Crops & Admin Management"])


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class CropSummary(BaseModel):
    """Summary representation of a crop with rich metadata for filtering."""
    id: int
    crop_name: str
    scientific_name: Optional[str] = None
    category: Optional[str] = None
    growing_season: Optional[str] = None
    water_requirement: Optional[str] = None
    crop_duration_days: Optional[str] = None
    image: Optional[str] = None
    image_url: Optional[str] = None
    gallery_urls: Optional[List[Any]] = None

    model_config = ConfigDict(from_attributes=True)


class GrowthStageIn(BaseModel):
    stage_number: int
    stage_name: str


class GrowthStageOut(BaseModel):
    stage_number: int
    stage_name: str

    model_config = ConfigDict(from_attributes=True)


class CropImageOut(BaseModel):
    id: Optional[int] = None
    image_url: str
    caption: Optional[str] = None
    is_primary: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class CropDetail(BaseModel):
    """Detailed crop representation combined with relational child data."""
    id: int
    crop_name: str
    scientific_name: Optional[str] = None
    category: Optional[str] = None
    growing_season: Optional[str] = None
    planting_time: Optional[str] = None
    harvest_time: Optional[str] = None
    soil_requirement: Optional[str] = None
    water_requirement: Optional[str] = None
    fertilizer: Optional[str] = None
    image: Optional[str] = None
    image_url: Optional[str] = None
    crop_duration_days: Optional[str] = None
    growth_stages: List[GrowthStageOut] = []
    diseases: List[str] = []
    regions: List[str] = []
    gallery_images: List[CropImageOut] = []
    gallery_urls: Optional[List[Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CropCreateInput(BaseModel):
    crop_name: str
    scientific_name: Optional[str] = None
    category: Optional[str] = None
    growing_season: Optional[str] = None
    planting_time: Optional[str] = None
    harvest_time: Optional[str] = None
    soil_requirement: Optional[str] = None
    water_requirement: Optional[str] = None
    fertilizer: Optional[str] = None
    image: Optional[str] = None
    image_url: Optional[str] = None
    crop_duration_days: Optional[str] = None
    growth_stages: Optional[List[GrowthStageIn]] = []
    diseases: Optional[List[str]] = []
    regions: Optional[List[str]] = []
    gallery_images: Optional[List[CropImageOut]] = []
    gallery_urls: Optional[List[Any]] = []


class CropUpdateInput(BaseModel):
    crop_name: Optional[str] = None
    scientific_name: Optional[str] = None
    category: Optional[str] = None
    growing_season: Optional[str] = None
    planting_time: Optional[str] = None
    harvest_time: Optional[str] = None
    soil_requirement: Optional[str] = None
    water_requirement: Optional[str] = None
    fertilizer: Optional[str] = None
    image: Optional[str] = None
    image_url: Optional[str] = None
    crop_duration_days: Optional[str] = None
    growth_stages: Optional[List[GrowthStageIn]] = None
    diseases: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    gallery_images: Optional[List[CropImageOut]] = None
    gallery_urls: Optional[List[Any]] = None


# ---------------------------------------------------------------------------
# Database Helper
# ---------------------------------------------------------------------------

def execute_query(query: Any) -> Any:
    """Execute a PostgREST query and handle errors gracefully."""
    try:
        response = query.execute()
        return response.data
    except APIError as exc:
        logger.error(f"Database API error: {exc.message} (Code: {exc.code})")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {exc.message}",
        )
    except Exception as exc:
        logger.exception("Unexpected error during database operation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred: {exc}",
        )


def parse_numeric_duration(duration_str: Optional[str]) -> Optional[int]:
    """Extract an approximate duration in days from text string."""
    if not duration_str:
        return None
    numbers = [int(n) for n in re.findall(r"\d+", duration_str)]
    if not numbers:
        return None
    return sum(numbers) // len(numbers)


# ---------------------------------------------------------------------------
# Endpoints: Public Discovery & Filtering
# ---------------------------------------------------------------------------

@router.get("/crops", response_model=List[CropSummary], summary="Get crops with multi-facet filtering")
def get_all_crops(
    query: Optional[str] = Query(None, description="Search crop name, scientific name, season, category, disease, or region"),
    category: Optional[str] = Query(None, description="Filter by category"),
    season: Optional[str] = Query(None, description="Filter by growing season"),
    region: Optional[str] = Query(None, description="Filter by Bangladesh region/district"),
    water_requirement: Optional[str] = Query(None, description="Filter by water requirement"),
    min_duration: Optional[int] = Query(None, description="Minimum duration in days"),
    max_duration: Optional[int] = Query(None, description="Maximum duration in days"),
):
    """Return crops matching multi-faceted filters or return all crops."""
    db_query = supabase.table("crops").select("*")

    if category and category.strip() and category.strip().lower() != "all":
        db_query = db_query.ilike("category", f"%{category.strip()}%")

    if season and season.strip() and season.strip().lower() != "all":
        db_query = db_query.ilike("growing_season", f"%{season.strip()}%")

    if water_requirement and water_requirement.strip() and water_requirement.strip().lower() != "all":
        db_query = db_query.ilike("water_requirement", f"%{water_requirement.strip()}%")

    crops = execute_query(db_query.order("crop_name")) or []

    # Filter by region if requested
    if region and region.strip() and region.strip().lower() != "all":
        reg_res = execute_query(
            supabase.table("regions").select("crop_id").ilike("region_name", f"%{region.strip()}%")
        )
        crop_ids_in_region = {r["crop_id"] for r in (reg_res or [])}
        crops = [c for c in crops if c["id"] in crop_ids_in_region]

    # Global text search across multiple dimensions
    if query and query.strip():
        q = query.strip().lower()
        matched_crop_ids = set()

        for c in crops:
            if (
                q in (c.get("crop_name") or "").lower()
                or q in (c.get("scientific_name") or "").lower()
                or q in (c.get("category") or "").lower()
                or q in (c.get("growing_season") or "").lower()
                or q in (c.get("soil_requirement") or "").lower()
            ):
                matched_crop_ids.add(c["id"])

        try:
            dis_res = execute_query(supabase.table("diseases").select("crop_id").ilike("disease_name", f"%{q}%"))
            for d in (dis_res or []):
                matched_crop_ids.add(d["crop_id"])
        except Exception:
            pass

        try:
            reg_search = execute_query(supabase.table("regions").select("crop_id").ilike("region_name", f"%{q}%"))
            for r in (reg_search or []):
                matched_crop_ids.add(r["crop_id"])
        except Exception:
            pass

        crops = [c for c in crops if c["id"] in matched_crop_ids]

    # Filter by duration range
    if min_duration is not None or max_duration is not None:
        filtered = []
        for crop in crops:
            duration_days = parse_numeric_duration(crop.get("crop_duration_days"))
            if duration_days is None:
                filtered.append(crop)
                continue
            if min_duration is not None and duration_days < min_duration:
                continue
            if max_duration is not None and duration_days > max_duration:
                continue
            filtered.append(crop)
        crops = filtered

    # Normalize image_url to fallback to image if needed
    for crop in crops:
        if not crop.get("image_url") and crop.get("image"):
            crop["image_url"] = crop.get("image")

    return crops


@router.get("/crops/{crop_name}", response_model=CropDetail, summary="Get complete crop details")
def get_crop_by_name(crop_name: str):
    """Return complete crop details combined with growth stages, diseases, regions, and gallery images."""
    clean_name = crop_name.strip()
    if not clean_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Crop name must not be empty.",
        )

    # 1. Fetch main crop record
    crop_query = supabase.table("crops").select("*").ilike("crop_name", clean_name).limit(1)
    crop_rows = execute_query(crop_query)

    if not crop_rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop '{crop_name}' not found.",
        )

    crop = crop_rows[0]
    crop_id = crop["id"]

    # 2. Fetch ordered growth stages
    stages_rows = execute_query(
        supabase.table("growth_stages").select("stage_number, stage_name").eq("crop_id", crop_id).order("stage_number")
    ) or []
    growth_stages = [
        {"stage_number": s["stage_number"], "stage_name": s["stage_name"]}
        for s in stages_rows
    ]

    # 3. Fetch diseases list
    diseases_rows = execute_query(
        supabase.table("diseases").select("disease_name").eq("crop_id", crop_id)
    ) or []
    diseases = [d["disease_name"] for d in diseases_rows if d.get("disease_name")]

    # 4. Fetch regions list
    regions_rows = execute_query(
        supabase.table("regions").select("region_name").eq("crop_id", crop_id)
    ) or []
    regions = [r["region_name"] for r in regions_rows if r.get("region_name")]

    # 5. Fetch gallery images
    gallery_images: List[Dict[str, Any]] = []
    
    # 5a. From crop_images table if exists
    try:
        img_res = (
            supabase.table("crop_images")
            .select("id, image_url, caption, is_primary")
            .eq("crop_id", crop_id)
            .order("id")
            .execute()
        )
        if img_res.data:
            gallery_images.extend(img_res.data)
    except Exception:
        pass

    # 5b. From gallery_urls JSONB column if exists
    raw_gallery_urls = crop.get("gallery_urls") or []
    if isinstance(raw_gallery_urls, list):
        for idx, item in enumerate(raw_gallery_urls):
            if isinstance(item, str) and item:
                gallery_images.append({
                    "id": 1000 + idx,
                    "image_url": item,
                    "caption": f"Gallery photo {idx+1}",
                    "is_primary": False,
                })
            elif isinstance(item, dict) and item.get("url"):
                gallery_images.append({
                    "id": 1000 + idx,
                    "image_url": item.get("url"),
                    "caption": item.get("caption") or f"Gallery photo {idx+1}",
                    "is_primary": False,
                })

    # Ensure main image is in gallery if empty
    main_img = crop.get("image_url") or crop.get("image")
    if not gallery_images and main_img:
        gallery_images.append({
            "id": 0,
            "image_url": main_img,
            "caption": "Main View",
            "is_primary": True,
        })

    # Ensure image_url is populated
    if not crop.get("image_url") and crop.get("image"):
        crop["image_url"] = crop.get("image")

    return {
        "id": crop["id"],
        "crop_name": crop["crop_name"],
        "scientific_name": crop.get("scientific_name"),
        "category": crop.get("category"),
        "growing_season": crop.get("growing_season"),
        "planting_time": crop.get("planting_time"),
        "harvest_time": crop.get("harvest_time"),
        "soil_requirement": crop.get("soil_requirement"),
        "water_requirement": crop.get("water_requirement"),
        "fertilizer": crop.get("fertilizer"),
        "image": crop.get("image"),
        "image_url": crop.get("image_url"),
        "crop_duration_days": crop.get("crop_duration_days"),
        "growth_stages": growth_stages,
        "diseases": diseases,
        "regions": regions,
        "gallery_images": gallery_images,
        "gallery_urls": raw_gallery_urls,
    }


@router.get("/search", response_model=List[CropSummary], summary="Search crops by crop_name")
def search_crops(query: str = Query(..., min_length=1, description="Crop name substring to search for")):
    """Search crops table by crop_name using case-insensitive partial match."""
    clean_query = query.strip()
    if not clean_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query parameter cannot be empty.",
        )

    db_query = (
        supabase.table("crops")
        .select("id, crop_name, scientific_name, category, growing_season, water_requirement, crop_duration_days, image, image_url")
        .ilike("crop_name", f"%{clean_query}%")
        .order("crop_name")
    )
    crops = execute_query(db_query) or []
    for c in crops:
        if not c.get("image_url") and c.get("image"):
            c["image_url"] = c.get("image")
    return crops


@router.get("/categories/{category}", response_model=List[CropSummary], summary="Get crops by category")
def get_crops_by_category(category: str):
    """Return crops belonging to the specified category."""
    clean_cat = category.strip()
    if not clean_cat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category cannot be empty.",
        )

    db_query = (
        supabase.table("crops")
        .select("id, crop_name, scientific_name, category, growing_season, water_requirement, crop_duration_days, image, image_url")
        .ilike("category", clean_cat)
        .order("crop_name")
    )
    crops = execute_query(db_query) or []
    for c in crops:
        if not c.get("image_url") and c.get("image"):
            c["image_url"] = c.get("image")
    return crops


# ---------------------------------------------------------------------------
# Endpoints: Automated Wikimedia Commons Search
# ---------------------------------------------------------------------------

@router.get("/admin/search-images", summary="Automated Wikimedia Commons image search")
async def search_wikimedia_images(
    query: str = Query(..., min_length=1, description="Crop name or keyword to search on Wikimedia"),
    limit: int = Query(12, ge=1, le=40, description="Max candidate images to return"),
):
    """Query Wikimedia Commons API for authentic high-resolution crop photos."""
    clean_query = query.strip()
    search_term = clean_query

    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_term,
        "gsrnamespace": "6",  # Namespace 6 corresponds to File:
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "500",
        "format": "json",
        "origin": "*",
    }

    headers = {
        "User-Agent": "BangladeshCropIntelligence/2.0 (precision-agri@bangladesh-agritech.org; automated discovery bot)",
    }

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.get("https://commons.wikimedia.org/w/api.php", params=params, headers=headers)
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Wikimedia Commons API returned status code {resp.status_code}",
                )
            data = resp.json()

        pages = data.get("query", {}).get("pages", {})
        results = []

        valid_extensions = (".jpg", ".jpeg", ".png", ".webp")

        for page_id, page in pages.items():
            title = page.get("title", "").replace("File:", "").strip()
            image_info_list = page.get("imageinfo", [])
            if not image_info_list:
                continue

            info = image_info_list[0]
            original_url = info.get("url", "")
            thumb_url = info.get("thumburl", original_url)
            mime = info.get("mime", "")
            width = info.get("width", 0)
            height = info.get("height", 0)
            desc_url = info.get("descriptionurl", "")

            # Strip query string before verifying image extension
            url_clean = original_url.split("?")[0].lower()
            if not any(url_clean.endswith(ext) for ext in valid_extensions):
                continue
            if "svg" in mime.lower():
                continue

            # Extract license/artist metadata if available
            metadata = info.get("extmetadata", {})
            artist = metadata.get("Artist", {}).get("value", "")
            license_name = metadata.get("LicenseShortName", {}).get("value", "Wikimedia Commons")

            # Clean HTML out of artist string
            clean_artist = re.sub(r"<[^>]+>", "", artist).strip()[:100]

            results.append({
                "page_id": page_id,
                "title": title.replace("_", " "),
                "thumbnail_url": thumb_url,
                "original_url": original_url,
                "width": width,
                "height": height,
                "mime": mime,
                "description_url": desc_url,
                "artist": clean_artist or "Unknown",
                "license": license_name,
            })

        return {
            "query": clean_query,
            "count": len(results),
            "images": results,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error searching Wikimedia Commons: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query Wikimedia Commons API: {exc}",
        )


# ---------------------------------------------------------------------------
# Endpoints: Image Upload & Storage Sync (Direct or Wikimedia Stream)
# ---------------------------------------------------------------------------

@router.post("/admin/upload-image", summary="Upload image to Supabase Storage and link to crop")
@router.post("/upload-image", summary="Legacy image upload endpoint")
async def upload_image(
    file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
    crop_id: Optional[int] = Form(None),
    image_type: str = Form("main"),  # "main" or "gallery"
    caption: Optional[str] = Form(""),
    is_primary: Optional[bool] = Form(None),
):
    """Download image from Wikimedia URL or accept direct file upload, store in Supabase Storage, and link to crop."""
    try:
        contents: bytes = b""
        filename: str = "crop_image.jpg"
        content_type: str = "image/jpeg"

        # Case 1: Automated Download from URL (e.g. Wikimedia Commons)
        if image_url and image_url.strip():
            target_url = image_url.strip()
            headers = {
                "User-Agent": "BangladeshCropIntelligence/2.0 (precision-agri@bangladesh-agritech.org; automated downloader)"
            }
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                dl_resp = await client.get(target_url, headers=headers)
                if dl_resp.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to download image from source URL (Status {dl_resp.status_code})",
                    )
                contents = dl_resp.content

            # Derive clean filename from URL
            url_path = target_url.split("?")[0]
            raw_name = url_path.split("/")[-1]
            filename = raw_name if raw_name else "wikimedia_image.jpg"
            content_type = dl_resp.headers.get("content-type", "image/jpeg").split(";")[0]

        # Case 2: Direct File Upload
        elif file is not None:
            contents = await file.read()
            if len(contents) == 0:
                raise HTTPException(status_code=400, detail="Uploaded file is empty.")
            filename = file.filename or "uploaded_image.jpg"
            content_type = file.content_type or "image/jpeg"

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either 'file' or 'image_url' must be provided for upload.",
            )

        # Normalize is_primary flag
        is_primary_flag = is_primary if is_primary is not None else (image_type == "main")

        # Sanitize filename and create storage path
        sanitized_filename = re.sub(r"[^\w\.-]", "_", filename)
        random_prefix = uuid.uuid4().hex[:8]
        folder = f"crop_{crop_id}" if crop_id else "general"
        storage_path = f"{folder}/{random_prefix}_{sanitized_filename}"

        # Upload to Supabase Storage bucket 'crops'
        bucket = supabase.storage.from_("crops")
        bucket.upload(
            path=storage_path,
            file=contents,
            file_options={"content-type": content_type, "upsert": "true"},
        )

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/crops/{storage_path}"

        # If crop_id is provided, associate in database
        if crop_id:
            if is_primary_flag:
                # Update main image in both image_url and legacy image columns
                update_payload = {"image": public_url}
                try:
                    execute_query(supabase.table("crops").update({"image_url": public_url, "image": public_url}).eq("id", crop_id))
                except Exception:
                    execute_query(supabase.table("crops").update(update_payload).eq("id", crop_id))
            else:
                # Append to gallery_urls JSONB array
                try:
                    current_crop = execute_query(supabase.table("crops").select("gallery_urls").eq("id", crop_id).limit(1))
                    if current_crop:
                        curr_gallery = current_crop[0].get("gallery_urls") or []
                        if not isinstance(curr_gallery, list):
                            curr_gallery = []
                        curr_gallery.append({
                            "url": public_url,
                            "caption": caption or sanitized_filename,
                            "uploaded_at": datetime.datetime.utcnow().isoformat(),
                        })
                        execute_query(supabase.table("crops").update({"gallery_urls": curr_gallery}).eq("id", crop_id))
                except Exception as exc:
                    logger.warning(f"Could not update gallery_urls JSONB on crop {crop_id}: {exc}")

            # Also sync into crop_images table if it exists
            try:
                execute_query(
                    supabase.table("crop_images").insert({
                        "crop_id": crop_id,
                        "image_url": public_url,
                        "caption": caption or sanitized_filename,
                        "is_primary": is_primary_flag,
                    })
                )
            except Exception:
                pass

        return {
            "success": True,
            "url": public_url,
            "image_url": public_url,
            "path": storage_path,
            "filename": filename,
            "image_type": image_type,
            "crop_id": crop_id,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to upload image: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage upload error: {exc}. Please verify the 'crops' storage bucket exists in Supabase.",
        )


# ---------------------------------------------------------------------------
# Endpoints: Admin Statistics Dashboard
# ---------------------------------------------------------------------------

@router.get("/admin/stats", summary="Get admin dashboard KPIs and summary metrics")
def get_admin_stats():
    """Return aggregated KPI metrics for crops, categories, images, and recent updates."""
    all_crops = execute_query(supabase.table("crops").select("id, crop_name, scientific_name, category, image, image_url").order("id", desc=True)) or []

    total_crops = len(all_crops)
    categories = {c.get("category") for c in all_crops if c.get("category")}
    categories_count = len(categories)

    images_count = sum(1 for c in all_crops if (c.get("image_url") or c.get("image")))

    # Recent updates (first 6 crops)
    recent_crops = all_crops[:6]
    for c in recent_crops:
        if not c.get("image_url") and c.get("image"):
            c["image_url"] = c.get("image")

    return {
        "total_crops": total_crops,
        "categories_count": categories_count,
        "images_count": images_count,
        "categories": sorted(list(categories)),
        "recent_updates": recent_crops,
    }


# ---------------------------------------------------------------------------
# Endpoints: Admin Crop CRUD Management
# ---------------------------------------------------------------------------

@router.post("/admin/crops", response_model=CropDetail, status_code=status.HTTP_201_CREATED, summary="Create a new crop record (Admin)")
@router.post("/crops", response_model=CropDetail, status_code=status.HTTP_201_CREATED, summary="Create a new crop record")
def create_crop(crop_in: CropCreateInput):
    """Create a new crop record and its relational children."""
    crop_name = crop_in.crop_name.strip()
    if not crop_name:
        raise HTTPException(status_code=400, detail="Crop name is required.")

    # Check for duplicate
    existing = execute_query(supabase.table("crops").select("id").ilike("crop_name", crop_name).limit(1))
    if existing:
        raise HTTPException(status_code=409, detail=f"A crop named '{crop_name}' already exists.")

    # Determine image URL
    primary_img = crop_in.image_url or crop_in.image

    crop_payload = {
        "crop_name": crop_name,
        "scientific_name": crop_in.scientific_name,
        "category": crop_in.category,
        "growing_season": crop_in.growing_season,
        "planting_time": crop_in.planting_time,
        "harvest_time": crop_in.harvest_time,
        "soil_requirement": crop_in.soil_requirement,
        "water_requirement": crop_in.water_requirement,
        "fertilizer": crop_in.fertilizer,
        "image": primary_img,
        "crop_duration_days": crop_in.crop_duration_days,
    }

    # Attempt to add image_url and gallery_urls if migrated
    if crop_in.image_url:
        crop_payload["image_url"] = crop_in.image_url
    if crop_in.gallery_urls:
        crop_payload["gallery_urls"] = crop_in.gallery_urls

    try:
        res = execute_query(supabase.table("crops").insert(crop_payload))
    except Exception:
        # Fallback if image_url or gallery_urls column not yet migrated in Supabase
        crop_payload.pop("image_url", None)
        crop_payload.pop("gallery_urls", None)
        res = execute_query(supabase.table("crops").insert(crop_payload))

    if not res:
        raise HTTPException(status_code=500, detail="Failed to insert crop record.")

    new_crop_id = res[0]["id"]

    # Insert growth stages
    if crop_in.growth_stages:
        stages_payload = [
            {"crop_id": new_crop_id, "stage_number": s.stage_number, "stage_name": s.stage_name}
            for s in crop_in.growth_stages
        ]
        execute_query(supabase.table("growth_stages").insert(stages_payload))

    # Insert diseases
    if crop_in.diseases:
        diseases_payload = [
            {"crop_id": new_crop_id, "disease_name": d.strip()}
            for d in crop_in.diseases if d.strip()
        ]
        if diseases_payload:
            execute_query(supabase.table("diseases").insert(diseases_payload))

    # Insert regions
    if crop_in.regions:
        regions_payload = [
            {"crop_id": new_crop_id, "region_name": r.strip()}
            for r in crop_in.regions if r.strip()
        ]
        if regions_payload:
            execute_query(supabase.table("regions").insert(regions_payload))

    return get_crop_by_name(crop_name)


@router.put("/admin/crops/{crop_id}", response_model=CropDetail, summary="Update crop details (Admin)")
@router.put("/crops/{crop_id}", response_model=CropDetail, summary="Update crop details")
def update_crop(crop_id: int, crop_in: CropUpdateInput):
    """Update fields on an existing crop and synchronize relational child records."""
    existing = execute_query(supabase.table("crops").select("id, crop_name").eq("id", crop_id).limit(1))
    if not existing:
        raise HTTPException(status_code=404, detail=f"Crop with ID {crop_id} not found.")

    crop_payload: Dict[str, Any] = {}
    if crop_in.crop_name is not None:
        crop_payload["crop_name"] = crop_in.crop_name.strip()
    if crop_in.scientific_name is not None:
        crop_payload["scientific_name"] = crop_in.scientific_name
    if crop_in.category is not None:
        crop_payload["category"] = crop_in.category
    if crop_in.growing_season is not None:
        crop_payload["growing_season"] = crop_in.growing_season
    if crop_in.planting_time is not None:
        crop_payload["planting_time"] = crop_in.planting_time
    if crop_in.harvest_time is not None:
        crop_payload["harvest_time"] = crop_in.harvest_time
    if crop_in.soil_requirement is not None:
        crop_payload["soil_requirement"] = crop_in.soil_requirement
    if crop_in.water_requirement is not None:
        crop_payload["water_requirement"] = crop_in.water_requirement
    if crop_in.fertilizer is not None:
        crop_payload["fertilizer"] = crop_in.fertilizer
    if crop_in.image is not None:
        crop_payload["image"] = crop_in.image
    if crop_in.image_url is not None:
        crop_payload["image_url"] = crop_in.image_url
        crop_payload["image"] = crop_in.image_url
    if crop_in.gallery_urls is not None:
        crop_payload["gallery_urls"] = crop_in.gallery_urls
    if crop_in.crop_duration_days is not None:
        crop_payload["crop_duration_days"] = crop_in.crop_duration_days

    if crop_payload:
        try:
            execute_query(supabase.table("crops").update(crop_payload).eq("id", crop_id))
        except Exception:
            # Fallback if image_url or gallery_urls column not yet in DB
            crop_payload.pop("image_url", None)
            crop_payload.pop("gallery_urls", None)
            execute_query(supabase.table("crops").update(crop_payload).eq("id", crop_id))

    # Sync growth stages if provided
    if crop_in.growth_stages is not None:
        execute_query(supabase.table("growth_stages").delete().eq("crop_id", crop_id))
        if crop_in.growth_stages:
            stages_payload = [
                {"crop_id": crop_id, "stage_number": s.stage_number, "stage_name": s.stage_name}
                for s in crop_in.growth_stages
            ]
            execute_query(supabase.table("growth_stages").insert(stages_payload))

    # Sync diseases if provided
    if crop_in.diseases is not None:
        execute_query(supabase.table("diseases").delete().eq("crop_id", crop_id))
        diseases_payload = [
            {"crop_id": crop_id, "disease_name": d.strip()}
            for d in crop_in.diseases if d.strip()
        ]
        if diseases_payload:
            execute_query(supabase.table("diseases").insert(diseases_payload))

    # Sync regions if provided
    if crop_in.regions is not None:
        execute_query(supabase.table("regions").delete().eq("crop_id", crop_id))
        regions_payload = [
            {"crop_id": crop_id, "region_name": r.strip()}
            for r in crop_in.regions if r.strip()
        ]
        if regions_payload:
            execute_query(supabase.table("regions").insert(regions_payload))

    updated_name = crop_payload.get("crop_name", existing[0]["crop_name"])
    return get_crop_by_name(updated_name)


@router.delete("/admin/crops/{crop_id}", status_code=status.HTTP_200_OK, summary="Delete a crop record (Admin)")
@router.delete("/crops/{crop_id}", status_code=status.HTTP_200_OK, summary="Delete a crop record")
def delete_crop(crop_id: int):
    """Delete a crop record and all associated child rows."""
    existing = execute_query(supabase.table("crops").select("id, crop_name").eq("id", crop_id).limit(1))
    if not existing:
        raise HTTPException(status_code=404, detail=f"Crop with ID {crop_id} not found.")

    crop_name = existing[0]["crop_name"]

    try:
        execute_query(supabase.table("growth_stages").delete().eq("crop_id", crop_id))
        execute_query(supabase.table("diseases").delete().eq("crop_id", crop_id))
        execute_query(supabase.table("regions").delete().eq("crop_id", crop_id))
        execute_query(supabase.table("crop_images").delete().eq("crop_id", crop_id))
    except Exception as exc:
        logger.warning(f"Error deleting child rows for crop {crop_id}: {exc}")

    execute_query(supabase.table("crops").delete().eq("id", crop_id))

    return {
        "success": True,
        "message": f"Successfully deleted crop '{crop_name}' (ID: {crop_id}) and associated records.",
    }
