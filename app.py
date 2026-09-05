import streamlit as st
import os
import random
import base64
import qrcode
from io import BytesIO

# Ustawienie "centered" dla schludnego wyglądu mobilnego
st.set_page_config(page_title="Auto Bingo", layout="centered")

# Minimalistyczny styl, usunięcie górnych marginesów
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Stały adres aplikacji na Render.com
RENDER_APP_URL = "https://car-bingo.onrender.com"

# Wspólna, globalna pamięć gry
@st.cache_resource
def get_game_state():
    return {
        "grid_size": 3,
        "winner": None,
        "ended": False,
        "game_id": 1,
        "master_session": None,
        "bingo_grid": [],
        "encoded_images": [],
        "last_game_id": 0
    }

game_state = get_game_state()
IMAGE_DIR = "images"

if os.path.exists(IMAGE_DIR):
    all_images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
else:
    all_images = []

# Unikalne ID dla każdego telefonu
if "my_session_id" not in st.session_state:
    st.session_state["my_session_id"] = str(random.randint(100000, 999999))

if "player_name" not in st.session_state:
    st.session_state["player_name"] = "Pasażer 1"

# Błyskawiczne generowanie i keszowanie planszy
grid_size = game_state["grid_size"]
required_images = grid_size * grid_size

if game_state["last_game_id"] != game_state["game_id"] or len(game_state["encoded_images"]) != required_images:
    if len(all_images) >= required_images:
        selected_imgs = random.sample(all_images, required_images)
        encoded_list = []
        for img_name in selected_imgs:
            img_path = os.path.join(IMAGE_DIR, img_name)
            with open(img_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
                encoded_list.append(f"data:image/jpeg;base64,{encoded}")
        game_state["bingo_grid"] = selected_imgs
        game_state["encoded_images"] = encoded_list
        game_state["last_game_id"] = game_state["game_id"]

# Tytuł
st.markdown("<h2 style='text-align: center; margin-top: 0; padding-top: 0;'>🚗 Auto Bingo</h2>", unsafe_allow_html=True)

is_current_master = (game_state["master_session"] == st.session_state["my_session_id"])

# --- 1. KOD QR ---
with st.expander("📲 Pokaż kod QR do gry", expanded=False):
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    qr = qrcode.QRCode(version=1, box_size=6, border=1)
    qr.add_data(RENDER_APP_URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf)
    st.image(buf.getvalue(), width=160)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 2. PANEL LIDERA ---
if game_state["master_session"] is None:
    if st.button("👑 Zostań Liderem gry", use_container_width=True, type="primary"):
        game_state["master_session"] = st.session_state["my_session_id"]
        st.rerun()
elif is_current_master:
    st.markdown("""
        <div style="background-color: #e6f7ff; padding: 15px; border-radius: 10px; border: 1px solid #91d5ff; margin-bottom: 15px;">
            <h4 style="margin-top: 0; color: #0050b3; text-align: center;">👑 Jesteś Liderem</h4>
    """, unsafe_allow_html=True)
    
    idx = 0
    if game_state["grid_size"] == 4: idx = 1
    elif game_state["grid_size"] == 5: idx = 2
    
    grid_choice = st.selectbox("Rozmiar planszy:", ["3x3 (9 zdjęć)", "4x4 (16 zdjęć)", "5x5 (25 zdjęć)"], index=idx)
    new_size = int(grid_choice.split("x")[0])
    
    col_reset, col_giveup = st.columns(2)
    with col_reset:
        if st.button("🚀 Rozdaj od nowa", use_container_width=True, type="primary"):
            game_state["grid_size"] = new_size
            game_state["winner"] = None
            game_state["ended"] = False
            game_state["game_id"] += 1
            st.rerun()
    with col_giveup:
        if st.button("❌ Oddaj Lidera", use_container_width=True):
            game_state["master_session"] = None
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("⚠️ Inny gracz dowodzi teraz grą.")
    if st.button("Przejmij Lidera", use_container_width=True):
        game_state["master_session"] = st.session_state["my_session_id"]
        st.rerun()

# --- 3. POLE NA IMIĘ ---
player_name = st.text_input("Twoje Imię / Nick:", value=st.session_state["player_name"]).strip()
st.session_state["player_name"] = player_name
st.write("") 

# Przycisk ręcznego odświeżenia stanu (gdy gracz chce sprawdzić, czy ktoś wygrał lub zmieniła się plansza)
col_sync1, col_sync2 = st.columns([3, 1])
with col_sync2:
    if st.button("🔄 Odśwież", use_container_width=True):
        st.rerun()

# --- 4. GŁÓWNY EKRAN GRY / WYNIKÓW ---
if game_state["ended"]:
    st.markdown(f"""
        <div style="background-color: #28a745; color: white; padding: 20px; border-radius: 12px; text-align: center; margin-top: 20px;">
            <h1 style="margin:0; font-size: 2.5rem;">🎉 BINGO! 🎉</h1>
            <h3 style="margin:10px 0 0 0;">Zwycięża: <strong>{game_state['winner']}</strong></h3>
        </div>
        
        <script>
            if (!window.hasPlayedWinSpeech && 'speechSynthesis' in window) {{
                window.hasPlayedWinSpeech = true;
                const msg = new SpeechSynthesisUtterance('Bingo! Zwyciężył gracz {game_state["winner"]}!');
                msg.lang = 'pl-PL';
                window.speechSynthesis.speak(msg);
            }}
        </script>
    """, unsafe_allow_html=True)
    
    if is_current_master:
        st.write("")
        if st.button("🚀 Grajcie dalej (Nowe rozdanie)", use_container_width=True, type="primary"):
            game_state["winner"] = None
            game_state["ended"] = False
            game_state["game_id"] += 1
            st.rerun()
    else:
        st.info("Czekamy na Lidera, aż rozpocznie nową rundę...")
        
else:
    if len(all_images) < required_images:
        st.warning(f"Za mało zdjęć! Masz {len(all_images)}, a potrzebujesz min. {required_images}!")
    else:
        html_height = 800 if grid_size == 3 else (1000 if grid_size == 4 else 1200)
        encoded_images = game_state["encoded_images"]

        html_code = f"""
        <style>
            .bingo-container {{
                display: grid;
                grid-template-columns: repeat({grid_size}, 1fr);
                gap: 6px;
                width: 100%;
                max-width: 600px;
                margin: auto;
            }}
            .bingo-card {{
                position: relative;
                width: 100%;
                padding-top: 100%;
                border-radius: {8 if grid_size > 3 else 12}px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                cursor: pointer;
                user-select: none;
            }}
            .bingo-card img {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: filter 0.2s;
            }}
            .bingo-card.checked img {{
                filter: grayscale(80%) brightness(40%);
            }}
            .bingo-card.checked::after {{
                content: "❌";
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: {2.2 if grid_size == 5 else (2.8 if grid_size == 4 else 3.5)}rem;
                pointer-events: none;
            }}
        </style>

        <div class="bingo-container">
            {"".join([f'<div class="bingo-card" data-idx="{i}" onclick="toggleCard(this)"><img src="{img_url}"></div>' for i, img_url in enumerate(encoded_images)])}
        </div>

        <script>
            let hasWon = false;
            const gridSize = {grid_size};
            const playerName = "{player_name}";

            window.onload = function() {{
                const buttons = window.parent.document.querySelectorAll('button');
                buttons.forEach(btn => {{
                    if (btn.innerText.includes('SYSTEM_WIN_BRIDGE')) {{
                        const container = btn.closest('div[data-testid="stButton"]');
                        if (container) container.style.display = 'none';
                    }}
                }});
            }}

            function generateWinPatterns(size) {{
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
                const diag1 = [];
                for (let i = 0; i < size; i++) diag1.push(i * size + i);
                patterns.push(diag1);

                const diag2 = [];
                for (let i = 0; i < size; i++) diag2.push(i * size + (size - 1 - i));
                patterns.push(diag2);
                return patterns;
            }}

            const winPatterns = generateWinPatterns(gridSize);

            function triggerWinEvent() {{
                const buttons = window.parent.document.querySelectorAll('button');
                buttons.forEach(btn => {{
                    if (btn.innerText.includes('SYSTEM_WIN_BRIDGE')) {{
                        btn.click();
                    }}
                }});
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

            function checkBingo() {{
                const cards = document.querySelectorAll('.bingo-card');
                const checked = Array.from(cards).map(card => card.classList.contains('checked'));

                let isWin = false;
                for (let pattern of winPatterns) {{
                    if (pattern.every(index => checked[index])) {{
                        isWin = true;
                        break;
                    }}
                }}

                if (isWin && !hasWon) {{
                    hasWon = true;
                    playVictorySound();
                    triggerWinEvent();
                }}
            }}

            function toggleCard(card) {{
                card.classList.toggle('checked');
                checkBingo();
            }}
        </script>
        """

        st.components.v1.html(html_code, height=html_height, scrolling=False)

        if st.button("SYSTEM_WIN_BRIDGE", key="win_bridge"):
            game_state["ended"] = True
            game_state["winner"] = player_name
            st.rerun()
