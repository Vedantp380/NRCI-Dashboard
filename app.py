import streamlit as st
import hashlib

st.set_page_config(layout="wide")

# =========================
# USER CONFIG (CAN MOVE LATER)
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

users = {
    "admin": {
        "password": hash_password("admin123"),
        "role": "global"
    },
    "india_user": {
        "password": hash_password("india123"),
        "role": "india"
    }
}

# =========================
# SESSION INIT
# =========================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# =========================
# LOGIN UI
# =========================
def login_page():
    st.markdown("<h2 style='text-align:center;'>🔐 Login to BenchSmart Insights</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in users:
                if users[username]["password"] == hash_password(password):
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = username
                    st.session_state["role"] = users[username]["role"]
                    st.success("Login successful ✅")
                    st.rerun()

            st.error("Invalid credentials ❌")

# =========================
# AUTH CHECK
# =========================
if not st.session_state["authenticated"]:
    login_page()
    st.stop()

# =========================
# LOGOUT
# =========================
st.sidebar.success(f"👤 {st.session_state['user']}")

if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()

# =========================
# YOUR ORIGINAL UI (UNCHANGED)
# =========================

# ✅ CENTER WRAPPER
container = st.container()

with container:

    st.markdown("""
    <style>
    .main-title {
        font-size: 42px;
        font-weight: bold;
        color: #0b4f6c;
        margin-bottom: 10px;
        text-align: left;
    }

    .desc {
        font-size: 16px;
        color: #444;
        line-height: 1.6;
        max-width: 800px;
    }

    .center-container {
        max-width: 1100px;
        margin: auto;
    }

    div.stButton > button {
        width: 100%;
        height: 120px;
        background-color: #0b4f6c;
        color: white;
        font-size: 16px;
        font-weight: bold;
        border-radius: 12px;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #083a53;
    }

    .card-desc {
        text-align: center;
        font-size: 13px;
        margin-top: 10px;
        color: #555;
        min-height: 60px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="center-container">', unsafe_allow_html=True)

    # ✅ TITLE
    st.markdown('<div class="main-title">BenchSmart Insights</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="desc">
    BenchSmart Insights offers a central resource of project information data, enabling consistent analysis, 
    portfolio navigation, and decision support.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Click a card to navigate")

    st.markdown("<br>", unsafe_allow_html=True)

    # ✅ GRID
    col1, col2, col3, col4 = st.columns(4)

    # ✅ CARD 1
    with col1:
        if st.button("📊 Project Library"):
            st.switch_page("pages/1_submission_intelligence.py")

        st.markdown('<div class="card-desc">Portfolio-style project dashboard with filters and insights.</div>', unsafe_allow_html=True)

    # ✅ CARD 2
    with col2:
        st.button("📈 Unit Rate Analysis", disabled=True)
        st.markdown('<div class="card-desc">Reserved for your next module.</div>', unsafe_allow_html=True)

    # ✅ CARD 3
    with col3:
        st.button("🚆 Rail Investment Reporting", disabled=True)
        st.markdown('<div class="card-desc">Reserved for your next module.</div>', unsafe_allow_html=True)

    # ✅ CARD 4
    with col4:
        st.button("🔍 Specialist Insights", disabled=True)
        st.markdown('<div class="card-desc">Reserved for your next module.</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)