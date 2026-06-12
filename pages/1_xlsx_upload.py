import streamlit as st
import pandas as pd
import numpy as np
import html

st.set_page_config(layout="wide")
st.title("📊 Work Activity")

# =========================================================
# ✅ USER EMAIL + ACCESS CONTROL
# =========================================================
current_user = st.text_input("Enter your email").strip().lower()

if not current_user:
    st.stop()

access_dict = {
    "North West & Central": ["abc@abc.com", "abc1@abc.com"],
    "Southern": ["abc1@abc.com"],
    "Eastern": ["abc1@abc.com"],
    "Scotland": ["abc1@abc.com"],
    "Wales & Western": ["abc1@abc.com"],
    "RICoE": ["admin@abc.com"]
}

allowed_regions = []

if current_user in [u.lower() for u in access_dict["RICoE"]]:
    allowed_regions = [r for r in access_dict if r != "RICoE"]
else:
    for region, users in access_dict.items():
        if region == "RICoE":
            continue
        if current_user in [u.lower() for u in users]:
            allowed_regions.append(region)

if not allowed_regions:
    st.error("❌ You do not have access")
    st.stop()

# =========================================================
# ✅ HELPERS
# =========================================================
def clean_text(val):
    val = str(val)
    val = html.unescape(val)
    val = val.replace("\xa0", " ")
    val = val.strip()
    val = " ".join(val.split())
    return val

def compute_unit_rate(df):
    df = df.copy()

    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df["RACM Qty"] = pd.to_numeric(df["RACM Qty"], errors="coerce")

    df["RACM Qty"] = df.groupby("RACM ID")["RACM Qty"].transform("first")

    df["RACM Unit Rate"] = (
        df.groupby("RACM ID")["Value"].transform("sum") / df["RACM Qty"]
    )

    df["RACM Unit Rate"] = df["RACM Unit Rate"].round(4)

    return df

def compute_summary(df):
    return df.groupby("RACM ID", as_index=False).agg({
        "Value": "sum",
        "RACM Qty": "first",
        "RACM Unit Rate": "first"
    }).rename(columns={"Value": "Total Value"})

def compute_racm_output(df):
    first_vals = df.groupby("RACM ID", as_index=False).first()

    cost = df.groupby("RACM ID", as_index=False)["Value"].sum()
    cost = cost.rename(columns={"Value": "RACM Cost"})

    out = first_vals.merge(cost, on="RACM ID")

    if "RACM ID Desc" in out.columns:
        out = out.drop(columns=["RACM ID Desc"])

    return out

# =========================================================
# ✅ FILE
# =========================================================
file = st.file_uploader("Upload Excel", type=["xlsx"])
if not file:
    st.stop()

df = pd.read_excel(file)

df.columns = [clean_text(c) for c in df.columns]
df["Region"] = df["Region"].apply(clean_text)

df["_row_id"] = range(len(df))

df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
df["RACM Qty"] = pd.to_numeric(df["RACM Qty"], errors="coerce")

df = compute_unit_rate(df)

# =========================================================
# ✅ REGION (BASED ON EMAIL)
# =========================================================
region = st.selectbox("Select Region", allowed_regions)

region_df = df[df["Region"] == region].copy()

# =========================================================
# ✅ FILTERS
# =========================================================
st.markdown("### Filters")

col1, col2 = st.columns(2)

# ---------------- Upload Index ----------------
with col1:

    upload_options = sorted(region_df["Upload Index"].astype(str).unique())

    search_upload = st.text_input("Search Upload Index").lower()

    upload_filtered = [x for x in upload_options if search_upload in x.lower()]

    b1, b2 = st.columns(2)

    if b1.button("Select All Upload"):
        st.session_state["upload"] = upload_filtered

    if b2.button("Clear Upload"):
        st.session_state["upload"] = []

    selected_upload = st.multiselect(
        "Upload Index",
        upload_filtered,
        default=st.session_state.get("upload", [])
    )

    st.session_state["upload"] = selected_upload

# ✅ Must select upload first
if not selected_upload:
    st.info("👉 Select Upload Index to proceed")
    st.stop()

df_upload = region_df[
    region_df["Upload Index"].astype(str).isin(selected_upload)
].copy()

# ---------------- RACM ID ----------------
with col2:

    racm_options = sorted(df_upload["RACM ID"].astype(str).unique())

    search_racm = st.text_input("Search RACM ID").lower()

    racm_filtered = [x for x in racm_options if search_racm in x.lower()]

    b3, b4 = st.columns(2)

    if b3.button("Select All RACM"):
        st.session_state["racm"] = racm_filtered

    if b4.button("Clear RACM"):
        st.session_state["racm"] = []

    selected_racm = st.multiselect(
        "RACM ID",
        racm_filtered,
        default=st.session_state.get("racm", [])
    )

    st.session_state["racm"] = selected_racm

# Apply filter
if selected_racm:
    filtered_df = df_upload[
        df_upload["RACM ID"].astype(str).isin(selected_racm)
    ].copy()
else:
    filtered_df = df_upload.copy()

# =========================================================
# ✅ SUMMARY
# =========================================================
st.markdown("### 📊 RACM Summary")
summary_df = compute_summary(filtered_df)
st.dataframe(summary_df, use_container_width=True)

# =========================================================
# ✅ EDITOR
# =========================================================
st.markdown("### ✏️ Edit Work Activity")

editor_df = filtered_df[["_row_id", "RACM ID", "Value", "RACM Qty"]]

edited = st.data_editor(
    editor_df,
    hide_index=True,
    use_container_width=True
)

# =========================================================
# ✅ MERGE BACK
# =========================================================
merged = filtered_df.merge(
    edited,
    on="_row_id",
    suffixes=("", "_new")
)

merged["Value"] = merged["Value_new"].fillna(merged["Value"])
merged["RACM Qty"] = merged["RACM Qty_new"].fillna(merged["RACM Qty"])

merged.drop(columns=["Value_new", "RACM Qty_new"], inplace=True)

merged["RACM Qty"] = merged.groupby("RACM ID")["RACM Qty"].transform("first")

# =========================================================
# ✅ RECALCULATE
# =========================================================
recalc = compute_unit_rate(merged)

# =========================================================
# ✅ WORK ACTIVITY
# =========================================================
st.markdown("### 🔧 Work Activity (Recalculated)")
st.dataframe(recalc.head(200), use_container_width=True)

# =========================================================
# ✅ RACM OUTPUT
# =========================================================
st.markdown("### 📊 RACM Output")

racm_output = compute_racm_output(recalc)

cols = ["RACM ID", "RACM Cost", "RACM Qty", "RACM Unit Rate"]

if "RACM UoM" in racm_output.columns:
    cols.append("RACM UoM")

st.dataframe(racm_output[cols], use_container_width=True)
