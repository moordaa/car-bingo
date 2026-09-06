import os
import random
import base64
import streamlit as st

# Config strony
st.set_page_config(
    page_title="Auto Bingo",
    page_icon="🚗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Ukrycie domyślnych elementów Streamlita i stylizacja
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
    }
    
    /* Kompaktowa siatka 5x5 mieszcząca się w całości na ekranie */
    .bingo-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 4px;
        width: 100%;
        max-width: 480px;
        margin: auto;
    }
    .bingo-card {
        position: relative;
        width: 100%;
        padding-top: 85%; /* Zmniejszona wysokość kafelka */
        border-radius: 6px;
        overflow: hidden;
        background-color: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        cursor: pointer;
        user-select: none;
    }
    .bingo-card img {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: contain; /* Pomniejszenie obrazka do kafelka */
        padding: 2px;
        box-sizing: border-box;
        transition: filter 0.2s;
    }
    .bingo-card.checked img {
        filter: grayscale(80%) brightness(30%);
    }
    .bingo-card.checked::after {
        content: "❌";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 1.8rem;
        pointer-events: none;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

IMAGE_DIR = "images"
REQUIRED_IMAGES = 25  # Na stałe 5x5
RENDER_APP_URL = "https://car-bingo.onrender.com"

# Wczytanie listy plików
if os.path.exists(IMAGE_DIR):
    all_images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))]
else:
    all_images = []

if "game_id" not in st.session_state:
    st.session_state["game_id"] = 1

def generate_encoded_images():
    if not all_images:
        return []

    # Generowanie dokładnie 25 elementów (z powtórzeniami, jeśli plików jest mniej niż 25)
    selected_imgs = [random.choice(all_images) for _ in range(REQUIRED_IMAGES)]

    encoded_list = []
    for img_name in selected_imgs:
        img_path = os.path.join(IMAGE_DIR, img_name)
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            encoded_list.append(f"data:image/jpeg;base64,{encoded}")
    return encoded_list

if "my_encoded_images" not in st.session_state or len(st.session_state["my_encoded_images"]) != REQUIRED_IMAGES:
    st.session_state["my_encoded_images"] = generate_encoded_images()

# --- INTERFEJS APLIKACJI ---

st.markdown("<h3 style='text-align: center; margin-top: 0; margin-bottom: 5px;'>🚗 Auto Bingo</h3>", unsafe_allow_html=True)

# Przyciski sterujące pod nazwą gry
col1, col2 = st.columns(2)
with col1:
    show_qr = st.button("📲 Kod QR", use_container_width=True, type="secondary")

with col2:
    if st.button("🚀 Reset / Nowa plansza", use_container_width=True, type="primary"):
        st.session_state["game_id"] += 1
        st.session_state["my_encoded_images"] = generate_encoded_images()
        st.rerun()

# Pełnoekranowy kod QR
if show_qr:
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={RENDER_APP_URL}"
    st.markdown(f"""
        <div style="
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background-color: rgba(0, 0, 0, 0.9);
            z-index: 999999;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
        ">
            <h2 style="margin-bottom: 20px;">Zeskanuj, aby dołączyć</h2>
            <img src="{qr_code_url}" style="width: 250px; height: 250px; border-radius: 12px; background: white; padding: 10px;">
        </div>
    """, unsafe_allow_html=True)
    if st.button("❌ Zamknij Kod QR", type="primary", use_container_width=True):
        st.rerun()

if len(all_images) == 0:
    st.warning("Brak grafik w folderze 'images'. Dodaj pliki do repozytorium, aby rozpocząć grę.")
else:
    encoded_images = st.session_state["my_encoded_images"]
    
    html_code = f"""
    <div class="bingo-container" id="bingoGrid">
        {"".join([f'<div class="bingo-card" data-idx="{i}" onclick="toggleCard(this)"><img src="{img_url}"></div>' for i, img_url in enumerate(encoded_images)])}
    </div>

    <div id="winBanner" style="display: none; background-color: #28a745; color: white; padding: 10px; border-radius: 8px; text-align: center; margin-top: 10px;">
        <h3 style="margin:0;">🎉 BINGO! WYGRAŁEM! 🎉</h3>
    </div>

    <script>
        const gameId = {st.session_state['game_id']};

        if (localStorage.getItem('current_game_id') != gameId) {{
            localStorage.setItem('current_game_id', gameId);
            localStorage.removeItem('bingo_checked_state');
        }}

        window.onload = function() {{
            const savedState = JSON.parse(localStorage.getItem('bingo_checked_state') || '[]');
            const cards = document.querySelectorAll('.bingo-card');
            cards.forEach((card, idx) => {{
                if (savedState[idx]) {{
                    card.classList.add('checked');
                }}
            }});
            checkBingo(false);
        }};

        function saveState() {{
            const cards = document.querySelectorAll('.bingo-card');
            const state = Array.from(cards).map(card => card.classList.contains('checked'));
            localStorage.setItem('bingo_checked_state', JSON.stringify(state));
        }}

        function generateWinPatterns() {{
            const size = 5;
            const patterns = [];
            for (let r = 0; r < size; r++) {{
                const row = [];
                for (let c = 0; c < size; c++) row.push(r * size + c);
                patterns.push(row);
            }}
            for (let c = 0; c < size; c++) {{
                const col = [];
                for (let r = 0; r < size; r++) col.push(r * size + c);
                patterns.push(col);
            }}
            const diag1 = [], diag2 = [];
            for (let i = 0; i < size; i++) {{
                diag1.push(i * size + i);
                diag2.push(i * size + (size - 1 - i));
            }}
            patterns.push(diag1, diag2);
            return patterns;
        }}

        const winPatterns = generateWinPatterns();

        function playVictorySound() {{
            try {{
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                const ctx = new AudioContext();
                const notes = [261.63, 329.63, 392.00, 523.25];
                notes.forEach((freq, index) => {{
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = 'triangle';
                    osc.frequency.value = freq;
                    gain.gain.setValueAtTime(0.3, ctx.currentTime + index * 0.12);
                    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + index * 0.12 + 0.3);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(ctx.currentTime + index * 0.12);
                    osc.stop(ctx.currentTime + index * 0.12 + 0.3);
                }});
            }} catch(e) {{}}
        }}

        function checkBingo(playSound = true) {{
            const cards = document.querySelectorAll('.bingo-card');
            const checked = Array.from(cards).map(card => card.classList.contains('checked'));

            let isWin = winPatterns.some(pattern => pattern.every(index => checked[index]));
            const banner = document.getElementById('winBanner');

            if (isWin) {{
                if (banner.style.display === 'none' && playSound) {{
                    playVictorySound();
                }}
                banner.style.display = 'block';
            }} else {{
                banner.style.display = 'none';
            }}
        }}

        function toggleCard(card) {{
            card.classList.toggle('checked');
            saveState();
            checkBingo(true);
        }}
    </script>
    """

    st.components.v1.html(html_code, height=620, scrolling=False)
