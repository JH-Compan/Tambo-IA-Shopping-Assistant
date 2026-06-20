import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import Client, create_client


ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_BACKEND_KEY = (
    os.getenv("SUPABASE_SECRET_KEY")
    or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

if not SUPABASE_URL:
    raise RuntimeError("Falta SUPABASE_URL en python/.env")

if not SUPABASE_BACKEND_KEY:
    raise RuntimeError(
        "Falta SUPABASE_SECRET_KEY o "
        "SUPABASE_SERVICE_ROLE_KEY en python/.env"
    )

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_BACKEND_KEY,
)