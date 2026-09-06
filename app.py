import os
import random
import streamlit as st

# Config strony
st.set_page_config(
    page_title="Auto Bingo",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Poprawiony CSS - tworzy równe, estetyczne kafelki dla obrazków
st.markdown("""
    <style>
    /* Ujednolicenie rozmiaru obrazków i dodanie białego tła dla przezroczystych PNG */
    [data-testid="stImage"] img {
        object-fit: contain !important;
        height: 120px !important;
        width: 100%;
        background-color: white; 
        border-radius: 8px;
        padding: 5px;
    }
    
    /* Zmniejszenie ogromnych odstępów Streamlita między grafiką a przyciskiem */
    div[data-testid="column"] > div > div > div > div {
        gap: 0.2rem !important;
    }
    
    /* Wyśrodkowanie kolumn */
    div[data-testid="column"] {
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Definicje ścieżek i stałych
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")

# Inicjalizacja stanu sesji gracza
if 'board' not in st.session_state:
    st.session_state.board = []
if 'checked' not in st.session_state:
    st.session_state.checked = [False] * 16

def load_images():
    """Wczytanie dostępnych plików graficznych z folderu images."""
    if not os.path.exists(IMAGE_DIR):
        return []
    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
    files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(valid_extensions)]
    return sorted(files)

def generate_new_board():
    """Generowanie nowej planszy 4x4 (16 losowych kafelków)."""
    images = load_images()
    if len(images) < 16:
        if len(images) > 0:
            st.session_state.board = [random.choice(images) for _ in range(16)]
        else:
            st.session_state.board = []
    else:
        st.session_state.board = random.sample(images, 16)
    st.session_state.checked = [False] * 16

# Nagłówek aplikacji
st.title("🚗 Auto Bingo")

images_available = load_images()

if len(images_available) == 0:
    st.warning("Brak grafik w folderze 'images'. Dodaj pliki graficzne, aby rozpocząć grę.")
else:
    # Wygeneruj planszę przy pierwszym uruchomieniu
    if not st.session_state.board:
        generate_new_board()

    # Przycisk nowej gry
    if st.button("🔄 Nowa plansza", type="primary", use_container_width=True):
        generate_new_board()
        st.rerun()

    st.write("---")

    # Wyświetlanie siatki Bingo 4x4
    board = st.session_state.board
    for row in range(4):
        cols = st.columns(4)
        for col in range(4):
            idx = row * 4 + col
            with cols[col]:
                if idx < len(board):
                    img_name = board[idx]
                    img_path = os.path.join(IMAGE_DIR, img_name)
                    
                    # Nazwa wyświetlana na przycisku
                    clean_name = os.path.splitext(img_name)[0].replace("-", " ").replace("_", " ")

                    # Obrazek
                    if os.path.exists(img_path):
                        st.image(img_path, use_container_width=True)
                    
                    # Przycisk pod obrazkiem
                    is_checked = st.session_state.checked[idx]
                    btn_label = f"✅ {clean_name}" if is_checked else clean_name
                    btn_type = "primary" if is_checked else "secondary"
                    
                    if st.button(btn_label, key=f"tile_{idx}", type=btn_type, use_container_width=True):
                        st.session_state.checked[idx] = not st.session_state.checked[idx]
                        st.rerun()

    # Sprawdzanie wygranej
    if all(st.session_state.checked):
        st.balloons()
        st.success("🎉 GRATULACJE! Wszystkie pola zaznaczone!")
