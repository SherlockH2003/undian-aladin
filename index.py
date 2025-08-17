# app.py
import streamlit as st
import streamlit.components.v1 as components
import base64
import json
import time
from undian import pemenang

def get_base64_image(image_path):
    """Mengonversi file gambar lokal menjadi string base64."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return ""

# --- Konfigurasi Halaman Streamlit ---
st.set_page_config(layout="wide", page_title="Pengumuman Pemenang")
st.markdown("<h1 style='text-align: center; color: white;'>Undian Pemenang</h1>", unsafe_allow_html=True)
st.markdown(
    """
    <p style='text-align: center;'>Pilih jenis hadiah di bawah ini dan klik "Mulai Mengundi" untuk melihat pemenangnya.</p>
    """, unsafe_allow_html=True
)
st.markdown("<hr>", unsafe_allow_html=True)

# --- Tampilkan Semua Pemenang ---
st.markdown("<h2 style='text-align: center; color: white;'>Hadiah Nabung Rutin Alfamidi</h2>", unsafe_allow_html=True)

# --- Gambar untuk animasi ---
amplop_bg_b64 = get_base64_image("amplop_bg.png") or "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
amplop_image_b64 = get_base64_image("amplop.png") or "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
surat_image_b64 = get_base64_image("letter.png") or "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

# --- UI Streamlit ---
kolom1, kolom2, kolom3 = st.columns([1, 2, 1])
with kolom2:
    jenis_hadiah = st.selectbox(
        "Pilih Jenis Hadiah:",
        options=list(pemenang.keys()),
        key="dropdown"
    )

    # Menggunakan kondisi if untuk tombol "Mulai Animasi"
    start_button = st.button("Mulai Mengundi", use_container_width=True, key="start_button")

# --- Session State ---
if 'animation_trigger' not in st.session_state:
    st.session_state.animation_trigger = 0
if 'selected_winners' not in st.session_state:
    st.session_state.selected_winners = {}
if 'deleted_winners' not in st.session_state:
    st.session_state.deleted_winners = {}
if 'show_winner_list' not in st.session_state:
    st.session_state.show_winner_list = False
if 'start_anim' not in st.session_state:
    st.session_state.start_anim = False
if 'show_balloons_flag' not in st.session_state:
    st.session_state.show_balloons_flag = False

# Reset trigger animasi saat dropdown berubah atau saat awal
# Ini adalah kunci untuk mencegah animasi berulang
if 'previous_jenis_hadiah' not in st.session_state:
    st.session_state.previous_jenis_hadiah = jenis_hadiah
if st.session_state.previous_jenis_hadiah != jenis_hadiah:
    st.session_state.animation_trigger = 0
    st.session_state.show_winner_list = False
    st.session_state.previous_jenis_hadiah = jenis_hadiah

# Hanya jalankan ini jika tombol start_button ditekan
if start_button:
    st.session_state.animation_trigger += 1
    st.session_state.start_anim = True
    st.session_state.show_winner_list = False
    st.session_state.show_balloons_flag = False

# --- Konversi DataFrame ke JSON serializable ---
pemenang_serializable = {}
for key, value in pemenang.items():
    if hasattr(value, 'to_dict'):
        # ambil list nama + branch
        pemenang_serializable[key] = [
            f"{row['Nama']} ({row['Branch']})" for _, row in value.iterrows()
        ]
    else:
        pemenang_serializable[key] = value

pemenang_data_json = json.dumps(pemenang_serializable, ensure_ascii=False)

# --- Data untuk HTML ---
jenis_hadiah_to_show = jenis_hadiah
animation_trigger = st.session_state.animation_trigger

# --- HTML + JS Animasi ---
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Animasi Pemenang</title>
<style>
    body {{
        margin: 0;
        padding: 0;
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
    .container {{
        position: relative;
        width: 100%;
        height: 100%;
        margin: auto;
        overflow: visible;
    }}
    #amplop {{
        position: absolute;
        bottom: -700px;
        left: 50%;
        transform: translateX(-50%);
        transition: bottom 1.4s ease-in-out;
        z-index: 2;
        width: 100%;
        max-width: 1600px;
    }}
    #surat {{
        position: absolute;
        bottom: -70px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1;
        transition: transform 3s ease-in-out, opacity 0.5s ease-in-out;
        width: 80%;
        max-width: 1000px;
        opacity: 0;
    }}
    .surat-behind {{ z-index: 1; opacity: 0; }}
    .surat-center {{ z-index: 2; opacity: 1; }}
    .surat-out {{ transform: translate(-200%, -50%); opacity: 0; }}
    .surat-in {{ transform: translate(-50%, 100%); opacity: 0; }}
    #nama-pemenang {{
        position: absolute;
        top: 1000px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 4;
        font-size: 48px;
        font-weight: bold;
        color: black;
        opacity: 0;
        transition: opacity 0.6s ease-in-out;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        width: 630px;
        height: 380px;
        overflow: hidden;
        padding: 10px;
        box-sizing: border-box;
        font-family: sans-serif;
    }}
    #nama-pemenang .ucapan {{
        font-size: 48px;
        font-weight: bold;
        margin-bottom: 20px;
    }}
    #nama-pemenang .list-pemenang {{
        font-size: 24px;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        text-align: center;
        width: 100%;
    }}
    @keyframes slideUpNama {{
        0% {{ transform: translate(-50%, 300px); opacity: 0; }}
        100% {{ transform: translate(-300px, -630px); opacity: 1; }}
    }}
    .nama-up {{ animation: slideUpNama 0.6s forwards; left: 50%; }}
    @keyframes slideLeft {{
        0% {{ transform: translate(-50%, -50%); opacity: 1; }}
        100% {{ transform: translate(-200%, -50%); opacity: 0; }}
    }}
    @keyframes slideUp {{
        0% {{ transform: translate(-50%, 500px); opacity: 0; }}
        100% {{ transform: translate(-50%, -20%); opacity: 1; }}
    }}
    .slide-up {{ animation: slideUp 0.6s forwards; left: 50%; }}
    .slide-left {{ animation: slideLeft 2s forwards; left: 50%; }}
</style>
</head>
<body>
<div class="container">
    <img id="surat" src="data:image/png;base64,{surat_image_b64}" alt="Surat" class="surat-in">
    <img id="amplop" src="data:image/png;base64,{amplop_image_b64}" alt="Amplop">
    <div id="nama-pemenang"></div>
</div>
<script>
function startAnimation() {{
    let amplop = document.getElementById("amplop");
    let surat = document.getElementById("surat");
    let namaBox = document.getElementById("nama-pemenang");

    amplop.style.bottom = "-700px";
    surat.classList.remove("surat-behind","surat-center","slide-left","slide-up");
    surat.style.zIndex = "1";
    namaBox.classList.remove("nama-up");
    namaBox.innerHTML = "";

    let pemenang = {pemenang_data_json};
    let jenisHadiah = "{jenis_hadiah_to_show}";

    let pemenangText = ""; 

if (["Hadiah Ketiga", "Hadiah Keempat", "Hadiah Cabang"].includes(jenisHadiah)) {{
    pemenangText = `
        <div class="ucapan" style="font-size:30px">🎉 CONGRATULATIONS 🎉</div>
        <div style="font-size:26px">Selamat kepada nama-nama di bawah ini</div>
        <div class="jenis-kemenangan" style="font-size:20px"><br><br>Sebagai pemenang <b>${{jenisHadiah}}</b></div>
    `;
}} else {{
    pemenangText = `
        <div class="ucapan" style="font-size:30px">🎉 CONGRATULATIONS 🎉</div>
        <div class="list-pemenang">${{pemenang[jenisHadiah].map(nama => `<div>${{nama}}</div>`).join("")}}</div>
        <div class="jenis-kemenangan" style="font-size:20px"><br><br>Sebagai pemenang <b>${{jenisHadiah}}</b></div>
    `;
}}


    setTimeout(() => {{ amplop.style.bottom = "160px"; }}, 50);
    setTimeout(() => {{ surat.classList.add("surat-behind"); }}, 500);
    setTimeout(() => {{ surat.classList.remove("surat-behind"); surat.classList.add("surat-center"); }}, 1000);
    setTimeout(() => {{ surat.style.zIndex="1"; surat.classList.remove("surat-center"); surat.classList.add("slide-left"); }}, 1500);
    setTimeout(() => {{
        surat.style.zIndex="3";
        surat.classList.remove("slide-left");
        surat.classList.add("slide-up");
        namaBox.innerHTML = pemenangText;
        namaBox.style.zIndex="4";
        namaBox.classList.add("nama-up");
    }}, 3500);
}}

const animationTrigger = {animation_trigger};
if (animationTrigger > 0) {{ startAnimation(); }}
</script>
</body>
</html>
"""

