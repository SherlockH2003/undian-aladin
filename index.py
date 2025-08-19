import streamlit as st
import streamlit.components.v1 as components
import base64
import json
import time
import random
from undian import pemenang, df_backup

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return ""

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to bottom, #b81b25, #881618);
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --- Config ---
st.set_page_config(layout="wide", page_title="Pengumuman Pemenang")
st.markdown("<h1 style='text-align: center; color: white;'>Undian Pemenang</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Pilih jenis hadiah di bawah ini dan klik tombol untuk memulai animasi.</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- Images ---
amplop_image_b64 = get_base64_image("amplop.png")
surat_image_b64  = get_base64_image("letter.png")
overlay_image_b64 = get_base64_image("overlay.png")  # <--- baru
arrow_image_b64 = get_base64_image("arrow_overlay.png")  # <--- baru

# --- UI ---
kolom1, kolom2, kolom3 = st.columns([1,2,1])
with kolom2:
    jenis_hadiah = st.selectbox("Pilih Jenis Hadiah:", options=list(pemenang.keys()), key="dropdown")
    
    if st.button("Mulai Mengundi", use_container_width=True, key="start_button"):
        st.session_state.anim_mode = 'kombinasi'
        st.session_state.start_combo_anim = True
        st.session_state.show_winner_list = False
        
# --- Session State defaults ---
if 'anim_mode' not in st.session_state: st.session_state.anim_mode = None
if 'start_combo_anim' not in st.session_state: st.session_state.start_combo_anim = False
if 'show_winner_list' not in st.session_state: st.session_state.show_winner_list = False
if 'previous_jenis_hadiah' not in st.session_state: st.session_state.previous_jenis_hadiah = jenis_hadiah

# Reset bila ganti jenis hadiah
if st.session_state.previous_jenis_hadiah != jenis_hadiah:
    st.session_state.anim_mode = None
    st.session_state.start_combo_anim = False
    st.session_state.show_winner_list = False
    st.session_state.previous_jenis_hadiah = jenis_hadiah

st.markdown("<hr>", unsafe_allow_html=True)

# --- Helper untuk teks pemenang ---
def build_winner_html_list(df):
    names = [f"<strong>{row['Nama']}</strong> <br>({row['Branch']})<br><br><strong>Perolehan Poin :</strong> <br>({row['Point']} Point)<br><br><strong>Persentase Menang : </strong>({row['Probability']*100:.5f}%) " for _, row in df.iterrows()]
    return "<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:10px;text-align:center;'>" + \
           "".join([f"<div style='font-size:20px'><br>{n}</div>" for n in names]) + "</div>"

# --- SLOT & KOMBINASI LOGIC ---
def generate_slot_data(df_winner, semua_peserta, gimmick_only=False):
    if gimmick_only:
        slot_names_data = []
        for i in range(3):
            shuffled = random.sample(semua_peserta, len(semua_peserta))
            slot_list = shuffled * 5
            slot_names_data.append(slot_list)
        return slot_names_data
    else:
        slot_names_data = []
        for i in range(len(df_winner)):
            shuffled = random.sample(semua_peserta, len(semua_peserta))
            slot_list = shuffled * 5
            if df_winner.iloc[i]['Nama'] not in slot_list:
                slot_list.append(df_winner.iloc[i]['Nama'])
            slot_names_data.append(slot_list)
        return slot_names_data

# --- IDLE SLOT ---
if st.session_state.anim_mode is None:
    semua_peserta = df_backup["Nama"].tolist()
    slot_names_data = generate_slot_data(df_backup, semua_peserta, gimmick_only=True)

    js_code_idle = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body, html {{ margin:0; padding:0; height:720px; overflow:hidden; }}
            
            .slot-container {{ display:flex; gap:20px; justify-content:center; align-items:center; position:absolute; top:50%; left:50%; transform: translate(-50%, -50%); }}
            .slot {{ position: relative; width:240px; height:180px; overflow:hidden; border:2px solid #ccc; border-radius:10px; background-color:WHITE; }}
            .reel-idle {{ animation: scroll 20000s linear infinite; }}
            @keyframes scroll {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-50%); }}}}
            .name {{ height:60px; line-height:60px; text-align:center; width:100%; font-size:18px; color:BLACK; }}

            /* Overlay di atas slot */
            #overlay {{ position:absolute; top:0; left:0; width:100%; height:100%; z-index:0; background-image:url("data:image/png;base64,{overlay_image_b64}"); background-size:cover; background-position:center; pointer-events:none; }}
            #arrow {{ position:absolute; top:0; left:0; width:100%; height:100%; z-index:2; background-image:url("data:image/png;base64,{arrow_image_b64}"); background-size:cover; background-position:center; pointer-events:none; }}

            /* Slot selang-seling */
            .slot:nth-child(odd) .reel-idle {{ animation-direction: normal; }}
            .slot:nth-child(even) .reel-idle {{ animation-direction: reverse; }}
        </style>
    </head>
    <body>
        <div id="arrow"></div>
        <div id="overlay"></div>
        <div class="slot-container" id="slot-container"></div>
        <script>
            const slotNamesData = {json.dumps(slot_names_data)};
            const container = document.getElementById('slot-container');

            slotNamesData.forEach(names => {{
                const slotDiv = document.createElement('div');
                slotDiv.className = 'slot';
                const reelDiv = document.createElement('div');
                reelDiv.className = 'reel-idle';
                names.forEach(name => {{
                    const d = document.createElement('div');
                    d.className = 'name';
                    d.textContent = name;
                    reelDiv.appendChild(d);
                }});
                slotDiv.appendChild(reelDiv);
                container.appendChild(slotDiv);
            }});
        </script>
    </body>
    </html>
    """
    components.html(js_code_idle, height=720, width=1400, scrolling=False)

# --- MODE KOMBINASI ---
if st.session_state.anim_mode == 'kombinasi':
    df_pemenang = pemenang[jenis_hadiah]
    if df_pemenang is None or len(df_pemenang) == 0:
        st.warning(f"Tidak ada data pemenang untuk kategori {jenis_hadiah}.")
    else:
        semua_peserta = df_backup["Nama"].tolist()
        gimmick_mode = jenis_hadiah in ["Hadiah Ketiga", "Hadiah Keempat", "Hadiah Cabang"]
        slot_names_data = generate_slot_data(df_pemenang, semua_peserta, gimmick_only=gimmick_mode)
        pemenang_html_grid = build_winner_html_list(df_pemenang)

        # --- JS animasi slot ---
        D_SLOT_MS   = 7000
        T_ENVELOPE  = 4000
        ENVELOPE_UP = 1400
        LETTER_LEFT = 1200
        GAP_AFTER_LEFT = 150
        LETTER_UP   = 800
        TEXT_UP     = 800

        js_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body, html {{ margin:0; padding:0; height:720px; overflow:hidden; }}
                .slot-container {{ display:flex; gap:20px; justify-content:center; align-items:center; position:absolute; top:50%; left:50%; transform: translate(-50%, -50%); z-index:1; }}
                .slot {{ position: relative; width:240px; height:180px; overflow:hidden; border:2px solid #ccc; border-radius:10px; background-color:WHITE; }}
                .reel {{ position:absolute; top:0; left:0; width:100%; transition: transform 7s cubic-bezier(0.175,0.885,0.32,1.275); }}
                .reel-idle {{ animation: scroll 10s linear infinite; }}
                @keyframes scroll {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-50%); }}}}
                .name {{ height:60px; line-height:60px; text-align:center; width:100%; font-size:18px; color:BLACK; }}

                /* Overlay di atas slot */
                #overlay {{ position:absolute; top:0; left:0; width:100%; height:100%; z-index:0; background-image:url("data:image/png;base64,{overlay_image_b64}"); background-size:cover; background-position:center; pointer-events:none; }}
                #arrow {{ position:absolute; top:0; left:0; width:100%; height:100%; z-index:2; background-image:url("data:image/png;base64,{arrow_image_b64}"); background-size:cover; background-position:center; pointer-events:none; }}

                #amplop {{ position:absolute; left:50%; transform:translateX(-660px); bottom:-900px; z-index:3; width:1300px; transition:bottom 1.4s ease-in-out; }}
                #surat {{ position:absolute; left:50%; transform:translateX(-50%); bottom:100px; width:clamp(735px,78.75vw,1575px); z-index:2; opacity:0; transition: transform 1.2s ease-in-out, opacity 0.4s ease-in; }}
                #nama-pemenang {{ color:black; font-size:22px; position:absolute; left:370px; bottom:170px; z-index:6; opacity:0; text-align:center; max-width:600px; }}
            </style>
        </head>
        <body>
            <div id="arrow"></div>
            <div id="overlay"></div>
            <div class="slot-container" id="slot-container"></div>
            <img id="amplop" src="data:image/png;base64,{amplop_image_b64}" />
            <img id="surat" src="data:image/png;base64,{surat_image_b64}" />
            <div id="nama-pemenang"></div>
            <script>
                const slotNamesData = {json.dumps(slot_names_data)};
                const winners       = {json.dumps(df_pemenang["Nama"].tolist())};
                const jenisHadiah   = {json.dumps(jenis_hadiah)};
                const pemenangHTML  = {json.dumps(pemenang_html_grid)};
                const container     = document.getElementById('slot-container');
                const amplopEl      = document.getElementById('amplop');
                const suratEl       = document.getElementById('surat');
                const namaEl        = document.getElementById('nama-pemenang');

                slotNamesData.forEach((names, i) => {{
                    const slotDiv = document.createElement('div');
                    slotDiv.className = 'slot';
                    const reelDiv = document.createElement('div');
                    reelDiv.className = 'reel';
                    names.forEach(name => {{
                        const d = document.createElement('div');
                        d.className = 'name';
                        d.textContent = name;
                        reelDiv.appendChild(d);
                    }});
                    slotDiv.appendChild(reelDiv);
                    container.appendChild(slotDiv);

                    const itemH   = 60;
                    const slotH   = 180;
                    const center  = (slotH / 2) - (itemH / 2);
                    const idxWin  = names.indexOf(winners[i] || names[0]);
                    const stopPos = -(idxWin * itemH) + center;

                    setTimeout(() => {{ reelDiv.style.transform = `translateY(${{stopPos}}px)`; }}, 200 + i*220);
                }});

                setTimeout(() => {{ amplopEl.style.bottom = "50px"; }}, {T_ENVELOPE});
                setTimeout(() => {{ suratEl.style.opacity = 1; suratEl.style.transform = "translateX(-200%)"; }}, {T_ENVELOPE + ENVELOPE_UP});
                setTimeout(() => {{
                    suratEl.style.transition = "none";
                    suratEl.style.opacity = 0;
                    suratEl.style.transform = "translateX(-530px)";
                    suratEl.style.bottom = "-600px";
                    suratEl.offsetHeight;
                    suratEl.style.transition = "bottom {LETTER_UP/1000:.3f}s ease, opacity {LETTER_UP/1000:.3f}s ease";
                    suratEl.style.bottom = "20px"; suratEl.style.opacity = 1; suratEl.style.zIndex=4;
                }}, {T_ENVELOPE + ENVELOPE_UP + LETTER_LEFT + GAP_AFTER_LEFT});

                setTimeout(() => {{
                    if (["Hadiah Ketiga","Hadiah Keempat","Hadiah Cabang"].includes(jenisHadiah)) {{
                        namaEl.innerHTML = `
                        <div style="margin-left: 100px;margin-top: 200px; display:flex; flex-direction:column; justify-content:center; align-items:center; height:100%; text-align:center;">
                            <div style="font-size:26px;margin-bottom:8px"><strong>🎉 CONGRATULATIONS 🎉</strong></div>
                            <div style="font-size:22px"><br>Selamat kepada nama-nama di bawah ini</div>
                            <div class="jenis-kemenangan" style="font-size:20px"><br><br>Sebagai pemenang <b>${{jenisHadiah}}</b><br><br><br><br><br></div>
                        </div>`;
                    }} else {{
                        namaEl.innerHTML = `<div style="font-size:26px;margin-bottom:8px"><strong>🎉 CONGRATULATIONS 🎉</strong></div>` + pemenangHTML + `<div class="jenis-kemenangan" style="font-size:20px"><br><br>Sebagai pemenang <b>${{jenisHadiah}}</b></div>`;
                    }}
                    namaEl.style.transition = "bottom {TEXT_UP/1000:.3f}s ease, opacity {TEXT_UP/1000:.3f}s ease";
                    namaEl.style.opacity = 1;
                }}, {T_ENVELOPE + ENVELOPE_UP + LETTER_LEFT + GAP_AFTER_LEFT + LETTER_UP});
            </script>
        </body>
        </html>
        """
        components.html(js_code, height=720, width=1400, scrolling=False)
        time.sleep(8)
        st.balloons()

        if gimmick_mode:
            st.session_state.show_winner_list = True

