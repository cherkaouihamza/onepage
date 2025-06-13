import streamlit as st
import os
import re
from pathlib import Path
from PIL import Image
from datetime import datetime
from ppt_auth_db import record_ppt_upload, get_user_uploads
from pdf2image import convert_from_path
from io import BytesIO
import base64


# --- Configuration ---
UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)
PDF2IMAGE_PATH = "C:/poppler/Library/bin"  # à adapter selon ton chemin Poppler

# --- Authentification ---
USERS = {
    "admin": {"password": "password123", "role": "admin"},
    "lecteur": {"password": "viewer123", "role": "viewer"}
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = USERS[username]["role"]
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()
    


# --- Fonctions auxiliaires ---
def secure_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)

def clean_filename(name):
    return name.replace("TECHLAB_ONEPAGE_", "")

# --- Interface principale ---
st.set_page_config(page_title="ONEPAGE TECHLAB", layout="wide")
st.markdown("""
    <style>
        /* Cacher le bouton 'Deploy' (Streamlit Cloud) */
        [data-testid="stDeployButton"] {
            display: none !important;
        }

        /* Compatibilité avec d’autres identifiants possibles */
        .stDeployButton {
            display: none !important;
        }

        /* Cacher aussi toute barre d’actions si présente */
        header [data-testid="stToolbar"] {
            visibility: hidden !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-size: 2.5em;'>LAST SHARED ONEPAGE TECHLAB</h1>", unsafe_allow_html=True)

# Réduction manuelle de la largeur de la sidebar avec CSS
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        min-width: 200px;
        max-width: 250px;
        width: 40% !important;
    }
    </style>
""", unsafe_allow_html=True)

if st.session_state.role == "admin":
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file:
        filename = secure_filename(uploaded_file.name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{timestamp}_{filename.replace('.pdf','')}"
        save_dir = UPLOAD_FOLDER / folder_name
        pdf_path = save_dir / "slides.pdf"
        save_dir.mkdir(parents=True, exist_ok=True)

        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        try:
            record_ppt_upload(st.session_state.username, folder_name, filename)
            st.success("PDF file saved successfully!")
        except Exception as e:
            st.error(f"Error while saving : {e}")

# --- Sidebar et historique ---
st.sidebar.title(f"Welcome, {st.session_state.username}")
if st.sidebar.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

if st.session_state.role == "admin":
    user_uploads = get_user_uploads(st.session_state.username)
else:
    user_uploads = get_user_uploads("admin")

if user_uploads:
    folder_display = [Path(u[0]) for u in user_uploads]
    filename_display = [clean_filename(u[1]) for u in user_uploads]
    options = list(zip(folder_display, filename_display))
    selected_folder, _ = st.sidebar.selectbox(
        "📂 Browse ONEPAGE history",
        options,
        format_func=lambda x: x[1]
    )
    selected_ppt = selected_folder
    pdf_path = UPLOAD_FOLDER / selected_ppt / "slides.pdf"

    if pdf_path.exists():
        try:
            images =  convert_from_path(
    str(pdf_path),
    dpi=400,
    fmt='png',
    poppler_path=PDF2IMAGE_PATH
)
            
            if len(images) >= 1:
                st.markdown("<div style='text-align: center; margin-bottom: 1em;'>", unsafe_allow_html=True)
                img1 = images[0].resize((300, int(images[0].height * (300 / images[0].width))))
                st.image(img1, caption="Slide 1")
                st.markdown("</div>", unsafe_allow_html=True)

            if len(images) >= 2:
                img2 = images[1]
                st.image(img2, caption="Slide 2", width=800)
        except Exception as e:
            st.error(f"Error reading the PDF : {e}")
    else:
        st.info("PDF not found for this file.")
else:
    st.info("No files found for the selected user.")