# Tampilkan komponen HTML
components.html(html_code, height=800, width=1920, scrolling=False)

# ---------------- Kontrol Balon dan Daftar Pemenang ----------------
if st.session_state.start_anim:
    st.session_state.start_anim = False
    st.session_state.show_balloons_flag = True
    time.sleep(4.5)
    st.session_state.show_winner_list = True
    st.rerun() # Memaksa rerun untuk menampilkan daftar pemenang

if st.session_state.show_balloons_flag:
    st.balloons()
    st.session_state.show_balloons_flag = False

# Container untuk menampilkan pemenang
def toggle_winner_list():
    st.session_state.show_winner_list = not st.session_state.show_winner_list
    st.session_state.animation_trigger = 0 # Reset trigger animasi agar tidak terpicu saat tombol ini ditekan
    st.session_state.start_anim = False
    
st.button(
    "Reveal Winner",
    on_click=toggle_winner_list,
    key="reveal_button"
)


if st.session_state.show_winner_list:
    st.subheader("Pemenang:")
    winners_df = pemenang[jenis_hadiah]
    if not winners_df.empty:
        if hasattr(winners_df, 'iloc'):
            if jenis_hadiah == "Hadiah Cabang":
                branch_groups = winners_df.groupby('Branch')
                for branch, group in branch_groups:
                    with st.expander(f"Cabang {branch} ({len(group)} pemenang)"):
                        st.table(group[['Nama', 'Branch']])
            else:
                if len(winners_df) > 10:
                    st.markdown(f"<h4>Daftar Pemenang {jenis_hadiah} (dalam tabel)</h4>", unsafe_allow_html=True)
                    st.table(winners_df[['Nama', 'Branch']])
                else:
                    st.markdown(f"<h4>Daftar Pemenang {jenis_hadiah}</h4>", unsafe_allow_html=True)
                    cols = st.columns(3)
                    for idx, (_, row) in enumerate(winners_df.iterrows()):
                        cols[idx % 3].write(f"• {row['Nama']} ({row['Branch']})")
    else:
        st.write("Tidak ada pemenang untuk kategori ini.")


st.markdown("<hr>", unsafe_allow_html=True)

