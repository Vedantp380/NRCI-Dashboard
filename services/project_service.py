import pandas as pd

# =========================
# LOAD FILE
# =========================
import pandas as pd

def load_project_file(uploaded_file):
    try:
        file_name = uploaded_file.name.lower()

        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")

        else:
            raise ValueError("Unsupported file format")

        return df

    except Exception as e:
        raise ValueError(f"""
❌ Uploaded file is not a valid CSV or Excel file.

👉 Please upload:
- Proper .csv OR
- Proper .xlsx (not renamed file)

Error: {str(e)}
""")
    

import streamlit as st

# =========================
# FILE UPLOAD (ADD HERE ✅)
# =========================
uploaded_file = st.file_uploader(
    "Upload Project File",
    type=["csv", "xlsx"]
)

# Stop if no file
if uploaded_file is None:
    st.warning("Please upload a file")
    st.stop()



# =========================
# CLEAN + MAP DATA
# =========================
def prepare_project_library_data(uploaded_file, inflation_mode="cpi"):

    df = load_project_file(uploaded_file)

    # ✅ BASIC CLEANING
    df.columns = [c.strip() for c in df.columns]

    # =========================
    # COLUMN MAPPING
    # =========================
    if "Project_ID" in df.columns:
        df["Project ID"] = df["Project_ID"]
    elif "Oracle Projects (OP) Number" in df.columns:
        df["Project ID"] = df["Oracle Projects (OP) Number"]
    else:
        df["Project ID"] = df.index

    df["Project Name"] = df.get("Project Name", "")
    df["Project ID Display"] = df["Project ID"].astype(str) + " - " + df["Project Name"].astype(str)

    df["Region"] = df.get("Region", "")
    df["Basis of Costs"] = df.get("Basis of Costs", "")
    df["Scheme Type"] = df.get("Scheme Type", "")
    df["Funding Category"] = df.get("Funding Type", "")

    # =========================
    # BASE DATE
    # =========================
    if "Base Date" in df.columns:
        df["Base Date Parsed"] = pd.to_datetime(df["Base Date"], errors="coerce")
    else:
        df["Base Date Parsed"] = pd.NaT

    df["Base Date"] = df.get("Base Date", "")

    # =========================
    # PITG %
    # =========================
    if "PITG%" in df.columns:
        df["PITG Numeric"] = pd.to_numeric(df["PITG%"], errors="coerce")
    else:
        df["PITG Numeric"] = None

    df["PITG %"] = df["PITG Numeric"].astype(str) + "%"

    # =========================
    # PROJECT COST
    # =========================
    if "AFC" in df.columns:
        df["Project Cost Numeric"] = pd.to_numeric(df["AFC"], errors="coerce")
    else:
        df["Project Cost Numeric"] = 0

    df["Project Cost"] = df["Project Cost Numeric"].apply(
        lambda x: f"£{int(x):,}" if pd.notna(x) else ""
    )

    # =========================
    # INFLATED COST
    # =========================
    if "Inflation" in df.columns and inflation_mode == "cpi":
        df["Inflation"] = pd.to_numeric(df["Inflation"], errors="coerce")
        df["Inflated Project Cost Numeric"] = df["Project Cost Numeric"] * df["Inflation"]
    else:
        df["Inflated Project Cost Numeric"] = df["Project Cost Numeric"]

    df["Inflated Project Cost"] = df["Inflated Project Cost Numeric"].apply(
        lambda x: f"£{int(x):,}" if pd.notna(x) else ""
    )

    return df