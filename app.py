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

# Wybór rozmiaru planszy
grid_choice = st.selectbox("Wybierz rozmiar planszy:", ["3x3 (9 zdjęć)", "4x4 (16 zdjęć)", "5x5 (25 zdjęć)"])
grid_size = int(grid_choice.split("x")[0])  # Pobiera 3, 4 lub 5
required_images = grid_size * grid_size

if len(all_images) < required_images:
    st.warning(f"W folderze 'images' znajduje się tylko {len(all_images)} zdjęć. Do planszy {grid_size}x{grid_size} potrzebujesz co najmniej {required_images} obrazków!")
else:
    # Losowanie nowej planszy przy zmianie rozmiaru lub po kliknięciu przycisku
    if (st.button("🎲 Losuj nową planszę", use_container_width=True) or 
        "bingo_grid" not in st.session_state or 
        len(st.session_state.bingo_grid) != required_images):
        st.session_state.bingo_grid = random.sample(all_images, required_images)

    # Konwersja zdjęć na base64 do wyświetlenia w HTML
    encoded_images = []
    for img_name in st.session_state.bingo_grid:
        img_path = os.path.join(IMAGE_DIR, img_name)
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            encoded_images.append(f"data:image/jpeg;base64,{encoded}")

    # Wysokość komponentu HTML zależnie od rozmiaru
    html_height = 500 + (grid_size - 3) * 120

    # Kod HTML, CSS i JavaScript z dynamiczną siatką, detekcją wygranej oraz dźwiękiem
    html_code = f"""
    <style>
        .bingo-container {{
            display: grid;
            grid-template-columns: repeat({grid_size}, 1fr);
            gap: {6 if grid_size > 3 else 8}px;
            width: 100%;
            max-width: 550px;
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
        const gridSize = {grid_size};

        // Generowanie wzorów wygrywających (poziome, pionowe, przekątne)
        function generateWinPatterns(size) {{
            const patterns = [];
            
            // Poziome
            for (let r = 0; r < size; r++) {{
                const row = [];
                for (let c = 0; c < size; c++) {{
                    row.push(r * size + c);
                }}
                patterns.push(row);
            }}

            // Pionowe
            for (let c = 0; c < size; c++) {{
                const col = [];
                for (let r = 0; r < size; r++) {{
                    col.push(r * size + c);
                }}
                patterns.push(col);
            }}

            // Przekątne
            const diag1 = [];
            for (let i = 0; i < size; i++) {{
                diag1.push(i * size + i);
            }}
            patterns.push(diag1);

            const diag2 = [];
            for (let i = 0; i < size; i++) {{
                diag2.push(i * size + (size - 1 - i));
            }}
            patterns.push(diag2);

            return patterns;
        }}

        const winPatterns = generateWinPatterns(gridSize);

        // Generator tonów dźwiękowych i syntezy mowy
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

    st.components.v1.html(html_code, height=html_height, scrolling=False)

# Boczne menu z kodem QR do dołączania pasażerów
with st.sidebar:
    st.header("📲 Kod QR dla pasażerów")
    st.write("Wpisz dokładny, publiczny adres swojej aplikacji:")
    
    # Podaj dokładny, publiczny URL swojej aplikacji Streamlit
    default_url = "https://car-bingo.streamlit.app"
    app_url = st.text_input("Link do gry:", default_url)
    
    # Generowanie kodu QR
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=2,
    )
    qr.add_data(app_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf)
    st.image(buf.getvalue(), width=220)
