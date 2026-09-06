import os
import random
import base64
import streamlit as st

st.set_page_config(page_title="Auto Bingo", page_icon="🚗", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding: 0.5rem 0.2rem 2rem 0.2rem !important;}
    div[data-testid="stButton"] button {
        width: 100%;
        border-radius: 8px;
        height: 100px;
        padding: 0px;
        background-color: white;
        border: 1px solid rgba(0,0,0,0.1);
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    div[data-testid="stButton"] button img {
        object-fit: contain;
        height: 90px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

IMAGE_DIR = "images"
REQUIRED_IMAGES = 25
RENDER_APP_URL = "https://car-bingo.onrender.com"

all_images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))] if os.path.exists(IMAGE_DIR) else []

if "game_id" not in st.session_state:
    st.session_state["game_id"] = 1
if "board_images" not in st.session_state:
    st.session_state["board_images"] = []
if "checked" not in st.session_state:
    st.session_state["checked"] = [False] * REQUIRED_IMAGES

def init_board():
    if len(all_images) >= REQUIRED_IMAGES:
        st.session_state["board_images"] = random.sample(all_images, REQUIRED_IMAGES)
        st.session_state["checked"] = [False] * REQUIRED_IMAGES

if not st.session_state["board_images"] or len(st.session_state["board_images"]) != REQUIRED_IMAGES:
    init_board()

st.markdown("<h3 style='text-align: center; margin: 0 0 10px 0;'>🚗 Auto Bingo</h3>", unsafe_allow_html=True)

if st.button("🚀 Nowa plansza / Reset", use_container_width=True, type="primary"):
    init_board()
    st.rerun()

st.write("")

if len(all_images) < REQUIRED_IMAGES:
    st.error(f"W folderze 'images' jest tylko {len(all_images)} grafik. Wymagane min. 25 unikalnych obrazków!")
else:
    # Wzorce wygranej dla siatki 5x5
    win_patterns = []
    for r in range(5):
        win_patterns.append([r * 5 + c for c in range(5)])  # rzędy
        win_patterns.append([c * 5 + r for c in range(5)])  # kolumny
    win_patterns.append([0, 6, 12, 18, 24])  # przekątna 1
    win_patterns.append([4, 8, 12, 16, 20])  # przekątna 2

    # Sprawdzenie wygranej
    is_win = any(all(st.session_state["checked"][idx] for idx in pattern) for pattern in win_patterns)

    # Wyświetlanie siatki 5x5 przy użyciu natywnych kolumn i przycisków Streamlita
    for r in range(5):
        cols = st.columns(5)
        for c in range(5):
            idx = r * 5 + c
            img_name = st.session_state["board_images"][idx]
            img_path = os.path.join(IMAGE_DIR, img_name)
            
            with open(img_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            
            is_checked = st.session_state["checked"][idx]
            
            # Stylizacja przycisku w zależności od zaznaczenia
            with cols[c]:
                if is_checked:
                    btn_label = f"❌\n(Zaznaczone)"
                    if st.button(f"❌ {idx}", key=f"tile_{idx}", use_container_width=True):
                        st.session_state["checked"][idx] = False
                        st.rerun()
                else:
                    # Ładowanie obrazka do przycisku
                    img_html = f'<img src="data:image/jpeg;base64,{b64}">'
                    if st.button(img_name, key=f"tile_{idx}", use_container_width=True, help="Kliknij, aby zaznaczyć"):
                        st.session_state["checked"][idx] = True
                        st.rerun()

    if is_win:
        st.success("🎉 BINGO! Wygrałem, leszcze! 🎉")
        st.balloons()
        st.markdown("""
            <script>
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                    const msg = new SpeechSynthesisUtterance("BINGO! Wygrałem, leszcze!");
                    msg.lang = 'pl-PL'; msg.pitch = 1.1;
                    window.speechSynthesis.speak(msg);
                }
            </script>
        """, unsafe_allow_html=True)

    # Kod QR ukryty pod planszą (wymaga przewinięcia)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={RENDER_APP_URL}"
    st.markdown(f"""
        <div style="margin-top: 250px; padding: 20px; text-align: center; background: rgba(255,255,255,0.05); border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); color: #fff;">
            <h4 style="margin:0 0 5px 0;">Zeskanuj, aby grać na swoim telefonie</h4>
            <img src="{qr_url}" style="width: 200px; height: 200px; border-radius: 8px; background: #fff; padding: 8px; margin-top: 10px;">
        </div>
    """, unsafe_allow_html=True)
