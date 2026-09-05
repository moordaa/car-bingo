import streamlit as st
import os
import random
import base64
import qrcode
from io import BytesIO

st.set_page_config(page_title="Auto Bingo", layout="wide")

# Ukrycie paska nagłówka i stopki Streamlita
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0.5rem;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🚗 Auto Bingo")

IMAGE_DIR = "images"

# Pobieranie listy zdjęć z folderu
if os.path.exists(IMAGE_DIR):
    all_images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
else:
    all_images = []

if len(all_images) < 9:
    st.warning(f"W folderze 'images' znajduje się tylko {len(all_images)} zdjęć. Dodaj co najmniej 9 obrazków!")
else:
    # Losowanie nowej planszy
    if st.button("🎲 Losuj nową planszę", use_container_width=True) or "bingo_grid" not in st.session_state:
        st.session_state.bingo_grid = random.sample(all_images, 9)

    # Konwersja zdjęć na base64 do wyświetlenia w HTML
    encoded_images = []
    for img_name in st.session_state.bingo_grid:
        img_path = os.path.join(IMAGE_DIR, img_name)
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            encoded_images.append(f"data:image/jpeg;base64,{encoded}")

    # Kod HTML, CSS i JavaScript z generowaniem dźwięku fanfar i głosu
    html_code = f"""
    <style>
        .bingo-container {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            width: 100%;
            max-width: 500px;
            margin: auto;
        }}
        .bingo-card {{
            position: relative;
            width: 100%;
            padding-top: 100%;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            cursor: pointer;
            user-select: none;
            border: 3px solid transparent;
            transition: border-color 0.3s;
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
            font-size: 3.5rem;
            pointer-events: none;
        }}
        #win-banner {{
            display: none;
            background-color: #28a745;
            color: white;
            text-align: center;
            font-size: 1.8rem;
            font-weight: bold;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 12px;
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

        // Generator tonów dźwiękowych (fanfara wygranej)
        function playVictorySound() {{
            try {{
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                const ctx = new AudioContext();
                
                const notes = [261.63, 329.63, 392.00, 523.25]; // Do-Mi-Sol-Do
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

                // Lektor głosowy po odtworzeniu dźwięków
                setTimeout(() => {{
                    if ('speechSynthesis' in window) {{
                        const msg = new SpeechSynthesisUtterance('Bingo! Mamy zwycięzcę!');
                        msg.lang = 'pl-PL';
                        msg.rate = 1.0;
                        window.speechSynthesis.speak(msg);
                    }}
                }}, 600);
            }} catch(e) {{
                console.log("Dźwięk wyłączony lub zablokowany przez przeglądarkę.");
            }}
        }}

        function checkBingo() {{
            const cards = document.querySelectorAll('.bingo-card');
            const checked = Array.from(cards).map(card => card.classList.contains('checked'));

            const winPatterns = [
                [0, 1, 2], [3, 4, 5], [6, 7, 8], // Poziome
                [0, 3, 6], [1, 4, 7], [2, 5, 8], // Pionowe
                [0, 4, 8], [2, 4, 6]             // Przekątne
            ];

            let isWin = false;
            for (let pattern of winPatterns) {{
                if (pattern.every(index => checked[index])) {{
                    isWin = true;
                    break;
                }}
            }}

            const banner = document.getElementById('win-banner');
            if (isWin) {{
                banner.style.display = 'block';
                if (!hasWon) {{
                    hasWon = true;
                    playVictorySound();
                }}
            }} else {{
                banner.style.display = 'none';
                hasWon = false;
            }}
        }}

        function toggleCard(card) {{
            card.classList.toggle('checked');
            checkBingo();
        }}
    </script>
    """

    st.components.v1.html(html_code, height=600, scrolling=False)

# Boczne menu z kodem QR do dołączania pasażerów
with st.sidebar:
    st.header("📲 Kod QR dla pasażerów")
    st.write("Wpisz link aplikacji, aby wygenerować kod QR:")
    
    app_url = st.text_input("Link do gry:", "https://fakturki-tejbrant.streamlit.app")
    
    qr = qrcode.make(app_url)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), width=200)
