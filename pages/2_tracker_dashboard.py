import streamlit as st
import os
import pandas as pd
import plotly.express as px
import numpy as np
# import streamlit as📋 

# =========================================================
# FILE LOCATION
# =========================================================
FILE_PATH = r"C:\Users\pandeyv1581\Downloads\Tracker - Backend (1).xlsx"

if not os.path.exists(FILE_PATH):
    st.error(f"❌ File not found: {FILE_PATH}")
    st.stop()

# =========================================================
# CACHE SAFE LOADERS
# =========================================================
@st.cache_data
def get_sheet_names(path):
    return pd.ExcelFile(path).sheet_names

@st.cache_data
def load_sheet(path, sheet):
    df = pd.read_excel(path, sheet_name=sheet)
    df.columns = [str(c).strip() for c in df.columns]
    return df

sheet_names = get_sheet_names(FILE_PATH)

# =========================================================
# SHEET SELECTOR
# =========================================================
selected_sheet = st.selectbox("📄 Select Sheet", sheet_names)

df = load_sheet(FILE_PATH, selected_sheet)

st.markdown(f"### 📌 {selected_sheet}")

if df.empty:
    st.warning("No data in this sheet")
    st.stop()

# =========================================================
# HELPERS
# =========================================================
STATUS_COLORS = {
    "Completed": "#16a34a",      # green
    "In Progress": "#2563eb",    # blue
    "Not Started": "#f59e0b",    # amber
    "On Hold": "#7c3aed",        # violet
    "Cancelled": "#ef4444",      # red
    "Timeline asked": "#0ea5e9", # sky
    "Default": "#6b7280"         # gray
}

def normalize_status(val):
    s = str(val).strip()
    if not s or s.lower() == "nan":
        return "Unknown"
    return s

def status_color_lookup(status):
    status = normalize_status(status)
    for known, color in STATUS_COLORS.items():
        if known != "Default" and known.lower() in status.lower():
            return color
    return STATUS_COLORS["Default"]

def classify_sheet(df, sheet_name):
    cols = set(df.columns)

    # Task-type tracker sheets
    if "Task ID" in cols or "Status" in cols or "Assigned To" in cols:
        return "task"

    # Testing sheet pattern
    if "Testing use case" in cols or ("Status" in cols and "Remarks" in cols and "Section" in cols):
        return "testing"

    # Validation sheet pattern
    if "Validation" in cols and "Sub-Validation" in cols:
        return "validation"

    # Fallback by name if needed
    name_lower = sheet_name.lower()
    if "testing" in name_lower:
        return "testing"
    if "validation" in name_lower:
        return "validation"

    return "generic"

def parse_excel_date_series(series):
    """
    Handles mixed Excel serial dates + normal text dates.
    """
    s = series.copy()

    # First try normal datetime parse
    parsed = pd.to_datetime(s, errors="coerce")

    # For numeric Excel serials, fill missing values
    numeric = pd.to_numeric(s, errors="coerce")
    numeric_mask = numeric.notna() & parsed.isna()

    if numeric_mask.any():
        parsed.loc[numeric_mask] = pd.to_datetime(
            numeric.loc[numeric_mask],
            unit="D",
            origin="1899-12-30",
            errors="coerce"
        )

    return parsed

def apply_dynamic_filters(df):
    st.markdown("### 🔍 Filters")

    filters = {}
    filter_cols = st.columns(4)

    possible_filters = [
        "Status",
        "Priority",
        "Assigned To",
        "Task Name",
        "Section",
        "Level of Validation",
        "Validation"
    ]

    col_idx = 0
    for col_name in possible_filters:
        if col_name in df.columns:
            with filter_cols[col_idx % 4]:
                values = sorted(df[col_name].dropna().astype(str).unique())
                selected = st.multiselect(col_name, values, key=f"{selected_sheet}_{col_name}")
                if selected:
                    filters[col_name] = selected
            col_idx += 1

    filtered_df = df.copy()
    for col, vals in filters.items():
        filtered_df = filtered_df[
            filtered_df[col].astype(str).isin(vals)
        ]

    return filtered_df

def style_status_rows(df):
    """
    Row style for status-based coloring in dataframe.
    """
    def row_style(row):
        if "Status" not in row.index:
            return [""] * len(row)
        color = status_color_lookup(row["Status"])
        return [f"background-color: {color}20" if c == "Status" else "" for c in row.index]

    try:
        return df.style.apply(row_style, axis=1)
    except Exception:
        return df

# =========================================================
# SHEET TYPE
# =========================================================
sheet_type = classify_sheet(df, selected_sheet)

# =========================================================
# FILTERS
# =========================================================
filtered_df = apply_dynamic_filters(df)

