import streamlit as st
import os
import random
import base64
import qrcode
from io import BytesIO
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Auto Bingo", layout="wide")

# Odświeżanie strony w tle co 3 sekundy (synchronizacja resetu Lidera)
st_autorefresh(interval=3000, limit=None, key="auto_refresh")

# Ukrycie menu, stopki Streamlita i marginesów
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0.5rem;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Stały, poprawny adres Twojej aplikacji na Render.com
RENDER_APP_URL = "https://car-bingo.onrender.com"

# Wspólna pamięć dla wszystkich telefonów w aucie
@st.cache_resource
def get_game_state():
    return {
        "grid_size": 3,
        "winner": None,
        "ended": False,
        "game_id": 1
    }

game_state = get_game_state()
IMAGE_DIR = "images"

# Odczyt folderu ze zdjęciami
if os.path.exists(IMAGE_DIR):
    all_images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
else:
    all_images = []

# Inicjalizacja stanu widoczności kodu QR
if "show_qr" not in st.session_state:
    st.session_state["show_qr"] = False

# Górny nagłówek z przyciskiem QR
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("🚗 Auto Bingo")
with col_btn:
    st.write("") # małe wyrównanie w pionie
    if st.button("📱 QR", use_container_width=True, type="secondary"):
        st.session_state["show_qr"] = not st.session_state["show_qr"]
        st.rerun()

# Wyświetlanie kodu QR po kliknięciu ikonki
if st.session_state["show_qr"]:
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px; border: 1px solid #ddd;">
            <p style="color: #333; font-weight: bold; margin-bottom: 8px;">Zeskanuj kod, aby dołączyć do gry:</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_q1, col_q2, col_q3 = st.columns([1, 2, 1])
    with col_q2:
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(RENDER_APP_URL)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = BytesIO()
        img.save(buf)
        st.image(buf.getvalue(), width=220)
        st.caption(f"Link: {RENDER_APP_URL}")

# --- IDENTYFIKACJA GRACZA ---
col1, col2 = st.columns([2, 1])
with col1:
    if "player_name" not in st.session_state:
        st.session_state["player_name"] = "Pasażer 1"
    player_name = st.text_input("Twoje Imię / Nick:", value=st.session_state["player_name"]).strip()
    st.session_state["player_name"] = player_name
with col2:
    is_master = st.checkbox("👑 Lider (Master)")

st.write("---")

# --- PANEL LIDERA (RESET GRY) ---
if is_master:
    st.subheader("⚙️ Panel Lidera")
    grid_choice = st.selectbox("Wybierz rozmiar planszy dla wszystkich:", ["3x3 (9 zdjęć)", "4x4 (16 zdjęć)", "5x5 (25 zdjęć)"])
    new_grid_size = int(grid_choice.split("x")[0])

    if st.button("🚀 Zresetuj grę i rozdaj nowe plansze", use_container_width=True, type="primary"):
        game_state["grid_size"] = new_grid_size
        game_state["winner"] = None
        game_state["ended"] = False
        game_state["game_id"] += 1
        st.rerun()

grid_size = game_state["grid_size"]
required_images = grid_size * grid_size

# --- LOGIKA GRY ---
if game_state["ended"]:
    st.error(f"🛑 KONIEC GRY! Gracz **{game_state['winner']}** ułożył BINGO jako pierwszy!")
    if is_master:
        st.info("💡 Liderze, zresetuj grę wyżej, by zacząć od nowa.")
else:
    if len(all_images) < required_images:
        st.warning(f"W folderze 'images' masz tylko {len(all_images)} zdjęć. Do planszy {grid_size}x{grid_size} potrzebujesz min. {required_images}!")
    else:
        current_game_id = game_state["game_id"]
        
        if "current_game_id" not in st.session_state or st.session_state["current_game_id"] != current_game_id:
            st.session_state["current_game_id"] = current_game_id
            st.session_state["bingo_grid"] = random.sample(all_images, required_images)

        encoded_images = []
        for img_name in st.session_state["bingo_grid"]:
            img_path = os.path.join(IMAGE_DIR, img_name)
            with open(img_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
                encoded_images.append(f"data:image/jpeg;base64,{encoded}")

        html_height = 800 if grid_size == 3 else (1000 if grid_size == 4 else 1200)

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
            #win-banner {{
                display: none;
                background-color: #28a745;
                color: white;
                text-align: center;
                font-size: 1.8rem;
                font-weight: bold;
                padding: 14px;
                border-radius: 10px;
                margin-bottom: 14px;
                animation: pop 0.4s ease-in-out;
            }}
            @keyframes pop {{
                0% {{ transform: scale(0.8); opacity: 0; }}
                100% {{ transform: scale(1); opacity: 1; }}
            }}
        </style>

        <div id="win-banner">🎉 BINGO! WYGRANA! 🎉</div>

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
            }};

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

            function playVictorySound(name) {{
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
                    setTimeout(() => {{
                        if ('speechSynthesis' in window) {{
                            const msg = new SpeechSynthesisUtterance('Bingo! Zwyciężył gracz ' + name + '!');
                            msg.lang = 'pl-PL';
                            window.speechSynthesis.speak(msg);
                        }}
                    }}, 600);
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

                const banner = document.getElementById('win-banner');
                if (isWin && !hasWon) {{
                    hasWon = true;
                    banner.style.display = 'block';
                    playVictorySound(playerName);
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

# --- BOCZNY QR (DODATKOWO) ---
with st.sidebar:
    st.header("📲 Szybki QR")
    qr_s = qrcode.QRCode(version=1, box_size=8, border=2)
    qr_s.add_data(RENDER_APP_URL)
    qr_s.make(fit=True)
    img_s = qr_s.make_image(fill_color="black", back_color="white")
    buf_s = BytesIO()
    img_s.save(buf_s)
    st.image(buf_s.getvalue(), width=180)
