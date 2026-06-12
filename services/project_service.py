import pandas as pd


# =========================================================
# LOAD FILE
# =========================================================
def load_project_file(uploaded_file):

    file_name = uploaded_file.name.lower()

    # ✅ Try CSV first
    try:
        df = pd.read_csv(uploaded_file)
        return df
    except:
        pass

    uploaded_file.seek(0)

    # ✅ Try Excel
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        return df
    except:
        pass

    uploaded_file.seek(0)

    raise ValueError("❌ Invalid file. Upload proper CSV or Excel")


# =========================================================
# MAIN FUNCTION
# =========================================================
def prepare_project_library_data(uploaded_file, inflation_mode="cpi"):

    df = load_project_file(uploaded_file)

    # ✅ Clean column names
    df.columns = [c.strip() for c in df.columns]

    # ====================================================
    # ✅ CONVERT NUMERIC
    # ====================================================
    df["Total Cost"] = pd.to_numeric(df["Total Cost"], errors="coerce")

    # ====================================================
    # ✅ AGGREGATE PROJECT LEVEL (CRITICAL FIX ✅)
    # ====================================================
    project_df = df.groupby(
        [
            "Project_ID",
            "Upload Index",   # ✅ version control
            "Project Name",
            "Oracle Projects (OP) Number",
            "Base Date"
        ],
        as_index=False
    ).agg({
        "Total Cost": "sum"
    })

    # ====================================================
    # ✅ PROJECT ID + DISPLAY
    # ====================================================
    project_df["Project ID"] = project_df["Project_ID"]

    project_df["Project ID Display"] = (
        project_df["Project_ID"].astype(str)
        + " | Upload: " + project_df["Upload Index"].astype(str)
        + " - " + project_df["Project Name"]
    )

    # ====================================================
    # ✅ COST LOGIC
    # ====================================================
    project_df["Project Cost Numeric"] = project_df["Total Cost"]

    project_df["Project Cost"] = project_df["Project Cost Numeric"].apply(
        lambda x: f"£{int(x):,}" if pd.notna(x) else ""
    )

    # ✅ For now inflation same as cost
    project_df["Inflated Project Cost Numeric"] = project_df["Project Cost Numeric"]

    project_df["Inflated Project Cost"] = project_df["Project Cost"]

    # ====================================================
    # ✅ BASE DATE
    # ====================================================
    project_df["Base Date Parsed"] = pd.to_datetime(
        project_df["Base Date"], errors="coerce"
    )

    project_df["year"] = project_df["Base Date Parsed"].dt.year

    # ====================================================
    # ✅ DEFAULT FIELDS (for UI compatibility)
    # ====================================================
    project_df["Region"] = "Unknown"
    project_df["Basis of Costs"] = "Estimate"
    project_df["Scheme Type"] = "Default"
    project_df["PITG %"] = "0%"

    return project_df