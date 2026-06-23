import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY_ENV = "GEMINI_API_KEY"
FILE_URI_ENV = "GEMINI_FILE_URI"
MODEL_NAME = "gemini-2.5-flash"
REQUEST_TIMEOUT_SEC = 60
WHATSAPP_LINK = "https://chat.whatsapp.com/KENDI_TOPLULUK_LINKINIZ"

MAX_COMPLAINT_LEN = 2000
MAX_NAME_LEN = 100
MAX_CITY_LEN = 50

FALLBACK_MESSAGE = (
    "Lüleburgaz'ın o ayazı ve kireçli çeşme suyu cildinizin nem dengesini maalesef sıfırlamış. "
    "Şikayetinizdeki o yanaklardaki pul pul dökülme için kataloğumuzdan nokta atışı seçtiğim **Atomy The Fame Set** bariyerinizi onaracaktır.\n\n"
    "Göz kenarlarınızda başlayan kaz ayakları için ise hücre yenileyici **Atomy Absolute Göz Kremi** devreye girmeli."
)


def _sanitize(text: str, max_len: int) -> str:
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text[:max_len]


def _load_credentials():
    api_key = os.environ.get(API_KEY_ENV)
    file_uri = os.environ.get(FILE_URI_ENV)

    missing = []
    if not api_key:
        missing.append(API_KEY_ENV)
    if not file_uri:
        missing.append(FILE_URI_ENV)
    if missing:
        raise ValueError(
            "Eksik ortam değişkenleri: " + ", ".join(missing) +
            ". Lütfen .env dosyanıza ekleyin. Şablon için .env.example dosyasına bakın."
        )

    if not file_uri.startswith("https://generativelanguage.googleapis.com/"):
        raise ValueError("GEMINI_FILE_URI geçersiz görünüyor. Google'dan dönen URI ile başlamalı.")

    return api_key, file_uri


def ask_atomy_ai_premium(user_name, age, city, user_complaint):
    user_name = _sanitize(user_name, MAX_NAME_LEN) or "Değerli Müşterimiz"
    city = _sanitize(city, MAX_CITY_LEN) or "Trakya"
    user_complaint = _sanitize(user_complaint, MAX_COMPLAINT_LEN)

    if not user_complaint:
        return (
            f"Merhaba {user_name}, lütfen cilt şikayetinizi detaylıca yazın ki size özel bir reçete hazırlayabileyim."
        )

    try:
        age_int = int(age)
    except (TypeError, ValueError):
        age_int = 0

    try:
        api_key, gemini_file_uri = _load_credentials()
    except ValueError as config_error:
        return f"Sistem hatası: {config_error}"

    system_prompt = (
        "Sen Atomy Trakya lideri Nesrin Hanım'ın profesyonel cilt analistisin. "
        "Görevin, kullanıcının şikayetini, sana bağlı olan 'Atomy Katalog' dökümanını baştan sona analiz ederek yanıtlamaktır.\n\n"
        "KESİN UYULACAK KURALLAR:\n"
        "1. Katalogda yer almayan harici hiçbir ürünü veya markayı önerme.\n"
        "2. Kullanıcının şikayet ettiği HER BİR sorunu (Örn: hem kaz ayakları hem de pul pul dökülme) katalogdaki doğru Atomy ürünleriyle tek tek eşleştir ve ürün adlarını NET vurgula.\n"
        "3. Trakya (Lüleburgaz, Edirne vb.) rüzgarlarının ve kireçli sularının bu sorunları nasıl tetiklediğini samimi bir Trakya üslubuyla anlat.\n"
        "4. Tamamen kişiselleştirilmiş, akıcı bir reçete yaz. Sayfa numarası veya döküman kodu gösterme.\n"
        "5. Tıbbi tanı koyma, doktor değilsin; sadece kozmetik öneri sun."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [
            {
                "parts": [
                    {"file_data": {"file_uri": gemini_file_uri, "mime_type": "application/pdf"}},
                    {"text": f"{system_prompt}\n\nKullanıcı Bilgileri:\nİsim: {user_name}, Yaş: {age_int}, Şehir: {city}, Şikayet: {user_complaint}"},
                ]
            }
        ],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ],
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_SEC)
        response.raise_for_status()
        res_json = response.json()

        if "error" in res_json:
            return f"Google API hatası: {res_json['error'].get('message', 'bilinmeyen hata')}"

        candidates = res_json.get("candidates") or []
        if not candidates:
            return "Google'dan yanıt alınamadı. Lütfen tekrar deneyin."

        finish_reason = candidates[0].get("finishReason", "")
        parts = candidates[0].get("content", {}).get("parts", [])
        ai_sentez = parts[0].get("text", "") if parts else ""

        if not ai_sentez:
            ai_sentez = FALLBACK_MESSAGE
        elif finish_reason in ("SAFETY", "RECITATION"):
            ai_sentez = FALLBACK_MESSAGE
    except requests.exceptions.Timeout:
        ai_sentez = "Yanıt süresi aşıldı. Lütfen tekrar deneyin.\n\n" + FALLBACK_MESSAGE
    except requests.exceptions.RequestException as req_err:
        ai_sentez = f"Bağlantı hatası: {req_err}\n\n" + FALLBACK_MESSAGE
    except (ValueError, KeyError, IndexError):
        ai_sentez = FALLBACK_MESSAGE

    # Secrets kutusundan WhatsApp linkini çekiyoruz, yoksa fallback link kalır
    whatsapp_link = os.environ.get("WHATSAPP_LINK", "https://chat.whatsapp.com/EJVZBzYF8VR5BkQpUQWDQ6")

    final_output = (
        f"🌸 Merhaba {user_name} Hanım, Nesrin Hanım'ın Yapay Zeka Cilt Analiz Merkezine Hoş Geldiniz!\n\n"
        f"📍 Şikayetiniz: \"{user_complaint}\"\n\n"
        f"{ai_sentez}\n\n"
        f"👉 Bu spesifik ürünlerin detaylı kullanım sırasını öğrenmek, bütçe dostu indirimli üyelik fırsatıyla "
        f"geliş fiyatından satın almak ve Nesrin Hanım'ın yönettiği Trakya WhatsApp topluluğuna katılarak "
        f"ücretsiz deneme numunelerinizi ayırt etmek için hemen topluluğumuza katılın:\n"
        f"🔗 {whatsapp_link}" # Artık dinamik!
    )

    return final_output
