import time
import streamlit as st
from atomy_ai_agent import ask_atomy_ai_premium
from database import save_analysis

st.set_page_config(page_title="Atomy Trakya AI Cilt Analizi", page_icon="🌸", layout="centered")

st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>🌸 Nesrin Hanım ile AI Cilt Analizi</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:18px;'>Trakya iklimine ve cildinize özel ücretsiz Kore güzellik reçetenizi saniyeler içinde oluşturun.</p>", unsafe_allow_html=True)
st.write("---")

st.subheader("📋 Kişisel Bilgileriniz & Cilt Şikayetiniz")

isim = st.text_input("Adınız ve Soyadınız", placeholder="Örn: Ayşe Y.")
yas = st.number_input("Yaşınız", min_value=15, max_value=100, value=35)
şehir = st.selectbox("Yaşadığınız Trakya Şehri/İlçesi", ["Lüleburgaz", "Edirne", "Kırklareli", "Tekirdağ", "Çorlu", "Keşan", "Diğer"])
şikayet = st.text_area("Cildinizde şu an en çok rahatsız olduğunuz sorunları detaylıca anlatın:",
                       placeholder="Örn: Gözlerimin kenarında kaz ayakları çıkmaya başladı, yanaklarım pul pul dökülüyor...")

st.write("\n")

if st.button("🚀 Yapay Zeka ile Analizi Başlat", use_container_width=True):
    if not isim or not şikayet:
        st.warning("⚠️ Lütfen analiz için adınızı ve cilt şikayetinizi eksiksiz doldurun.")
    else:
        try:
            with st.spinner("🧠 80 Sayfalık Atomy Kataloğu taranıyor ve cildiniz analiz ediliyor..."):
                baslangic = time.perf_counter()
                rapor_sonucu = ask_atomy_ai_premium(isim, yas, şehir, şikayet)
                gecen_sure = round(time.perf_counter() - baslangic, 2)

            try:
                save_analysis(
                    name=isim,
                    age=yas,
                    city=şehir,
                    complaint=şikayet,
                    ai_response=rapor_sonucu,
                    model_used="gemini-2.5-flash",
                    response_time=gecen_sure,
                    source="streamlit",
                )
            except Exception as db_err:
                st.warning(f"⚠️ Analiz tamamlandı ancak veritabanına kayıt sırasında sorun oluştu: {db_err}")

            st.success(f"🎉 Analiziniz Başarıyla Tamamlandı! ({gecen_sure} sn)")
            st.write("---")
            st.info(rapor_sonucu)
            st.write("---")
            st.info("💡 Yukarıdaki analizinizi kopyalayarak veya aşağıdaki WhatsApp linkine tıklayarak Nesrin Hanım'a doğrudan ulaştırabilirsiniz.")
        except Exception as e:
            st.error(f"Beklenmeyen bir hata oluştu: {e}")