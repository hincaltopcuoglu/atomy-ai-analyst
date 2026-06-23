import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

PDF_PATH = "Atomy_2026_katalog.pdf"


def upload_catalog_to_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("HATA: GEMINI_API_KEY bulunamadı. .env dosyanıza ekleyin.")
        sys.exit(1)

    if not os.path.exists(PDF_PATH):
        print(f"HATA: {PDF_PATH} bulunamadı!")
        return

    file_size = os.path.getsize(PDF_PATH)

    # 1. Google'a dosya yükleme başlatma isteği (Metadata)
    url_init = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={api_key}"
    headers_init = {
        "X-Goog-Upload-Protocol": "resumable",
        "X-Goog-Upload-Command": "start",
        "X-Goog-Upload-Header-Content-Length": str(file_size),
        "X-Goog-Upload-Header-Content-Type": "application/pdf",
        "Content-Type": "application/json",
    }
    payload_init = {"file": {"display_name": "Atomy Katalog"}}

    print("1. Google Gemini File API ile bağlantı kuruluyor...")
    res_init = requests.post(url_init, headers=headers_init, json=payload_init)

    if res_init.status_code != 200:
        print(f"Init isteği başarısız. HTTP {res_init.status_code}")
        print(res_init.text)
        return

    upload_url = res_init.headers.get("X-Goog-Upload-URL")
    if not upload_url:
        print("X-Goog-Upload-URL başlığı response'da bulunamadı.")
        print("Headers:", dict(res_init.headers))
        print("Body:", res_init.text)
        return

    # 2. Dosya içeriğini (Binary) Google sunucularına yükle
    print("2. 80 Sayfalık katalog Google hafızasına yükleniyor (Bu biraz sürebilir)...")
    with open(PDF_PATH, "rb") as f:
        pdf_data = f.read()

    if len(pdf_data) == 0:
        print(f"HATA: {PDF_PATH} okundu ama içi boş (0 byte).")
        return

    if len(pdf_data) != file_size:
        print(f"UYARI: Header'da {file_size} byte dediniz ama dosyadan {len(pdf_data)} byte okundu.")
        file_size = len(pdf_data)

    print(f"   -> {len(pdf_data):,} byte veri Google'a gönderiliyor...")

    headers_upload = {
        "X-Goog-Upload-Offset": "0",
        "X-Goog-Upload-Command": "upload, finalize",
        "X-Goog-Upload-Header-Content-Length": str(file_size),
        "Content-Type": "application/pdf",
    }

    res_upload = requests.post(upload_url, headers=headers_upload, data=pdf_data)

    if res_upload.status_code != 200:
        print(f"Upload başarısız. HTTP {res_upload.status_code}")
        print(res_upload.text)
        return

    try:
        res_json = res_upload.json()
    except ValueError:
        print("Upload response'u JSON değil. Muhtemelen auth/izin hatası.")
        print(f"Status: {res_upload.status_code}")
        print(f"Body: {res_upload.text[:1000]}")
        return

    if "file" not in res_json or "uri" not in res_json.get("file", {}):
        print("Beklenen 'file.uri' response'ta yok. Dönen JSON:")
        print(res_json)
        return

    gemini_file_uri = res_json["file"]["uri"]

    print("\nBAŞARILI! Katalog Google bulutuna yüklendi.")
    print(f"SENİN GEMINI DOSYA URI'N: {gemini_file_uri}")
    print("İpucu: Bu URI değerini kopyala, bir sonraki adımda kullanacağız.")


if __name__ == "__main__":
    upload_catalog_to_gemini()
