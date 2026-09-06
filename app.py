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
        padding-bottom: 2rem !important;
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

IMAGE_DIR = "images"
REQUIRED_IMAGES = 25  # Wymagane 25 unikalnych obrazków dla siatki 5x5
RENDER_APP_URL = "https://car-bingo.onrender.com"

# Wczytanie listy plików
if os.path.exists(IMAGE_DIR):
    all_images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))]
else:
    all_images = []

if "game_id" not in st.session_state:
    st.session_state["game_id"] = 1

def generate_encoded_images():
    if len(all_images) < REQUIRED_IMAGES:
        return []

    selected_imgs = random.sample(all_images, REQUIRED_IMAGES)

    encoded_list = []
    for img_name in selected_imgs:
        img_path = os.path.join(IMAGE_DIR, img_name)
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            encoded_list.append(f"data:image/jpeg;base64,{encoded}")
    return encoded_list

if "my_encoded_images" not in st.session_state:
    st.session_state["my_encoded_images"] = generate_encoded_images()

# --- INTERFEJS APLIKACJI ---

st.markdown("<h3 style='text-align: center; margin-top: 0; margin-bottom: 10px;'>🚗 Auto Bingo</h3>", unsafe_allow_html=True)

# Przycisk resetu/nowej planszy
if st.button("🚀 Nowa plansza / Reset", use_container_width=True, type="primary"):
    st.session_state["game_id"] += 1
    st.session_state["my_encoded_images"] = generate_encoded_images()
    st.rerun()

st.write("")

if len(all_images) < REQUIRED_IMAGES:
    st.error(f"W folderze 'images' znajduje się **{len(all_images)}** grafik. Wymagane jest minimum **25 unikalnych obrazków**, aby uruchomić planszę 5x5 bez powtórzeń.")
else:
    encoded_images = st.session_state["my_encoded_images"]
    if not encoded_images:
        encoded_images = generate_encoded_images()
        st.session_state["my_encoded_images"] = encoded_images

    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={RENDER_APP_URL}"

    html_code = f"""
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: transparent;
            font-family: sans-serif;
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
        .qr-section {{
            margin-top: 250px; /* Duży odstęp wymuszający zeskrolowanie */
            padding: 20px;
            text-align: center;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
        }}
        .qr-section img {{
            width: 200px;
            height: 200px;
            border-radius: 8px;
            background: white;
            padding: 8px;
            margin-top: 10px;
        }}
    </style>

    <div class="bingo-container" id="bingoGrid">
        {"".join([f'<div class="bingo-card" data-idx="{i}" onclick="toggleCard(this)"><img src="{img_url}"></div>' for i, img_url in enumerate(encoded_images)])}
    </div>

    <div id="winBanner" style="display: none; background-color: #28a745; color: white; padding: 10px; border-radius: 8px; text-align: center; margin-top: 15px;">
        <h3 style="margin:0;">🎉 BINGO! WYGRAŁEM! 🎉</h3>
    </div>

    <!-- Kod QR daleko pod planszą -->
    <div class="qr-section">
        <h4 style="margin: 0 0 5px 0;">Zeskanuj, aby grać na swoim telefonie</h4>
        <img src="{qr_code_url}" alt="Kod QR Dołączenia">
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

        function speakWin() {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                const msg = new SpeechSynthesisUtterance("BINGO! WYGRAŁEM!");
                msg.lang = 'pl-PL';
                msg.rate = 1.0;
                msg.pitch = 1.1;
                window.speechSynthesis.speak(msg);
            }}
        }}

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
                    speakWin();
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

    st.components.v1.html(html_code, height=1050, scrolling=True)
