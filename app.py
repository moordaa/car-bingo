import streamlit as st
import os
import random
import base64
import qrcode
from io import BytesIO
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Auto Bingo", layout="wide")

# Odświeżanie strony w tle co 3 sekundy (synchronizacja)
st_autorefresh(interval=3000, limit=None, key="auto_refresh")

# Ukrycie menu, stopki Streamlita, marginesów oraz wymuszenie kwadratowego kształtu przycisków w rzędzie
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0.5rem;}
    
    /* Styl dla kwadratowych przycisków w jednej linii */
    div[data-testid="stHorizontalBlock"] > div:not([data-testid="column"]) {
        display: flex;
        gap: 6px;
    }
    div[data-testid="stHorizontalBlock"] button {
        aspect-ratio: 1 / 1;
        width: 100%;
        min-height: 55px;
        padding: 0px;
        font-size: 0.9rem;
        line-height: 1.2;
        border-radius: 8px;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Stały, poprawny adres aplikacji na Render.com
RENDER_APP_URL = "https://car-bingo.onrender.com"

# Wspólna pamięć dla wszystkich w aucie
@st.cache_resource
def get_game_state():
    return {
        "grid_size": 3,
        "winner": None,
        "ended": False,
        "game_id": 1,
        "master_session": None
    }

game_state = get_game_state()
IMAGE_DIR = "images"

if os.path.exists(IMAGE_DIR):
    all_images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
else:
    all_images = []

if "my_session_id" not in st.session_state:
    st.session_state["my_session_id"] = str(random.randint(100000, 999999))

if "player_name" not in st.session_state:
    st.session_state["player_name"] = "Pasażer 1"

for key in ["show_qr", "show_master", "show_settings", "show_reset"]:
    if key not in st.session_state:
        st.session_state[key] = False

# Tytuł aplikacji
st.title("🚗 Auto Bingo")

player_name = st.text_input("Twoje Imię / Nick:", value=st.session_state["player_name"]).strip()
st.session_state["player_name"] = player_name

# --- PASEK STEROWANIA: 4 KWADRATOWE PRZYCISKI W JEDNEJ LINII ---
col_b1, col_b2, col_b3, col_b4, col_space = st.columns([1, 1, 1, 1, 4])

with col_b1:
    if st.button("📱\nQR", use_container_width=True):
        st.session_state["show_qr"] = not st.session_state["show_qr"]
        st.session_state["show_settings"] = False
        st.session_state["show_reset"] = False
        st.rerun()

with col_b2:
    is_current_master = (game_state["master_session"] == st.session_state["my_session_id"])
    btn_label = "👑\nLider" if not is_current_master else "❌\nOddaj"
    if st.button(btn_label, use_container_width=True):
        if not is_current_master:
            game_state["master_session"] = st.session_state["my_session_id"]
        else:
            game_state["master_session"] = None
        st.rerun()

with col_b3:
    if st.button("⚙️\nPlansza", use_container_width=True):
        st.session_state["show_settings"] = not st.session_state["show_settings"]
        st.session_state["show_qr"] = False
        st.session_state["show_reset"] = False
        st.rerun()

with col_b4:
    if st.button("🚀\nReset", use_container_width=True):
        st.session_state["show_reset"] = not st.session_state["show_reset"]
        st.session_state["show_qr"] = False
        st.session_state["show_settings"] = False
        st.rerun()

is_master = is_current_master

# --- ROZWIJANE PANELE ---

if st.session_state["show_qr"]:
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 12px; border-radius: 8px; text-align: center; margin-top: 10px; border: 1px solid #ddd;">
            <strong>Zeskanuj kod, aby dołączyć do gry:</strong>
        </div>
    """, unsafe_allow_html=True)
    q1, q2, q3 = st.columns([1, 2, 1])
    with q2:
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(RENDER_APP_URL)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf)
        st.image(buf.getvalue(), width=200)
        st.caption(f"Link: {RENDER_APP_URL}")

if st.session_state["show_settings"]:
    st.markdown("### ⚙️ Wybór wielkości planszy")
    if is_master:
        grid_choice = st.selectbox("Wybierz planszę dla wszystkich:", ["3x3 (9 zdjęć)", "4x4 (16 zdjęć)", "5x5 (25 zdjęć)"], key="grid_select_box")
        new_size = int(grid_choice.split("x")[0])
        if new_size != game_state["grid_size"]:
            game_state["grid_size"] = new_size
            game_state["game_id"] += 1
            st.rerun()
    else:
        st.warning("⚠️ Tylko aktualny Lider (Master) może zmieniać wielkość planszy!")

if st.session_state["show_reset"]:
    st.markdown("### 🚀 Resetowanie gry")
    if is_master:
        if st.button("Potwierdź i zresetuj grę dla wszystkich", type="primary", use_container_width=True):
            game_state["winner"] = None
            game_state["ended"] = False
            game_state["game_id"] += 1
            st.session_state["show_reset"] = False
            st.rerun()
    else:
        st.warning("⚠️ Tylko aktualny Lider (Master) może zresetować grę!")

st.write("---")

grid_size = game_state["grid_size"]
required_images = grid_size * grid_size

# --- LOGIKA GRY ---
if game_state["ended"]:
    st.error(f"🛑 KONIEC GRY! Gracz **{game_state['winner']}** ułożył BINGO jako pierwszy!")
    if is_master:
        st.info("💡 Liderze, możesz zresetować grę przyciskiem wyżej.")
else:
    if len(all_images) < required_images:
        st.warning(f"W folderze 'images' masz tylko {len(all_images)} zdjęć. Do planszy {grid_size}x{grid_size} potrzeba min. {required_images}!")
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
