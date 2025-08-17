# app.py
import streamlit as st
import streamlit.components.v1 as components
import base64
import json
import time
import random
from undian import pemenang, df_backup

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
    <p style='text-align: center;'>Pilih jenis hadiah di bawah ini dan klik tombol untuk memulai animasi.</p>
    """, unsafe_allow_html=True
)
st.markdown("<hr>", unsafe_allow_html=True)

# --- Gambar untuk animasi amplop ---
amplop_bg_b64 = get_base64_image("amplop_bg.png") or "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
amplop_image_b64 = get_base64_image("amplop.png") or "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
surat_image_b64 = get_base64_image("letter.png") or "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

# --- UI Streamlit Utama ---
kolom1, kolom2, kolom3 = st.columns([1, 2, 1])
with kolom2:
    jenis_hadiah = st.selectbox(
        "Pilih Jenis Hadiah:",
        options=list(pemenang.keys()),
        key="dropdown"
    )

    # Tombol pemicu untuk masing-masing animasi
    col_amp, col_slot = st.columns(2)
    with col_amp:
        if st.button("Mulai Mengundi (Amplop)", use_container_width=True, key="start_button_amplop"):
            st.session_state.animation_trigger += 1
            st.session_state.start_anim = True
            st.session_state.show_winner_list = False
            st.session_state.show_balloons_flag = False
            st.session_state.anim_mode = 'amplop'
    
    with col_slot:
        if st.button("Mulai Mengundi (Slot)", use_container_width=True, key="start_button_slot"):
            st.session_state.anim_mode = 'slot'
            st.session_state.start_slot_anim = True
            st.session_state.show_winner_list = False
            
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
if 'anim_mode' not in st.session_state:
    st.session_state.anim_mode = None
if 'start_slot_anim' not in st.session_state:
    st.session_state.start_slot_anim = False
if 'previous_jenis_hadiah' not in st.session_state:
    st.session_state.previous_jenis_hadiah = jenis_hadiah
if st.session_state.previous_jenis_hadiah != jenis_hadiah:
    st.session_state.animation_trigger = 0
    st.session_state.show_winner_list = False
    st.session_state.anim_mode = None
    st.session_state.start_anim = False
    st.session_state.start_slot_anim = False
    st.session_state.previous_jenis_hadiah = jenis_hadiah

st.markdown("<hr>", unsafe_allow_html=True)

# --- Logika Animasi Amplop ---
if st.session_state.anim_mode == 'amplop':
    # Konversi DataFrame ke JSON serializable
    pemenang_serializable = {}
    for key, value in pemenang.items():
        if hasattr(value, 'to_dict'):
            pemenang_serializable[key] = [
                f"{row['Nama']} ({row['Branch']})" for _, row in value.iterrows()
            ]
        else:
            pemenang_serializable[key] = value
    
    pemenang_data_json = json.dumps(pemenang_serializable, ensure_ascii=False)
    
    jenis_hadiah_to_show = jenis_hadiah
    animation_trigger = st.session_state.animation_trigger
    
    # HTML + JS Animasi Amplop
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Animasi Pemenang</title>
    <style>
        body {{ margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; }}
        .container {{ position: relative; width: 100%; height: 100%; margin: auto; overflow: visible; }}
        #amplop {{ position: absolute; bottom: -700px; left: 50%; transform: translateX(-50%); transition: bottom 1.4s ease-in-out; z-index: 2; width: 100%; max-width: 1600px; }}
        #surat {{ position: absolute; bottom: -70px; left: 50%; transform: translateX(-50%); z-index: 1; transition: transform 3s ease-in-out, opacity 0.5s ease-in-out; width: 80%; max-width: 1000px; opacity: 0; }}
        .surat-behind {{ z-index: 1; opacity: 0; }}
        .surat-center {{ z-index: 2; opacity: 1; }}
        .surat-out {{ transform: translate(-200%, -50%); opacity: 0; }}
        .surat-in {{ transform: translate(-50%, 100%); opacity: 0; }}
        #nama-pemenang {{ position: absolute; top: 1000px; left: 50%; transform: translateX(-50%); z-index: 4; font-size: 48px; font-weight: bold; color: black; opacity: 0; transition: opacity 0.6s ease-in-out; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; width: 630px; height: 380px; overflow: hidden; padding: 10px; box-sizing: border-box; font-family: sans-serif; }}
        #nama-pemenang .ucapan {{ font-size: 48px; font-weight: bold; margin-bottom: 20px; }}
        #nama-pemenang .list-pemenang {{ font-size: 24px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; text-align: center; width: 100%; }}
        @keyframes slideUpNama {{ 0% {{ transform: translate(-50%, 300px); opacity: 0; }} 100% {{ transform: translate(-300px, -630px); opacity: 1; }} }}
        .nama-up {{ animation: slideUpNama 0.6s forwards; left: 50%; }}
        @keyframes slideLeft {{ 0% {{ transform: translate(-50%, -50%); opacity: 1; }} 100% {{ transform: translate(-200%, -50%); opacity: 0; }} }}
        @keyframes slideUp {{ 0% {{ transform: translate(-50%, 500px); opacity: 0; }} 100% {{ transform: translate(-50%, -20%); opacity: 1; }} }}
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
            pemenangText = `<div class="ucapan" style="font-size:30px">🎉 CONGRATULATIONS 🎉</div><div style="font-size:26px">Selamat kepada nama-nama di bawah ini</div><div class="jenis-kemenangan" style="font-size:20px"><br><br>Sebagai pemenang <b>${{jenisHadiah}}</b></div>`;
        }} else {{
            pemenangText = `<div class="ucapan" style="font-size:30px">🎉 CONGRATULATIONS 🎉</div><div class="list-pemenang">${{pemenang[jenisHadiah].map(nama => `<div>${{nama}}</div>`).join("")}}</div><div class="jenis-kemenangan" style="font-size:20px"><br><br>Sebagai pemenang <b>${{jenisHadiah}}</b></div>`;
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
    components.html(html_code, height=800, width=1920, scrolling=False)

    if st.session_state.start_anim:
        st.session_state.start_anim = False
        st.session_state.show_balloons_flag = True
        time.sleep(4.5)
        st.session_state.show_winner_list = True
        st.rerun()

    if st.session_state.show_balloons_flag:
        st.balloons()
        st.session_state.show_balloons_flag = False

# --- Logika Animasi Slot ---
elif st.session_state.anim_mode == 'slot':
    df_pemenang = pemenang[jenis_hadiah]
    if df_pemenang is None or len(df_pemenang) == 0:
        st.warning(f"Tidak ada data pemenang untuk kategori {jenis_hadiah}.")
    else:
        semua_peserta = df_backup["Nama"].tolist()
        pemenang_nama = df_pemenang["Nama"].tolist()

        durasi_animasi = st.slider("Pilih durasi animasi (detik):", min_value=1, max_value=10, value=3, key="slot_duration_slider")

        if st.session_state.start_slot_anim:
            st.session_state.start_slot_anim = False
            num_slots = len(pemenang_nama)
            slot_names_data = []
            for i in range(num_slots):
                shuffled_names = random.sample(semua_peserta, len(semua_peserta))
                slot_list = shuffled_names * 5
                if pemenang_nama[i] not in slot_list:
                    slot_list.append(pemenang_nama[i])
                slot_names_data.append(slot_list)

            js_code = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    .slot-container {{ display: flex; gap: 20px; justify-content: center; align-items: center; margin-top: 20px; }}
                    .slot {{ position: relative; width: 200px; height: 150px; overflow: hidden; border: 2px solid #ccc; border-radius: 5px; background-color: #262730; }}
                    .reel {{ position: absolute; top: 0; left: 0; width: 100%; transition: transform {durasi_animasi}s cubic-bezier(0.175, 0.885, 0.32, 1.275); }}
                    .name {{ height: 50px; line-height: 50px; text-align: center; width: 100%; font-size: 16px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: white; }}
                </style>
            </head>
            <body>
                <div id="root">
                    <div class="slot-container" id="slot-container"></div>
                    <div style="text-align: center; margin-top: 30px;">
                        <h2 style="color: WHITE">Pemenang {jenis_hadiah}:</h2>
                        <p id="winner-text" style="font-size: 24px; color: WHITE">Memutar...</p>
                    </div>
                </div>

                <script>
                    const slotNamesData = {json.dumps(slot_names_data)};
                    const pemenang = {json.dumps(pemenang_nama)};
                    const durasi = {durasi_animasi} * 1000;
                    const container = document.getElementById('slot-container');

                    slotNamesData.forEach((names, i) => {{
                        const slotDiv = document.createElement('div');
                        slotDiv.className = 'slot';
                        slotDiv.id = 'slot-' + i;
                        const reelDiv = document.createElement('div');
                        reelDiv.className = 'reel';
                        names.forEach(name => {{
                            const nameDiv = document.createElement('div');
                            nameDiv.className = 'name';
                            nameDiv.textContent = name;
                            reelDiv.appendChild(nameDiv);
                        }});
                        slotDiv.appendChild(reelDiv);
                        container.appendChild(slotDiv);
                        const itemHeight = 50;
                        const slotHeight = 150;
                        const centerOffset = (slotHeight / 2) - (itemHeight / 2);
                        const winningNameIndex = names.indexOf(pemenang[i]);
                        const stopPosition = -(winningNameIndex * itemHeight) + centerOffset;
                        setTimeout(() => {{
                            reelDiv.style.transform = `translateY(${{stopPosition}}px)`;
                        }}, 100 + i * 200);
                    }});
                    setTimeout(() => {{
                        document.getElementById("winner-text").textContent = pemenang.join(" - ");
                        parent.Streamlit.setComponentValue("show_winner_list", true);
                    }}, durasi + 500);
                </script>
            </body>
            </html>
            """
            components.html(js_code, height=500, width=1000, scrolling=False)

# --- Kontrol Daftar Pemenang ---
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
