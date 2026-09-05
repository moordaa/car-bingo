# Ukrycie menu, stopki Streamlita, marginesów oraz stylizacja przycisków
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0.5rem;}
    
    /* Wymuszenie równego podziału i kwadratowego kształtu przycisków */
    div[data-testid="stHorizontalBlock"] {
        display: flex;
        width: 100%;
        gap: 8px;
    }
    div[data-testid="stHorizontalBlock"] > div {
        flex: 1;
    }
    div[data-testid="stHorizontalBlock"] button {
        aspect-ratio: 1 / 1;
        width: 100%;
        min-height: 60px;
        padding: 0px;
        font-size: 1rem;
        font-weight: bold;
        line-height: 1.2;
        border-radius: 10px;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Tytuł aplikacji
st.title("🚗 Auto Bingo")

player_name = st.text_input("Twoje Imię / Nick:", value=st.session_state["player_name"]).strip()
st.session_state["player_name"] = player_name

# --- PASEK STEROWANIA: 4 PRZYCISKI W POZIOMEJ LINII NA CAŁĄ SZEROKOŚĆ ---
col_b1, col_b2, col_b3, col_b4 = st.columns(4)

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
