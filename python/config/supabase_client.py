import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

if not SUPABASE_URL:
    raise ValueError("Falta SUPABASE_URL en python/.env")

if not SUPABASE_KEY:
    raise ValueError("Falta SUPABASE_KEY en python/.env")

if "/rest/v1" in SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL no debe incluir /rest/v1. Usa solo https://TU_PROJECT_REF.supabase.co"
    )

if "dashboard" in SUPABASE_URL or "supabase.com/project" in SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL no debe ser la URL del dashboard. Usa la Project URL: https://TU_PROJECT_REF.supabase.co"
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)