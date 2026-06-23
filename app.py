import streamlit as st
from atomy_ai_agent import ask_atomy_ai_premium

# Web Sayfası Ayarları
st.set_page_config(page_title="Atomy Trakya AI Cilt Analizi", page_icon="🌸", layout="centered")

# Şık bir görsel başlık alanı
st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>🌸 Nesrin Hanım ile AI Cilt Analizi</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:18px;'>Trakya iklimine ve cildinize özel ücretsiz Kore güzellik reçetenizi saniyeler içinde oluşturun.</p>", unsafe_allow_html=True)
st.write("---")

# Kullanıcı Giriş Formu
st.subheader("📋 Kişisel Bilgileriniz & Cilt Şikayetiniz")

isim = st.text_input("Adınız ve Soyadınız", placeholder="Örn: Ayşe Y.")
yas = st.number_input("Yaşınız", min_value=15, max_value=100, value=35)
şehir = st.selectbox("Yaşadığınız Trakya Şehri/İlçesi", ["Lüleburgaz", "Edirne", "Kırklareli", "Tekirdağ", "Çorlu", "Keşan", "Diğer"])
şikayet = st.text_area("Cildinizde şu an en çok rahatsız olduğunuz sorunları detaylıca anlatın:", 
                       placeholder="Örn: Gözlerimin kenarında kaz ayakları çıkmaya başladı, yanaklarım pul pul dökülüyor...")

st.write("\n")

# Analiz Butonu
if st.button("🚀 Yapay Zeka ile Analizi Başlat", use_container_width=True):
    if not isim or not şikayet:
        st.warning("⚠️ Lütfen analiz için adınızı ve cilt şikayetinizi eksiksiz doldurun.")
    else:
        with st.spinner("🧠 80 Sayfalık Atomy Kataloğu taranıyor ve cildiniz analiz ediliyor..."):
            # Bizim yazdığımız o güçlü premium RAG motorunu çağırıyoruz
            rapor_sonucu = ask_atomy_ai_premium(isim, yas, şehir, şikayet)
            
            st.success("🎉 Analiziniz Başarıyla Tamamlandı!")
            st.write("---")
            
            # Sonucu şık bir kutu (blockquote / markdown) içinde kullanıcıya gösteriyoruz
            st.info(rapor_sonucu)
            
            st.write("---")
            st.info("💡 Yukarıdaki analizinizi kopyalayarak veya aşağıdaki WhatsApp linkine tıklayarak Nesrin Hanım'a doğrudan ulaştırabilirsiniz.")