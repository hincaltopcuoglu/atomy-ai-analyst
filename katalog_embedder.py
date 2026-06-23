import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

PDF_PATH = "Atomy_2026_katalog.pdf"
DB_DIR = "/Users/hincaltopcuoglu/Desktop/atomy/chroma_db"

def embed_atomy_catalog_smart():
    if not os.path.exists(PDF_PATH):
        print(f"⚠️ HATA: {PDF_PATH} bulunamadı!")
        return

    print("📄 1. 80 Sayfalık Atomy Kataloğu Okunuyor...")
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()
    
    clean_docs = []
    print("\n🧼 2. Sayfa Bazlı Akıllı Filtreleme Yapılıyor...")
    
    # Körlemesine karakter bölmesi (chunking) YAPMIYORUZ. 
    # Her sayfayı bir bütün (bütünsel bağlam) olarak koruyoruz.
    for doc in docs:
        text = doc.page_content.lower()
        
        # Göz yorgunluğu, araba sürmek gibi yorum sayfalarını ve gürültülü datayı eliyoruz
        if "araba kullanırken" in text or "ekran başında" in text or "yorgunluk hissediyordum" in text:
            continue # Bu sayfayı veri tabanına ekleme, çöpe at
            
        clean_docs.append(doc)
        
    print(f"[✓] Gürültülü sayfalar elendi. Toplam {len(clean_docs)} saf ürün sayfası korundu.")

    print("\n🧠 3. Vektörleştirme Başlıyor...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("\n💾 4. Veri Tabanı (ChromaDB) Sıfırdan Güncelleniyor...")
    # Eski hatalı DB'yi temizleyip üzerine yazalım
    vector_db = Chroma.from_documents(clean_docs, embeddings, persist_directory=DB_DIR)
    
    print("\n🎉 BAŞARILI! Sayfa bazlı akıllı RAG hafızası oluşturuldu.")

if __name__ == "__main__":
    embed_atomy_catalog_smart()