import streamlit as st
import os
import random
import qrcode
from io import BytesIO

st.set_page_config(page_title="Auto Bingo", layout="wide")

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
    if st.button("🎲 Losuj nową planszę") or "bingo_grid" not in st.session_state:
        st.session_state.bingo_grid = random.sample(all_images, 9)
        st.session_state.checked = [False] * 9

    st.write("---")

    # Rysowanie siatki 3x3
    for row in range(3):
        cols = st.columns(3)
        for col in range(3):
            idx = row * 3 + col
            img_name = st.session_state.bingo_grid[idx]
            img_path = os.path.join(IMAGE_DIR, img_name)
            
            with cols[col]:
                st.image(img_path, use_container_width=True)
                st.session_state.checked[idx] = st.checkbox(
                    "Znalazłem!", 
                    value=st.session_state.checked[idx], 
                    key=f"check_{idx}"
                )

    if all(st.session_state.checked):
        st.balloons()
        st.success("🎉 BINGO! Znalazłeś wszystkie obiekty!")

with st.sidebar:
    st.header("📲 Kod QR dla pasażerów")
    st.write("Skanuj z drugiego telefonu:")
    
    # Tutaj po uruchomieniu wkleisz swój link z przeglądarki
    app_url = st.text_input("Link do gry:", "https://share.streamlit.io")
    
    qr = qrcode.make(app_url)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), width=200)