# =========================================================
# SHEET-SPECIFIC KPI + CHARTS
# =========================================================
if sheet_type == "task":
    st.markdown("### 📊 KPI Summary")

    k1, k2, k3, k4, k5 = st.columns(5)

    total_rows = len(filtered_df)

    status_series = filtered_df["Status"].astype(str) if "Status" in filtered_df.columns else pd.Series(dtype="string")

    completed_count = len(filtered_df[status_series.str.contains("Completed", case=False, na=False)])
    in_progress_count = len(filtered_df[status_series.str.contains("Progress", case=False, na=False)])
    not_started_count = len(filtered_df[status_series.str.contains("Not", case=False, na=False)])

    overdue_count = 0
    overdue_df = pd.DataFrame()

    if "Due Date" in filtered_df.columns:
        work_df = filtered_df.copy()
        work_df["Due Date Parsed"] = parse_excel_date_series(work_df["Due Date"])

        if "Status" in work_df.columns:
            incomplete_mask = ~work_df["Status"].astype(str).str.contains("Completed", case=False, na=False)
        else:
            incomplete_mask = pd.Series([True] * len(work_df), index=work_df.index)

        overdue_df = work_df[
            work_df["Due Date Parsed"].notna() &
            incomplete_mask &
            (work_df["Due Date Parsed"] < pd.Timestamp.today().normalize())
        ].copy()

        overdue_count = len(overdue_df)

    k1.metric("Total Rows", total_rows)
    k2.metric("Completed", completed_count)
    k3.metric("In Progress", in_progress_count)
    k4.metric("Not Started", not_started_count)
    k5.metric("Overdue", overdue_count)

    st.markdown("### 📈 Charts")

    chart_row_1_col1, chart_row_1_col2 = st.columns(2)

    # Status chart
    if "Status" in filtered_df.columns:
        status_counts = (
            filtered_df["Status"]
            .apply(normalize_status)
            .value_counts(dropna=False)
            .reset_index()
        )
        status_counts.columns = ["Status", "Count"]
        status_counts["Color"] = status_counts["Status"].apply(status_color_lookup)

        fig_status = px.bar(
            status_counts,
            x="Status",
            y="Count",
            title="Status Distribution",
            text="Count",
            color="Status",
            color_discrete_map={s: status_color_lookup(s) for s in status_counts["Status"].tolist()}
        )
        fig_status.update_layout(showlegend=False)

        with chart_row_1_col1:
            st.plotly_chart(fig_status, use_container_width=True)

    # Priority chart
    if "Priority" in filtered_df.columns:
        priority_counts = (
            filtered_df["Priority"]
            .astype(str)
            .value_counts(dropna=False)
            .reset_index()
        )
        priority_counts.columns = ["Priority", "Count"]

        fig_priority = px.bar(
            priority_counts,
            x="Priority",
            y="Count",
            title="Priority Distribution",
            text="Count"
        )

        with chart_row_1_col2:
            st.plotly_chart(fig_priority, use_container_width=True)

    chart_row_2_col1, chart_row_2_col2 = st.columns(2)

    # Assignee chart
    if "Assigned To" in filtered_df.columns:
        assignee_counts = (
            filtered_df["Assigned To"]
            .astype(str)
            .value_counts(dropna=False)
            .reset_index()
        )
        assignee_counts.columns = ["Assigned To", "Count"]

        fig_assignee = px.bar(
            assignee_counts,
            x="Assigned To",
            y="Count",
            title="Tasks by Assignee",
            text="Count"
        )

        with chart_row_2_col1:
            st.plotly_chart(fig_assignee, use_container_width=True)

    # Status by assignee
    if "Assigned To" in filtered_df.columns and "Status" in filtered_df.columns:
        assignee_status = (
            filtered_df.groupby(["Assigned To", "Status"])
            .size()
            .reset_index(name="Count")
        )

        if not assignee_status.empty:
            fig_assignee_status = px.bar(
                assignee_status,
                x="Assigned To",
                y="Count",
                color="Status",
                title="Tasks by Assignee and Status",
                barmode="stack",
                color_discrete_map={s: status_color_lookup(s) for s in assignee_status["Status"].astype(str).unique()}
            )

            with chart_row_2_col2:
                st.plotly_chart(fig_assignee_status, use_container_width=True)

    # Overdue chart
    if not overdue_df.empty:
        st.markdown("### ⏳ Overdue Tasks")

        if "Assigned To" in overdue_df.columns:
            overdue_chart_df = (
                overdue_df.groupby("Assigned To")
                .size()
                .reset_index(name="Overdue Tasks")
            )
            fig_overdue = px.bar(
                overdue_chart_df,
                x="Assigned To",
                y="Overdue Tasks",
                title="Overdue Tasks by Assignee",
                text="Overdue Tasks",
                color_discrete_sequence=["#ef4444"]
            )
        elif "Task Name" in overdue_df.columns:
            overdue_chart_df = overdue_df.copy()
            fig_overdue = px.bar(
                overdue_chart_df.head(20),
                x="Task Name",
                y=[1] * min(len(overdue_chart_df), 20),
                title="Top Overdue Tasks",
                color_discrete_sequence=["#ef4444"]
            )
        else:
            overdue_chart_df = (
                overdue_df.groupby("Due Date Parsed")
                .size()
                .reset_index(name="Overdue Tasks")
            )
            fig_overdue = px.bar(
                overdue_chart_df,
                x="Due Date Parsed",
                y="Overdue Tasks",
                title="Overdue Tasks by Due Date",
                text="Overdue Tasks",
                color_discrete_sequence=["#ef4444"]
            )

        st.plotly_chart(fig_overdue, use_container_width=True)

