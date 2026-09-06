import os
import random
import streamlit as st

# Config strony
st.set_page_config(
    page_title="Auto Bingo",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styl CSS dopasowujący zdjęcia
st.markdown("""
    <style>
    [data-testid="stImage"] img {
        object-fit: contain !important;
        height: 100px !important;
        width: 100%;
        background-color: white; 
        border-radius: 8px;
        padding: 5px;
    }
    div[data-testid="column"] > div > div > div > div {
        gap: 0.2rem !important;
    }
    div[data-testid="column"] {
        text-align: center;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Definicje ścieżek i stałych
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
GRID_SIZE = 25

# Indywidualny stan sesji dla każdego urządzenia (brak synchronizacji i imion)
if 'board' not in st.session_state:
    st.session_state.board = []
if 'checked' not in st.session_state:
    st.session_state.checked = [False] * GRID_SIZE

def load_images():
    if not os.path.exists(IMAGE_DIR):
        return []
    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
    files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(valid_extensions)]
    return sorted(files)

def generate_new_board():
    images = load_images()
    if len(images) == 0:
        st.session_state.board = []
    elif len(images) < GRID_SIZE:
        st.session_state.board = [random.choice(images) for _ in range(GRID_SIZE)]
    else:
        st.session_state.board = random.sample(images, GRID_SIZE)
    st.session_state.checked = [False] * GRID_SIZE

# --- MENU BOCZNE ---
with st.sidebar:
    st.header("⚙️ Menu Gry")
    
    if st.button("🔄 Nowa plansza", type="primary", use_container_width=True):
        generate_new_board()
        st.rerun()
        
    if st.button("🗑️ Odznacz wszystko", use_container_width=True):
        st.session_state.checked = [False] * GRID_SIZE
        st.rerun()
        
    st.write("---")
    st.info("Tryb Solo: Każdy gracz ma swoją niezależną planszę. Wypatruj obiektów przez okno!")

# --- GŁÓWNA APLIKACJA ---
st.title("🚗 Auto Bingo")

images_available = load_images()

if len(images_available) == 0:
    st.warning("Brak grafik w folderze 'images'. Dodaj pliki graficzne, aby rozpocząć grę.")
else:
    if not st.session_state.board or len(st.session_state.board) != GRID_SIZE:
        generate_new_board()

    # Wyświetlanie siatki Bingo 5x5
    board = st.session_state.board
    for row in range(5):
        cols = st.columns(5)
        for col in range(5):
            idx = row * 5 + col
            with cols[col]:
                if idx < len(board):
                    img_name = board[idx]
                    img_path = os.path.join(IMAGE_DIR, img_name)
                    
                    clean_name = os.path.splitext(img_name)[0].replace("-", " ").replace("_", " ")

                    if os.path.exists(img_path):
                        st.image(img_path, use_container_width=True)
                    
                    is_checked = st.session_state.checked[idx]
                    btn_label = f"✅ {clean_name}" if is_checked else clean_name
                    btn_type = "primary" if is_checked else "secondary"
                    
                    if st.button(btn_label, key=f"tile_{idx}", type=btn_type, use_container_width=True):
                        st.session_state.checked[idx] = not st.session_state.checked[idx]
                        st.rerun()

    # Nowy, prosty komunikat o wygranej
    if all(st.session_state.checked):
        st.balloons()
        st.success("🎉 WYGRAŁEM! Cała plansza skompletowana!")
