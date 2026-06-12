import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# =========================================================
# TITLE
# =========================================================
st.title("📂 XLSM Structured Model")

# =========================================================
# FILE UPLOAD
# =========================================================
uploaded_file = st.file_uploader("Upload XLSM file", type=["xlsm"])

if uploaded_file is None:
    st.stop()

xls = pd.ExcelFile(uploaded_file, engine="openpyxl")

# =========================================================
# CONFIG (YOUR RULE ✅)
# =========================================================
sheet_config = {
    "Asset Questions": ("C", "G", 5),
    "Asset Sub-Component Questions": ("C", "I", 5),
    "Technical Parameters": ("C", "K", 6),
    "Key Volume Lines (KVL)": ("C", "M", 7),
    "Asset Summary": ("C", "J", 6),
    "Asset Sub Component Summary": ("C", "N", 6),
    "Work Activity Summary": ("C", "S", 6)
}

# =========================================================
# HELPERS
# =========================================================
def col_to_index(col):
    return ord(col.upper()) - 65


def make_arrow_safe(df):
    for col in df.columns:
        try:
            df[col] = df[col].astype("string")
        except:
            df[col] = df[col].astype(str)
    return df


# =========================================================
# ICA PROCESS
# =========================================================
def process_indirect_cost():

    raw_df = pd.read_excel(xls, sheet_name="Indirect Cost Allocation", header=None)

    raw_df = raw_df.dropna(how="all").reset_index(drop=True)

    labels = raw_df.iloc[:, 0]
    data = raw_df.iloc[:, 1:]

    records = []

    for col in data.columns:

        if data[col].isna().all():
            continue

        record = {}

        for i, label in enumerate(labels):

            label = str(label).strip()
            val = data.iloc[i, col]

            if label and label != "nan" and pd.notna(val):
                record[label] = val

        if len(record) > 0:
            records.append(record)

    df = pd.DataFrame(records)

    df = df.dropna(axis=1, how="all")

    return df


# =========================================================
# STRUCTURED READ
# =========================================================
def read_structured_sheet(sheet):

    start_col, end_col, header_row = sheet_config[sheet]

    raw_df = pd.read_excel(xls, sheet_name=sheet, header=None)

    start = col_to_index(start_col)
    end = col_to_index(end_col)

    headers = raw_df.iloc[header_row - 1, start:end + 1]

    df = raw_df.iloc[header_row:, start:end + 1].copy()

    df.columns = [str(c).strip() for c in headers]

    df = df.dropna(axis=1, how="all")
    df = df.dropna(how="all").reset_index(drop=True)

    return df


# =========================================================
# SELECT SHEET
# =========================================================
all_sheets = list(sheet_config.keys()) + ["Indirect Cost Allocation"]

selected_sheet = st.selectbox("Select Sheet", all_sheets)

# =========================================================
# LOAD DATA
# =========================================================
try:
    if selected_sheet == "Indirect Cost Allocation":
        df = process_indirect_cost()
    else:
        df = read_structured_sheet(selected_sheet)

except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

if df.empty:
    st.error("No data found")
    st.stop()

df = make_arrow_safe(df)

# =========================================================
# METRICS
# =========================================================
c1, c2, c3 = st.columns(3)
c1.metric("Rows", len(df))
c2.metric("Columns", len(df.columns))
c3.metric("Missing", int(df.isna().sum().sum()))

# =========================================================
# ✅ EDITABLE LOGIC (ONLY THESE 2 SHEETS)
# =========================================================
editable_sheets = [
    "Asset Questions",
    "Asset Sub-Component Questions"
]

if selected_sheet in editable_sheets:

    if "Required" in df.columns and "Answer" in df.columns:

        # ✅ Filter required rows
        df_filtered = df[df["Required"].astype(str).str.strip() != "Required"]

        st.subheader("✏️ Editable Answer (Required Only)")

        edited_df = st.data_editor(
            df_filtered,
            disabled=[col for col in df_filtered.columns if col != "Answer"],
            width="stretch"
        )

        df = edited_df

    else:
        st.warning("Required or Answer column not found")

# =========================================================
# COLUMN SELECTOR
# =========================================================
st.subheader("🧩 Select Columns")

if len(df.columns) == 0:
    st.error("No columns available")
    st.stop()

selected_cols = st.multiselect(
    "Choose columns",
    options=list(df.columns),
    default=list(df.columns)[:5]
)

if not selected_cols:
    st.stop()

# =========================================================
# PREVIEW
# =========================================================
st.subheader(f"📋 Preview: {selected_sheet}")

st.dataframe(
    df[selected_cols].head(200),
    width="stretch"
)