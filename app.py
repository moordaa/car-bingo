import os
import random
import base64
import json
import streamlit as st

st.set_page_config(page_title="Auto Bingo", page_icon="🚗", layout="centered", initial_sidebar_state="collapsed")

st.markdown("<style>#MainMenu, footer, header {visibility: hidden;} .block-container {padding: 0.5rem 0.2rem 2rem 0.2rem !important;}</style>", unsafe_allow_html=True)

IMAGE_DIR = "images"
REQUIRED_IMAGES = 25
RENDER_APP_URL = "https://car-bingo.onrender.com"

all_images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))] if os.path.exists(IMAGE_DIR) else []

if "game_id" not in st.session_state:
    st.session_state["game_id"] = 1

def generate_encoded_images():
    if len(all_images) < REQUIRED_IMAGES:
        return []
    selected = random.sample(all_images, REQUIRED_IMAGES)
    encoded = []
    for img in selected:
        path = os.path.join(IMAGE_DIR, img)
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            encoded.append(f"data:image/jpeg;base64,{b64}")
    return encoded

if "my_encoded_images" not in st.session_state or not st.session_state["my_encoded_images"]:
    st.session_state["my_encoded_images"] = generate_encoded_images()

st.markdown("<h3 style='text-align: center; margin: 0 0 10px 0;'>🚗 Auto Bingo</h3>", unsafe_allow_html=True)

if st.button("🚀 Nowa plansza / Reset", use_container_width=True, type="primary"):
    st.session_state["game_id"] += 1
    st.session_state["my_encoded_images"] = generate_encoded_images()
    st.rerun()

st.write("")

if len(all_images) < REQUIRED_IMAGES:
    st.error(f"W folderze 'images' jest tylko {len(all_images)} grafik. Wymagane min. 25 unikalnych obrazków!")
else:
    encoded_images = st.session_state["my_encoded_images"]
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={RENDER_APP_URL}"

    html_code = f"""
    <style>
        body {{ margin: 0; background: transparent; font-family: sans-serif; }}
        .bingo-container {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; max-width: 480px; margin: auto; }}
        .bingo-card {{ position: relative; width: 100%; padding-top: 100%; border-radius: 8px; overflow: hidden; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.3); cursor: pointer; user-select: none; }}
        .bingo-card img {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: contain; padding: 4px; box-sizing: border-box; }}
        .cross-overlay {{ display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); align-items: center; justify-content: center; font-size: 2.2rem; pointer-events: none; }}
        .bingo-card.checked .cross-overlay {{ display: flex; }}
        .bingo-card.checked img {{ filter: grayscale(80%) brightness(40%); }}
        .qr-section {{ margin-top: 250px; padding: 20px; text-align: center; background: rgba(255,255,255,0.05); border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); color: #fff; }}
        .qr-section img {{ width: 200px; height: 200px; border-radius: 8px; background: #fff; padding: 8px; margin-top: 10px; }}
    </style>

    <div class="bingo-container" id="bingoGrid"></div>
    <div id="winBanner" style="display:none; background:#28a745; color:#fff; padding:10px; border-radius:8px; text-align:center; margin-top:15px;"><h3 style="margin:0;">🎉 BINGO! Wygrałem, leszcze! 🎉</h3></div>
    
    <div class="qr-section">
        <h4 style="margin:0 0 5px 0;">Zeskanuj, aby grać na swoim telefonie</h4>
        <img src="{qr_url}">
    </div>

    <script>
        const gameId = {st.session_state['game_id']};
        const serverImgs = {json.dumps(encoded_images)};
        
        let imgs = (localStorage.getItem('bingo_gid') == gameId && localStorage.getItem('bingo_board')) ? JSON.parse(localStorage.getItem('bingo_board')) : serverImgs;
        if (localStorage.getItem('bingo_gid') != gameId) {{
            localStorage.setItem('bingo_gid', gameId);
            localStorage.setItem('bingo_board', JSON.stringify(serverImgs));
            localStorage.removeItem('bingo_state');
        }}

        document.getElementById('bingoGrid').innerHTML = imgs.map((url, i) => 
            `<div class="bingo-card" onclick="toggle(this)"><img src="${{url}}"><div class="cross-overlay">❌</div></div>`
        ).join('');

        const state = JSON.parse(localStorage.getItem('bingo_state') || '[]');
        const cards = document.querySelectorAll('.bingo-card');
        cards.forEach((c, i) => {{ if (state[i]) c.classList.add('checked'); }});

        const patterns = [];
        for(let r=0; r<5; r++) {{
            let row = [], col = [];
            for(let c=0; c<5; c++) {{ row.push(r*5+c); col.push(c*5+r); }}
            patterns.push(row, col);
        }}
        patterns.push([0,6,12,18,24], [4,8,12,16,20]);

        function checkWin(playSound=true) {{
            const checked = Array.from(cards).map(c => c.classList.contains('checked'));
            const isWin = patterns.some(p => p.every(idx => checked[idx]));
            const banner = document.getElementById('winBanner');
            if (isWin) {{
                if (banner.style.display === 'none' && playSound) {{
                    try {{
                        const ctx = new (window.AudioContext || window.webkitAudioContext)();
                        [261.63, 329.63, 392.00, 523.25].forEach((f, i) => {{
                            const o = ctx.createOscillator(), g = ctx.createGain();
                            o.frequency.value = f;
                            g.gain.setValueAtTime(0.3, ctx.currentTime + i*0.12);
                            g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + i*0.12 + 0.3);
                            o.connect(g); g.connect(ctx.destination);
                            o.start(ctx.currentTime + i*0.12); o.stop(ctx.currentTime + i*0.12 + 0.3);
                        }});
                    }} catch(e) {{}}
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        const msg = new SpeechSynthesisUtterance("BINGO! Wygrałem, leszcze!");
                        msg.lang = 'pl-PL'; msg.pitch = 1.1;
                        window.speechSynthesis.speak(msg);
                    }}
                }}
                banner.style.display = 'block';
            }} else {{
                banner.style.display = 'none';
            }}
        }}

        checkWin(false);

        function toggle(card) {{
            card.classList.toggle('checked');
            localStorage.setItem('bingo_state', JSON.stringify(Array.from(cards).map(c => c.classList.contains('checked'))));
            checkWin(true);
        }}
    </script>
    """

    st.components.v1.html(html_code, height=1050, scrolling=True)
