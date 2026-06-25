import os
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from supabase import create_client, Client
except ImportError:
    Client = None
    create_client = None

SUPABASE_URL_ENV = "SUPABASE_URL"
SUPABASE_KEY_ENV = "SUPABASE_KEY"
TABLE_NAME = "analyses"

USE_SUPABASE = bool(os.environ.get(SUPABASE_URL_ENV)) and bool(os.environ.get(SUPABASE_KEY_ENV))

_client = None
if USE_SUPABASE:
    if create_client is None:
        raise ImportError(
            "supabase paketi yüklü değil. `pip install supabase` çalıştırın veya "
            "requirements.txt'i requirements'e ekleyin."
        )
    _client = create_client(
        os.environ[SUPABASE_URL_ENV],
        os.environ[SUPABASE_KEY_ENV],
    )


def _validate(name: str, complaint: str, ai_response: str):
    if not complaint or not complaint.strip():
        raise ValueError("Şikayet boş olamaz.")
    if not ai_response or not ai_response.strip():
        raise ValueError("AI yanıtı boş olamaz.")


def save_analysis(*, name: str, age, city: str, complaint: str,
                  ai_response: str, model_used: str = "",
                  response_time=None, source: str = "streamlit") -> int:

    name = (name or "").strip()[:100] or "(isimsiz)"
    city = (city or "").strip()[:50]
    complaint = (complaint or "").strip()[:2000]
    ai_response = (ai_response or "").strip()

    if not complaint:
        raise ValueError("Şikayet boş olamaz.")
    if not ai_response:
        raise ValueError("AI yanıtı boş olamaz.")

    try:
        age_int = int(age) if age not in (None, "", "None") else None
    except (TypeError, ValueError):
        age_int = None

    try:
        response_time_float = float(response_time) if response_time is not None else None
    except (TypeError, ValueError):
        response_time_float = None

    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "name": name,
        "age": age_int,
        "city": city or None,
        "complaint": complaint,
        "ai_response": ai_response,
        "model_used": model_used or None,
        "response_time": response_time_float,
        "source": source,
    }

    if not USE_SUPABASE:
        raise RuntimeError(
            "Supabase yapılandırılmamış. .env dosyanıza SUPABASE_URL ve SUPABASE_KEY ekleyin."
        )

    result = _client.table(TABLE_NAME).insert(payload).execute()
    if not result.data:
        raise RuntimeError(f"Supabase insert başarısız: {result}")

    return result.data[0].get("id", 0)


def fetch_recent(limit: int = 50):
    if not USE_SUPABASE:
        raise RuntimeError("Supabase yapılandırılmamış.")

    result = (
        _client.table(TABLE_NAME)
        .select("*")
        .order("id", desc=True)
        .limit(int(limit))
        .execute()
    )
    return list(result.data or [])


def count_records() -> int:
    if not USE_SUPABASE:
        raise RuntimeError("Supabase yapılandırılmamış.")

    result = (
        _client.table(TABLE_NAME)
        .select("id", count="exact")
        .limit(1)
        .execute()
    )
    return result.count or 0


def close():
    pass


def is_configured() -> bool:
    return USE_SUPABASE