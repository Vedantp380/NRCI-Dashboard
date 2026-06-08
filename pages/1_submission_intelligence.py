import streamlit as st
from services.project_service import prepare_project_library_data

st.set_page_config(layout="wide")

# =========================
# HEADER
# =========================
st.title("📊 Project Library")

# ✅ Upload file
uploaded_file = st.file_uploader("Upload Project File", type=["xlsx", "xls", "csv"])

if uploaded_file is None:
    st.warning("Please upload file to continue")
    st.stop()

# =========================
# DATA LOAD
# =========================
df = prepare_project_library_data(uploaded_file, inflation_mode="cpi")

# =========================
# KPI SECTION
# =========================
k1, k2 = st.columns(2)

with k1:
    st.metric("Total Projects", len(df))

with k2:
    st.metric("Selected Projects", len(df))

st.markdown("---")

# =========================
# MAIN LAYOUT
# =========================
left, right = st.columns([1, 3], gap="medium")

# =========================
# LEFT PANEL → FILTERS
# =========================
with left:
    st.subheader("🔎 Filters")

    region = st.selectbox(
        "Region",
        ["All"] + sorted(df["Region"].dropna().unique().tolist())
    )

    basis = st.selectbox(
        "Basis of Costs",
        ["All"] + sorted(df["Basis of Costs"].dropna().unique().tolist())
    )

    scheme = st.selectbox(
        "Scheme Type",
        ["All"] + sorted(df["Scheme Type"].dropna().unique().tolist())
    )

    search = st.text_input("Search Project")

    # Cost range
    min_cost = int(df["Project Cost Numeric"].min())
    max_cost = int(df["Project Cost Numeric"].max())

    cost_range = st.slider(
        "Project Cost Range",
        min_cost,
        max_cost,
        (min_cost, max_cost)
    )

    # Date range
    df["year"] = df["Base Date Parsed"].dt.year

    min_year = int(df["year"].min())
    max_year = int(df["year"].max())

    year_range = st.slider(
        "Base Year",
        min_year,
        max_year,
        (min_year, max_year)
    )

# =========================
# FILTER LOGIC
# =========================
filtered_df = df.copy()

if region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == region]

if basis != "All":
    filtered_df = filtered_df[filtered_df["Basis of Costs"] == basis]

if scheme != "All":
    filtered_df = filtered_df[filtered_df["Scheme Type"] == scheme]

if search:
    filtered_df = filtered_df[
        filtered_df["Project ID Display"].str.contains(search, case=False, na=False)
    ]

filtered_df = filtered_df[
    (filtered_df["Project Cost Numeric"] >= cost_range[0]) &
    (filtered_df["Project Cost Numeric"] <= cost_range[1])
]

filtered_df = filtered_df[
    (filtered_df["year"] >= year_range[0]) &
    (filtered_df["year"] <= year_range[1])
]

# =========================
# UPDATE KPI AFTER FILTER
# =========================
k2.metric("Selected Projects", len(filtered_df))

# =========================
# RIGHT PANEL → TABLE
# =========================
with right:
    st.subheader("📋 Projects Table")

    display_cols = [
        "Project ID Display",
        "Basis of Costs",
        "Project Cost",
        "Inflated Project Cost",
        "Base Date",
        "PITG %"
    ]

    st.dataframe(
        filtered_df[display_cols],
        use_container_width=True,
        height=500
    )

# =========================
# FOOTER ACTION
# =========================
st.markdown("---")
st.write("👉 Select a project above for further details")
