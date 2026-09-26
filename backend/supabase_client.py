"""Supabase client configuration and initialization."""

import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import Client, create_client

# Resolve .env relative to this file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be configured in backend/.env")

# Normalize URL in case trailing slashes or /rest/v1 are present
SUPABASE_URL = SUPABASE_URL.rstrip("/")
if SUPABASE_URL.endswith("/rest/v1"):
    SUPABASE_URL = SUPABASE_URL[:-8].rstrip("/")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
