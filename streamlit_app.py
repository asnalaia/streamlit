import requests
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Nutri AI",
    page_icon="🍽️",
    layout="wide"
)

API_URL = st.secrets["API_URL"]

st.title("🍽️ Nutri AI")
st.write("Prediksi makanan dari gambar, estimasi nutrisi, perbandingan AKG, dan rekomendasi gizi.")

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Upload Gambar Makanan")

    uploaded_file = st.file_uploader(
        "Pilih gambar makanan",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar yang diupload", use_container_width=True)

with col2:
    st.subheader("Profil Pengguna")

    porsi_gram = st.number_input(
        "Porsi makanan (gram)",
        min_value=1,
        max_value=2000,
        value=100,
        step=10
    )

    age = st.number_input(
        "Usia",
        min_value=1,
        max_value=100,
        value=21,
        step=1
    )

sex = st.selectbox(
    "Jenis kelamin",
    options=["female", "male"],
    format_func=lambda x: "Perempuan" if x == "female" else "Laki-laki"
)

pregnancy_month = 0
breastfeeding_month = 0

if sex == "female":
    condition = st.selectbox(
        "Kondisi",
        options=["normal", "pregnant", "breastfeeding"],
        format_func=lambda x: {
            "normal": "Normal",
            "pregnant": "Hamil",
            "breastfeeding": "Menyusui"
        }[x]
    )

    if condition == "pregnant":
        pregnancy_month = st.number_input(
            "Usia kehamilan (bulan)",
            min_value=1,
            max_value=9,
            value=1,
            step=1
        )
        breastfeeding_month = 0

    elif condition == "breastfeeding":
        breastfeeding_month = st.number_input(
            "Lama menyusui (bulan)",
            min_value=1,
            max_value=24,
            value=1,
            step=1
        )
        pregnancy_month = 0

    else:
        pregnancy_month = 0
        breastfeeding_month = 0

else:
    condition = "normal"
    pregnancy_month = 0
    breastfeeding_month = 0

st.divider()

if st.button("Analisis Makanan", type="primary"):
    if uploaded_file is None:
        st.warning("Silakan upload gambar makanan terlebih dahulu.")
    else:
        with st.spinner("Sedang menganalisis gambar makanan..."):
            try:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }

                data = {
                    "porsi_gram": porsi_gram,
                    "age": age,
                    "sex": sex,
                    "condition": condition,
                    "pregnancy_month": pregnancy_month,
                    "breastfeeding_month": breastfeeding_month
                }

                response = requests.post(
                    API_URL,
                    files=files,
                    data=data,
                    timeout=180
                )

                result = response.json()

                if result.get("status") != "success":
                    st.error("Gagal memproses gambar.")
                    st.json(result)
                else:
                    st.success("Analisis berhasil!")

                    st.subheader("Hasil Prediksi Makanan")

                    col_a, col_b, col_c = st.columns(3)

                    with col_a:
                        st.metric("Makanan", result["makanan"])

                    with col_b:
                        st.metric("Confidence", f"{result['confidence_persen']}%")

                    with col_c:
                        st.metric("Porsi", f"{result['porsi_gram']} gram")

                    st.subheader("Estimasi Nutrisi")

                    nutrisi = result["estimasi_nutrisi"]

                    n1, n2, n3, n4 = st.columns(4)

                    with n1:
                        st.metric("Kalori", f"{nutrisi.get('calories_kcal', 0)} kcal")
                        st.metric("Protein", f"{nutrisi.get('protein_g', 0)} g")

                    with n2:
                        st.metric("Karbohidrat", f"{nutrisi.get('carbs_g', 0)} g")
                        st.metric("Lemak", f"{nutrisi.get('fat_g', 0)} g")

                    with n3:
                        st.metric("Serat", f"{nutrisi.get('fiber_g', 0)} g")
                        st.metric("Kalsium", f"{nutrisi.get('calcium_mg', 0)} mg")

                    with n4:
                        st.metric("Zat Besi", f"{nutrisi.get('iron_mg', 0)} mg")
                        st.metric("Vitamin C", f"{nutrisi.get('vitamin_c_mg', 0)} mg")

                    st.subheader("Komparasi dengan AKG Harian")

                    for item in result["komparasi_akg"]:
                        nutrient = item["nutrient"]
                        percent = item["percent_of_daily_need"]
                        predicted = item["predicted_amount"]
                        target = item["daily_target_akg"]

                        st.write(
                            f"**{nutrient}**: {predicted:.2f} dari target {target:.2f} "
                            f"({percent:.2f}%)"
                        )

                        st.progress(min(percent / 100, 1.0))

                    st.subheader("Rekomendasi Gizi")

                    rekomendasi = result.get("rekomendasi_gemini", "")

                    if rekomendasi:
                        st.info(rekomendasi)
                    else:
                        st.warning("Rekomendasi belum tersedia.")

                    with st.expander("Lihat response JSON"):
                        st.json(result)

            except requests.exceptions.ConnectionError:
                st.error("Tidak bisa terhubung ke backend. Pastikan URL backend sudah benar.")

            except Exception as e:
                st.error(f"Terjadi error: {str(e)}")