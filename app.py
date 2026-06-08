import streamlit as st

st.set_page_config(layout="wide")

# ✅ CENTER WRAPPER (IMPORTANT FIX)
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

    /* ✅ CENTER MAIN CONTENT */
    .center-container {
        max-width: 1100px;
        margin: auto;
    }

    /* ✅ CARD BUTTON STYLE (FIXED size) */
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
        transform: scale(1.02);
    }

    /* ✅ DESCRIPTION */
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

    # ✅ PERFECTLY CENTERED GRID
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