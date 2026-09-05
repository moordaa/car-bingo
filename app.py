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

    # Kod HTML i CSS tworzący wymuszoną siatkę 3x3 oraz klikalne obrazki
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
            padding-top: 100%; /* Kwadratowy kształt */
            border-radius: 12px;
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
            transition: transform 0.2s, filter 0.2s;
        }}
        /* Efekt po kliknięciu/zaznaczeniu */
        .bingo-card.checked img {{
            filter: grayscale(80%) brightness(50%);
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
    </style>

    <div class="bingo-container">
        {"".join([f'<div class="bingo-card" onclick="this.classList.toggle(\'checked\')"><img src="{img_url}"></div>' for img_url in encoded_images])}
    </div>
    """

    st.components.v1.html(html_code, height=520, scrolling=False)

# Boczne menu z kodem QR do dołączania pasażerów
with st.sidebar:
    st.header("📲 Kod QR dla pasażerów")
    st.write("Wpisz link aplikacji, aby wygenerować kod QR:")
    
    app_url = st.text_input("Link do gry:", "https://fakturki-tejbrant.streamlit.app")
    
    qr = qrcode.make(app_url)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), width=200)
