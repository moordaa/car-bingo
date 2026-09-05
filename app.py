import streamlit as st
import os
import random
import base64
import qrcode
from io import BytesIO
import json

st.set_page_config(page_title="Auto Bingo", layout="centered")

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

RENDER_APP_URL = "https://car-bingo.onrender.com"

@st.cache_resource
def get_game_state():
    return {
        "grid_size": 3,
        "winner": None,
        "ended": False,
        "game_id": 1,
        "bingo_grid": [],
        "encoded_images": [],
        "last_game_id": 0,
        "player_states": {}
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

if "confirm_restart" not in st.session_state:
    st.session_state["confirm_restart"] = False

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
        game_state["player_states"] = {}

st.markdown("<h2 style='text-align: center; margin-top: 0; margin-bottom: 5px;'>🚗 Auto Bingo</h2>", unsafe_allow_html=True)

# --- KOLEJNOŚĆ INTERFEJSU OD GÓRY ---

# 1. QR Code
with st.expander("📲 Pokaż kod QR", expanded=False):
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    qr = qrcode.QRCode(version=1, box_size=5, border=1)
    qr.add_data(RENDER_APP_URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf)
    st.image(buf.getvalue(), width=140)
    st.markdown("</div>", unsafe_allow_html=True)

# 2. Nazwa pasażera
player_name = st.text_input("Twoje Imię / Nick:", value=st.session_state["player_name"]).strip()
st.session_state["player_name"] = player_name

# 3. Nowe rozdanie (z potwierdzeniem)
if not st.session_state["confirm_restart"]:
    if st.button("🚀 Nowe rozdanie (Restart)", use_container_width=True, type="secondary"):
        st.session_state["confirm_restart"] = True
        st.rerun()
else:
    if st.button("⚠️ Potwierdź nowe rozdanie", use_container_width=True, type="primary"):
        game_state["winner"] = None
        game_state["ended"] = False
        game_state["game_id"] += 1
        game_state["player_states"] = {}
        st.session_state["confirm_restart"] = False
        st.rerun()

# 4. Rozmiar planszy
idx = 0
if game_state["grid_size"] == 4: idx = 1
elif game_state["grid_size"] == 5: idx = 2

grid_choice = st.selectbox("Rozmiar planszy:", ["3x3 (9 zdjęć)", "4x4 (16 zdjęć)", "5x5 (25 zdjęć)"], index=idx)
new_size = int(grid_choice.split("x")[0])

if new_size != game_state["grid_size"]:
    game_state["grid_size"] = new_size
    game_state["winner"] = None
    game_state["ended"] = False
    game_state["game_id"] += 1
    game_state["player_states"] = {}
    st.rerun()

# 5. Odśwież stan
if st.button("🔄 Odśwież stan", use_container_width=True):
    st.rerun()

st.write("")

if game_state["ended"]:
    st.markdown(f"""
        <div style="background-color: #28a745; color: white; padding: 20px; border-radius: 12px; text-align: center; margin-top: 10px;">
            <h1 style="margin:0; font-size: 2.2rem;">🎉 BINGO! 🎉</h1>
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
    
    st.write("")
    if st.button("🚀 Rozpocznij kolejną rundę", use_container_width=True, type="primary"):
        game_state["winner"] = None
        game_state["ended"] = False
        game_state["game_id"] += 1
        game_state["player_states"] = {}
        st.rerun()
else:
    if len(all_images) < required_images:
        st.warning(f"Za mało zdjęć! Masz {len(all_images)}, potrzebujesz min. {required_images}!")
    else:
        html_height = 750 if grid_size == 3 else (950 if grid_size == 4 else 1150)
        encoded_images = game_state["encoded_images"]

        html_code = f"""
        <style>
            .bingo-container {{
                display: grid;
                grid-template-columns: repeat({grid_size}, 1fr);
                gap: 5px;
                width: 100%;
                max-width: 500px;
                margin: auto;
            }}
            .bingo-card {{
                position: relative;
                width: 100%;
                padding-top: 100%;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
                font-size: 2.5rem;
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
            const mySessionId = "{st.session_state['my_session_id']}";

            window.addEventListener('beforeunload', function (e) {{
                e.preventDefault();
                e.returnValue = '';
            }});

            window.onload = function() {{
                const buttons = window.parent.document.querySelectorAll('button');
                buttons.forEach(btn => {{
                    if (btn.innerText.includes('SYSTEM_WIN_BRIDGE') || btn.innerText.includes('SYSTEM_STATE_BRIDGE')) {{
                        const container = btn.closest('div[data-testid="stButton"]');
                        if (container) container.style.display = 'none';
                    }}
                }});
                // Automatyczne przesłanie stanu przy załadowaniu/odświeżeniu
                sendStateToServer();
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

            function sendStateToServer() {{
                const cards = document.querySelectorAll('.bingo-card');
                const checkedStates = Array.from(cards).map(card => card.classList.contains('checked'));
                
                const buttons = window.parent.document.querySelectorAll('button');
                buttons.forEach(btn => {{
                    if (btn.innerText.includes('SYSTEM_STATE_BRIDGE')) {{
                        const inputField = window.parent.document.querySelector('input[aria-label="STATE_INPUT"]');
                        if (inputField) {{
                            nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, "value").set;
                            nativeInputValueSetter.call(inputField, JSON.stringify({{name: playerName, checked: checkedStates, id: mySessionId}}));
                            inputField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        }}
                    }}
                }});
            }}

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

                sendStateToServer();

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

        sync_data = st.text_input("STATE_INPUT", key="state_input", label_visibility="collapsed")
        if sync_data:
            try:
                data = json.loads(sync_data)
                game_state["player_states"][data["id"]] = {"name": data["name"], "checked": data["checked"]}
            except:
                pass

        if st.button("SYSTEM_WIN_BRIDGE", key="win_bridge"):
            game_state["ended"] = True
            game_state["winner"] = player_name
            st.rerun()

        # Inicjalizacja wpisu dla siebie, aby serwer widział Twoją sesję
        if st.session_state["my_session_id"] not in game_state["player_states"]:
            game_state["player_states"][st.session_state["my_session_id"]] = {"name": player_name, "checked": [False]*required_images}

        other_players = {sid: pdata for sid, pdata in game_state["player_states"].items() if sid != st.session_state["my_session_id"]}
        
        if other_players:
            st.markdown("---")
            st.markdown("#### 👥 Postępy innych graczy:")
            for sid, pdata in other_players.items():
                checked_count = sum(1 for c in pdata["checked"] if c)
                total_cards = len(pdata["checked"])
                st.markdown(f"**{pdata['name']}**: zaznaczono **{checked_count}** / {total_cards} kafelków")
                
                cols = st.columns(grid_size)
                for idx, is_chk in enumerate(pdata["checked"]):
                    col_idx = idx % grid_size
                    with cols[col_idx]:
                        icon = "✅" if is_chk else "⬜"
                        st.markdown(f"<div style='text-align: center; font-size: 1.2rem;'>{icon}</div>", unsafe_allow_html=True)
                st.write("")