elif sheet_type == "testing":
    st.markdown("### 📊 Testing Sheet KPIs")

    k1, k2, k3, k4 = st.columns(4)

    total_rows = len(filtered_df)
    completed_count = 0
    in_progress_count = 0
    not_started_count = 0

    if "Status" in filtered_df.columns:
        completed_count = len(filtered_df[
            filtered_df["Status"].astype(str).str.contains("Completed", case=False, na=False)
        ])
        in_progress_count = len(filtered_df[
            filtered_df["Status"].astype(str).str.contains("Progress", case=False, na=False)
        ])
        not_started_count = len(filtered_df[
            filtered_df["Status"].astype(str).str.contains("Not", case=False, na=False)
        ])

    k1.metric("Total Cases", total_rows)
    k2.metric("Completed", completed_count)
    k3.metric("In Progress", in_progress_count)
    k4.metric("Not Started", not_started_count)

    st.markdown("### 📈 Testing Charts")

    tcol1, tcol2 = st.columns(2)

    if "Status" in filtered_df.columns:
        test_status = (
            filtered_df["Status"].astype(str).value_counts().reset_index()
        )
        test_status.columns = ["Status", "Count"]

        fig_test_status = px.bar(
            test_status,
            x="Status",
            y="Count",
            title="Testing Status Distribution",
            text="Count",
            color="Status",
            color_discrete_map={s: status_color_lookup(s) for s in test_status["Status"].tolist()}
        )
        fig_test_status.update_layout(showlegend=False)

        with tcol1:
            st.plotly_chart(fig_test_status, use_container_width=True)

    if "Section" in filtered_df.columns:
        section_counts = (
            filtered_df["Section"].astype(str).value_counts().reset_index()
        )
        section_counts.columns = ["Section", "Count"]

        fig_section = px.bar(
            section_counts,
            x="Section",
            y="Count",
            title="Testing Cases by Section",
            text="Count"
        )

        with tcol2:
            st.plotly_chart(fig_section, use_container_width=True)

elif sheet_type == "validation":
    st.markdown("### 📊 Validation Sheet KPIs")

    k1, k2, k3 = st.columns(3)
    total_validations = len(filtered_df)
    unique_subvalidations = filtered_df["Sub-Validation"].nunique() if "Sub-Validation" in filtered_df.columns else 0
    unique_levels = filtered_df["Level of Validation"].nunique() if "Level of Validation" in filtered_df.columns else 0

    k1.metric("Total Validations", total_validations)
    k2.metric("Sub-Validations", unique_subvalidations)
    k3.metric("Validation Levels", unique_levels)

    st.markdown("### 📈 Validation Charts")

    vcol1, vcol2 = st.columns(2)

    if "Level of Validation" in filtered_df.columns:
        level_counts = (
            filtered_df["Level of Validation"].astype(str).value_counts().reset_index()
        )
        level_counts.columns = ["Level of Validation", "Count"]

        fig_level = px.bar(
            level_counts,
            x="Level of Validation",
            y="Count",
            title="Validations by Level",
            text="Count"
        )

        with vcol1:
            st.plotly_chart(fig_level, use_container_width=True)

    if "Validation" in filtered_df.columns:
        validation_counts = (
            filtered_df["Validation"].astype(str).value_counts().reset_index()
        )
        validation_counts.columns = ["Validation", "Count"]

        fig_validation = px.bar(
            validation_counts.head(20),
            x="Validation",
            y="Count",
            title="Top Validations",
            text="Count"
        )

        with vcol2:
            st.plotly_chart(fig_validation, use_container_width=True)

else:
    st.info("This sheet has a custom structure, so showing flexible filters and the data table without task-specific KPI charts.")

# =========================================================
# DATA TABLE
# =========================================================
st.markdown("### 📋 Data Table")

selected_columns = st.multiselect(
    "Select Columns",
    options=df.columns.tolist(),
    default=df.columns.tolist()[:10]
)

if selected_columns:
    display_df = filtered_df[selected_columns]
else:
    display_df = filtered_df

# Conditional styling only if Status exists
if "Status" in display_df.columns:
    st.dataframe(style_status_rows(display_df), use_container_width=True)
else:
    st.dataframe(display_df, use_container_width=True)

# =========================================================
# DEBUG
# =========================================================
with st.expander("🔍 Debug View"):
    st.write("Sheet type:", sheet_type)
    st.write("Columns:", df.columns.tolist())
    st.write("Rows:", len(df))
import pandas as pd
import os
import plotly.express as px
import numpy as np

st.set_page_config(layout="wide")
