"""Import Bangladesh crop data from JSON into Supabase PostgreSQL database.

This script reads crop information from data/bangladesh_crop_database_v2.json
and inserts data across four relational tables in Supabase:
1. crops (main crop details)
2. growth_stages (ordered stages for each crop)
3. diseases (common diseases associated with each crop)
4. regions (suitable growing regions in Bangladesh)
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from postgrest.exceptions import APIError
from supabase import Client, create_client


def get_env_credentials() -> tuple[str, str]:
    """Load and validate Supabase credentials from .env file."""
    # Look for .env in current directory or script directory
    script_dir = Path(__file__).resolve().parent
    env_path = script_dir / ".env"
    
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()

    if not supabase_url:
        print("Error: SUPABASE_URL is not set in .env", file=sys.stderr)
        sys.exit(1)

    if not supabase_key:
        print("Error: SUPABASE_KEY is not set in .env", file=sys.stderr)
        sys.exit(1)

    # Normalize URL in case /rest/v1 or trailing slashes are present
    supabase_url = supabase_url.rstrip("/")
    if supabase_url.endswith("/rest/v1"):
        supabase_url = supabase_url[:-8].rstrip("/")

    return supabase_url, supabase_key


def load_crops_json(json_path: Path) -> List[Dict[str, Any]]:
    """Read and parse the crop JSON database file."""
    if not json_path.exists():
        print(f"Error: JSON file not found at {json_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                print(f"Error: Expected a JSON array of crops in {json_path}", file=sys.stderr)
                sys.exit(1)
            return data
    except json.JSONDecodeError as exc:
        print(f"Error parsing JSON file {json_path}: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Unexpected error reading {json_path}: {exc}", file=sys.stderr)
        sys.exit(1)


def check_crop_exists(supabase: Client, crop_name: str) -> bool:
    """Check if a crop with the given name already exists in the crops table."""
    try:
        response = supabase.table("crops").select("id").eq("crop_name", crop_name).limit(1).execute()
        return bool(response.data)
    except APIError as exc:
        # Check if RLS policy blocked the read
        if exc.code == "42501":
            print("\n[RLS Error] Permission denied by Row Level Security policy on 'crops'.", file=sys.stderr)
            print("Please ensure your table allows SELECT/INSERT or use the service_role key.", file=sys.stderr)
        raise exc


def import_data():
    """Main execution function to import crops into Supabase."""
    supabase_url, supabase_key = get_env_credentials()

    try:
        supabase: Client = create_client(supabase_url, supabase_key)
    except Exception as exc:
        print(f"Error initializing Supabase client: {exc}", file=sys.stderr)
        sys.exit(1)

    base_dir = Path(__file__).resolve().parent
    json_path = base_dir / "data" / "bangladesh_crop_database_v2.json"

    crops_data = load_crops_json(json_path)
    print(f"Loaded {len(crops_data)} crops from '{json_path.name}'. Starting import...\n")

    inserted_count = 0
    skipped_count = 0
    failed_count = 0

    for idx, crop in enumerate(crops_data, start=1):
        crop_name = crop.get("crop_name", "").strip()
        if not crop_name:
            print(f"[{idx}/{len(crops_data)}] Skipping record with missing crop_name.")
            skipped_count += 1
            continue

        # Step 1: Check for duplicate crop
        try:
            if check_crop_exists(supabase, crop_name):
                print(f"[{idx}/{len(crops_data)}] Crop '{crop_name}' already exists. Skipping.")
                skipped_count += 1
                continue
        except Exception as exc:
            print(f"[{idx}/{len(crops_data)}] Error checking existence for '{crop_name}': {exc}")
            failed_count += 1
            continue

        # Step 2: Prepare main crop record
        crop_payload = {
            "crop_name": crop_name,
            "scientific_name": crop.get("scientific_name"),
            "category": crop.get("category"),
            "growing_season": crop.get("growing_season"),
            "planting_time": crop.get("planting_time"),
            "harvest_time": crop.get("harvest_time"),
            "soil_requirement": crop.get("soil_requirement"),
            "water_requirement": crop.get("water_requirement"),
            "fertilizer": crop.get("fertilizer"),
            "image": crop.get("image"),
            "crop_duration_days": str(crop.get("crop_duration_days")) if crop.get("crop_duration_days") is not None else None,
        }

        # Step 3: Insert into 'crops' table
        try:
            res = supabase.table("crops").insert(crop_payload).execute()
            if not res.data:
                raise RuntimeError("No data returned after insert.")
            crop_id = res.data[0]["id"]
            print(f"Inserted {crop_name}")
        except APIError as exc:
            print(f"Failed to insert crop '{crop_name}': {exc.message} (Code: {exc.code})")
            if exc.code == "42501":
                print("  -> Tip: Row Level Security (RLS) is enabled. Add an INSERT policy or use the service_role key.")
            failed_count += 1
            continue
        except Exception as exc:
            print(f"Failed to insert crop '{crop_name}': {exc}")
            failed_count += 1
            continue

        # Step 4: Insert related data (growth_stages, diseases, regions)
        related_failed = False

        # 4a. Growth stages
        growth_stages = crop.get("growth_stages", [])
        if growth_stages:
            stages_payload = []
            for s_idx, stage in enumerate(growth_stages, start=1):
                stage_name = stage.get("stage_name") if isinstance(stage, dict) else str(stage)
                stages_payload.append({
                    "crop_id": crop_id,
                    "stage_number": s_idx,
                    "stage_name": stage_name,
                })
            try:
                supabase.table("growth_stages").insert(stages_payload).execute()
                print(f"Inserted {len(stages_payload)} growth stages")
            except Exception as exc:
                print(f"  Error inserting growth stages for '{crop_name}': {exc}")
                related_failed = True

        # 4b. Common diseases
        common_diseases = crop.get("common_diseases", [])
        if common_diseases:
            diseases_payload = []
            for item in common_diseases:
                d_name = item.get("disease_name") if isinstance(item, dict) else str(item)
                diseases_payload.append({
                    "crop_id": crop_id,
                    "disease_name": d_name,
                })
            try:
                supabase.table("diseases").insert(diseases_payload).execute()
                print(f"Inserted {len(diseases_payload)} diseases")
            except Exception as exc:
                print(f"  Error inserting diseases for '{crop_name}': {exc}")
                related_failed = True

        # 4c. Bangladesh regions
        bangladesh_regions = crop.get("bangladesh_regions", [])
        if bangladesh_regions:
            regions_payload = []
            for item in bangladesh_regions:
                r_name = item.get("region_name") if isinstance(item, dict) else str(item)
                regions_payload.append({
                    "crop_id": crop_id,
                    "region_name": r_name,
                })
            try:
                supabase.table("regions").insert(regions_payload).execute()
                print(f"Inserted {len(regions_payload)} regions")
            except Exception as exc:
                print(f"  Error inserting regions for '{crop_name}': {exc}")
                related_failed = True

        if related_failed:
            print(f"Warning: Rolling back '{crop_name}' (ID: {crop_id}) due to errors in related tables...")
            try:
                supabase.table("crops").delete().eq("id", crop_id).execute()
                print(f"Successfully rolled back '{crop_name}'.")
            except Exception as rollback_exc:
                print(f"Failed to rollback '{crop_name}': {rollback_exc}")
            failed_count += 1
            print("-" * 40)
            continue

        print("-" * 40)
        inserted_count += 1

    print("\n" + "=" * 40)
    print("IMPORT SUMMARY")
    print(f"  Total processed: {len(crops_data)}")
    print(f"  Successfully inserted: {inserted_count}")
    print(f"  Skipped (existing or invalid): {skipped_count}")
    print(f"  Failed: {failed_count}")
    print("=" * 40)


if __name__ == "__main__":
    import_data()

