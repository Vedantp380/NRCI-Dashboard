import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Config
# -------------------------------
st.set_page_config(page_title="Issues Dashboard", layout="wide")

st.title("📊 Issues KPI Dashboard")

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    file = f"C:\\Users\\pandeyv1581\\Downloads\\Tracker - Backend_17062026.xlsx"
    df = pd.read_excel(file, sheet_name="Issues", engine="openpyxl")
    return df

df = load_data()

# Clean data
df = df[df["Issue ID"].notna()]

# -------------------------------
# KPI Calculations
# -------------------------------
total_issues = len(df)

failed_issues = len(df[df["Quality Status"] == "Failed"])

resolved_issues = df["Resolved by"].notna().sum()
open_issues = total_issues - resolved_issues

resolution_rate = (resolved_issues / total_issues) * 100 if total_issues > 0 else 0

technical_issues = len(df[df["Quality Issue Category"] == "Technical"])
data_issues = len(df[df["Quality Issue Category"] == "Data"])

workflow_issues = len(df[df["Quality Issue Sub Category"] == "Workflow"])

dependency_issues = len(df[df["Root Cause"] == "Dependency issue"])

# -------------------------------
# KPI Cards
# -------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Issues", total_issues)
col2.metric("Open Issues", open_issues)
col3.metric("Resolved Issues", resolved_issues)
col4.metric("Resolution Rate", f"{resolution_rate:.1f}%")

col5, col6, col7, col8 = st.columns(4)

col5.metric("Technical Issues", technical_issues)
col6.metric("Data Issues", data_issues)
col7.metric("Workflow Issues", workflow_issues)
col8.metric("Dependency Issues", dependency_issues)

st.markdown("---")

# -------------------------------
# Charts
# -------------------------------

# 1. Category Breakdown
st.subheader("📌 Issues by Category")
fig_cat = px.pie(
    df,
    names="Quality Issue Category",
    title="Issues Distribution by Category",
    hole=0.4
)
st.plotly_chart(fig_cat, use_container_width=True)

# 2. Stage Distribution
st.subheader("⚙️ Issues by Stage")
stage_df = df["Issue Stage"].value_counts().reset_index()
stage_df.columns = ["Stage", "Count"]

fig_stage = px.bar(
    stage_df,
    x="Stage",
    y="Count",
    title="Issues per Stage",
    color="Stage"
)
st.plotly_chart(fig_stage, use_container_width=True)

# 3. Root Cause Analysis
st.subheader("🔍 Root Cause Analysis")
root_df = df["Root Cause"].value_counts().reset_index()
root_df.columns = ["Root Cause", "Count"]

fig_root = px.bar(
    root_df,
    x="Root Cause",
    y="Count",
    title="Issues by Root Cause",
    color="Root Cause"
)
st.plotly_chart(fig_root, use_container_width=True)

# 4. Sub Category
st.subheader("📊 Issue Sub Categories")
sub_df = df["Quality Issue Sub Category"].value_counts().reset_index()
sub_df.columns = ["Sub Category", "Count"]

fig_sub = px.bar(
    sub_df,
    x="Sub Category",
    y="Count",
    title="Sub Category Distribution",
    color="Sub Category"
)
st.plotly_chart(fig_sub, use_container_width=True)

st.markdown("---")

# -------------------------------
# Detailed Table
# -------------------------------
st.subheader("📋 Issue Register")

st.dataframe(
    df[[
        "Issue ID",
        "Issue Name",
        "Issue Stage",
        "Quality Issue Category",
        "Quality Issue Sub Category",
        "Root Cause",
        "Raised by",
        "Resolved by"
    ]],
    use_container_width=True
)

# -------------------------------
# Insights Section
# -------------------------------
st.subheader("💡 Auto Insights")

if total_issues > 0:
    insights = []

    if technical_issues > data_issues:
        insights.append("⚠️ Majority of issues are Technical — focus on backend stability")

    if workflow_issues > 0:
        insights.append("🔁 Workflow issues are dominant — review process orchestration")

    if dependency_issues > 0:
        insights.append("🔗 Dependency issues detected — improve inter-system communication")

    if open_issues > resolved_issues:
        insights.append("🚨 More open issues than resolved — backlog needs attention")

    if len(insights) == 0:
        insights.append("✅ No major issue trends detected")

    for i in insights:
        st.write(i)
else:
    st.write("No issues data available to generate insights.")