# --- Daftar Pemenang ---
if st.session_state.show_winner_list:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader(f"Daftar Pemenang: {jenis_hadiah}")

    # --- CSS Background untuk tabel dan kolom ---
    st.markdown(
        f"""
        <style>
        /* Background untuk st.table() / st.dataframe() */
        div.stTable {{
            background-color: #0e1117;
            background-size: cover;
            background-repeat: no-repeat;
            border-radius: 10px;
        }}

        /* Background untuk kolom nama jika pemenang < 15 */
        div.stColumns > div {{
            background-color: #0e1117;
            background-size: cover;
            background-repeat: no-repeat;
            padding: 10px;
            border-radius: 8px;
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    winners_df = pemenang[jenis_hadiah]
    winners_df['Probability'] = winners_df['Probability'].apply(lambda x: f"{x*100:.5f}%")
    if winners_df is not None and not winners_df.empty:
        if jenis_hadiah == "Hadiah Cabang":
            branch_groups = winners_df.groupby('Branch')
            for branch, group in branch_groups:
                with st.expander(f"Cabang {branch} ({len(group)} pemenang)"):
                    st.table(group[['Nama', 'Branch', 'Point','Probability']])
        else:
            if len(winners_df) > 15:
                st.table(winners_df[['Nama', 'Branch', 'Point', 'Probability']])
            else:
                cols = st.columns(3)
                for idx, (_, row) in enumerate(winners_df.iterrows()):
                    cols[idx % 3].write(f"• {row['Nama']} - ({row['Branch']}) - {row['Point']} Point - {row['Probability']}")
    else:
        st.info("Tidak ada pemenang untuk kategori ini.")
