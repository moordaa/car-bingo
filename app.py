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

# Ukrycie domyślnych elementów Streamlita
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

# Przyciski sterujące
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
        <button onclick="document.getElementById('qrModalOverlay').style.display='flex'" 
                style="width: 100%; padding: 0.5rem; border-radius: 8px; border: 1px solid #4a4a4a; background-color: #262730; color: white; cursor: pointer; font-weight: bold;">
            📲 Kod QR
        </button>
    """, unsafe_allow_html=True)

with col2:
    if st.button("🚀 Reset / Nowa plansza", use_container_width=True, type="primary"):
        st.session_state["game_id"] += 1
        st.session_state["my_encoded_images"] = generate_encoded_images()
        st.rerun()

# Pełnoekranowy kod QR (sam w sobie jest przyciskiem do zamykania)
qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={RENDER_APP_URL}"
st.markdown(f"""
    <div id="qrModalOverlay" onclick="this.style.display='none'" style="
        display: none;
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: rgba(0, 0, 0, 0.92);
        z-index: 999999;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        cursor: pointer;
    ">
        <h2 style="margin-bottom: 15px; pointer-events: none;">Zeskanuj, aby dołączyć</h2>
        <img src="{qr_code_url}" style="width: 260px; height: 260px; border-radius: 12px; background: white; padding: 10px; pointer-events: none;">
        <p style="margin-top: 15px; font-size: 0.85rem; color: #aaa; pointer-events: none;">Dotknij w dowolnym miejscu, aby zamknąć</p>
    </div>
""", unsafe_allow_html=True)

if len(all_images) == 0:
    st.warning("Brak grafik w folderze 'images'. Dodaj pliki do repozytorium, aby rozpocząć grę.")
else:
    encoded_images = st.session_state["my_encoded_images"]
    
    html_code = f"""
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: transparent;
        }}
        .bingo-container {{
            display: grid !important;
            grid-template-columns: repeat(5, 1fr) !important;
            gap: 4px !important;
            width: 100% !important;
            max-width: 480px !important;
            margin: auto !important;
        }}
        .bingo-card {{
            position: relative !important;
            width: 100% !important;
            padding-top: 100% !important;
            border-radius: 6px !important;
            overflow: hidden !important;
            background-color: #ffffff !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
            cursor: pointer !important;
            user-select: none !important;
            box-sizing: border-box !important;
        }}
        .bingo-card img {{
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            object-fit: contain !important;
            padding: 3px !important;
            box-sizing: border-box !important;
            transition: filter 0.2s !important;
        }}
        .bingo-card.checked img {{
            filter: grayscale(80%) brightness(30%) !important;
        }}
        .bingo-card.checked::after {{
            content: "❌" !important;
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            font-size: 1.8rem !important;
            pointer-events: none !important;
        }}
    </style>

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

    st.components.v1.html(html_code, height=520, scrolling=False)
