import streamlit as st
import os
import random
import qrcode
from io import BytesIO

# Konfiguracja strony
st.set_page_config(page_title="Auto Bingo", layout="wide")

# Ukrycie menu i paska nagłówka Streamlita dla lepszego wyglądu na telefonie
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🚗 Auto Bingo")

IMAGE_DIR = "images"

# Pobieranie listy zdjęć z folderu images/
if os.path.exists(IMAGE_DIR):
    all_images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
else:
    all_images = []

if len(all_images) < 9:
    st.warning(f"W folderze 'images' znajduje się tylko {len(all_images)} zdjęć. Dodaj co najmniej 9 obrazków!")
else:
    # Przycisk do losowania nowej planszy dla gracza
    if st.button("🎲 Losuj nową planszę", use_container_width=True) or "bingo_grid" not in st.session_state:
        st.session_state.bingo_grid = random.sample(all_images, 9)
        st.session_state.checked = [False] * 9

    st.write("---")

    # Wyświetlanie siatki 3x3
    for row in range(3):
        cols = st.columns(3)
        for col in range(3):
            idx = row * 3 + col
            img_name = st.session_state.bingo_grid[idx]
            img_path = os.path.join(IMAGE_DIR, img_name)
            is_checked = st.session_state.checked[idx]

            with cols[col]:
                # Obrazek w siatce
                st.image(img_path, use_container_width=True)
                
                # Przycisk stanu pod zdjęciem
                btn_label = "✅ ZNALAZŁEM!" if is_checked else "🔍 Szukaj"
                btn_type = "primary" if is_checked else "secondary"
                
                if st.button(btn_label, key=f"btn_{idx}", type=btn_type, use_container_width=True):
                    st.session_state.checked[idx] = not is_checked
                    st.rerun()

    # Efekt po znalezieniu wszystkich 9 obiektów
    if all(st.session_state.checked):
        st.balloons()
        st.success("🎉 BINGO! Znalazłeś wszystkie 9 obiektów!")

# Boczne menu z kodem QR do dołączania pasażerów
with st.sidebar:
    st.header("📲 Kod QR dla pasażerów")
    st.write("Wpisz link swojej aplikacji, aby wygenerować QR kod do zeskanowania:")
    
    # Wklej tutaj docelowy URL swojej aplikacji (np. https://twoja-nazwa.streamlit.app)
    app_url = st.text_input("Link do gry:", "https://car-bingo.streamlit.app")
    
    qr = qrcode.make(app_url)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), width=200)
