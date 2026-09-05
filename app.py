# Inicjalizacja stanu widoczności kodu QR
if "show_qr" not in st.session_state:
    st.session_state["show_qr"] = False

# Górny nagłówek z przyciskiem QR w jednej linii
col_title, col_btn = st.columns([5, 1])
with col_title:
    st.markdown("<h1 style='padding-top: 0px; margin-top: 0px;'>🚗 Auto Bingo</h1>", unsafe_allow_html=True)
with col_btn:
    if st.button("📱 QR", use_container_width=True, type="secondary"):
        st.session_state["show_qr"] = not st.session_state["show_qr"]
        st.rerun()

# Wyświetlanie kodu QR po kliknięciu ikonki
if st.session_state["show_qr"]:
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px; border: 1px solid #ddd;">
            <p style="color: #333; font-weight: bold; margin-bottom: 8px;">Zeskanuj kod, aby dołączyć do gry:</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_q1, col_q2, col_q3 = st.columns([1, 2, 1])
    with col_q2:
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(RENDER_APP_URL)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = BytesIO()
        img.save(buf)
        st.image(buf.getvalue(), width=220)
        st.caption(f"Link: {RENDER_APP_URL}")
