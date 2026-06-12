
import streamlit as st
import pandas as pd
import plotly.express as px

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(layout="wide")
st.title("🌍 SDG Geospatial Analytics Dashboard")

# ======================================================
# LOAD DATA
# ======================================================
DATA_PATH = r"C:\Users\pandeyv1581\Downloads\sdg_index_2000-2022.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    # normalize columns
    df.columns = df.columns.str.lower().str.strip()

    return df

df = load_data()

# ======================================================
# VALIDATION
# ======================================================
required_cols = ["country", "country_code", "year"]

for col in required_cols:
    if col not in df.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

# dynamic score columns
score_cols = [col for col in df.columns if "score" in col]

# ======================================================
# SIDEBAR FILTERS
# ======================================================
st.sidebar.header("Filters")

year = st.sidebar.selectbox(
    "Select Year",
    sorted(df["year"].dropna().unique(), reverse=True)
)

goal = st.sidebar.selectbox(
    "Select Metric",
    score_cols
)

filtered_df = df[df["year"] == year].copy()
filtered_df = filtered_df.dropna(subset=[goal])

# ======================================================
# ================= INSIGHT ENGINE ======================
# ======================================================

def generate_insights(df, goal, year):
    insights = []

    avg_score = df[goal].mean()
    max_country = df.loc[df[goal].idxmax(), "country"]
    min_country = df.loc[df[goal].idxmin(), "country"]

    insights.append(f"Global average **{goal}** is **{avg_score:.2f}** in {year}.")
    insights.append(f"Top performer: **{max_country}**, lowest: **{min_country}**.")

    gap = df[goal].max() - df[goal].min()
    insights.append(f"Performance gap is **{gap:.2f} points**, indicating inequality.")

    if avg_score > 75:
        insights.append("Global performance is strong.")
    elif avg_score > 60:
        insights.append("Moderate progress with improvement potential.")
    else:
        insights.append("Global performance is uneven and needs attention.")

    return insights


def smart_insight(df, goal):
    avg = df[goal].mean()

    if avg > 75:
        return "✅ Most countries are performing strongly on this goal."
    elif avg > 60:
        return "⚠️ Moderate performance — some countries lag behind."
    else:
        return "❌ Significant challenges exist globally."

# ======================================================
# ================= KPI EXECUTIVE =======================
# ======================================================

st.subheader("📊 Executive Summary")

col1, col2, col3 = st.columns(3)

avg_val = filtered_df[goal].mean()
max_val = filtered_df[goal].max()
min_val = filtered_df[goal].min()

col1.metric("Global Avg", f"{avg_val:.2f}")
col2.metric("Best Score", f"{max_val:.2f}")
col3.metric("Lowest Score", f"{min_val:.2f}")

st.markdown("### 🧠 Key Insight")
st.info(generate_insights(filtered_df, goal, year)[0])

st.markdown("### 🌍 Insight Engine")
st.warning(smart_insight(filtered_df, goal))

# ======================================================
# ================= MAP ================================
# ======================================================

st.subheader("🌍 Global Map")

fig_map = px.choropleth(
    filtered_df,
    locations="country_code",
    color=goal,
    hover_name="country",
    color_continuous_scale="RdYlGn",
    title=f"{goal.upper()} ({year})"
)

st.plotly_chart(fig_map, use_container_width=True)

# ======================================================
# ================= STORYTELLING =======================
# ======================================================

st.subheader("📖 Global Storytelling")

insights = generate_insights(filtered_df, goal, year)

for ins in insights:
    st.write(f"👉 {ins}")

# ======================================================
# ================= TOP / BOTTOM =======================
# ======================================================

st.subheader("🏆 Performance Ranking")

col1, col2 = st.columns(2)

top5 = filtered_df.sort_values(goal, ascending=False).head(5)
bottom5 = filtered_df.sort_values(goal).head(5)

with col1:
    st.markdown("**Top 5 Countries**")
    st.dataframe(top5[["country", goal]])

with col2:
    st.markdown("**Bottom 5 Countries**")
    st.dataframe(bottom5[["country", goal]])

# ======================================================
# ================= TREND ==============================
# ======================================================

st.subheader("📈 Country Trend")

country = st.selectbox(
    "Select Country",
    sorted(df["country"].dropna().unique())
)

country_df = df[df["country"] == country]

fig_trend = px.line(
    country_df,
    x="year",
    y=goal,
    markers=True,
    title=f"{country} - {goal}"
)

st.plotly_chart(fig_trend, use_container_width=True)

# ======================================================
# ================= IMPROVEMENT ========================
# ======================================================

st.subheader("🚀 Improvement Analysis")

df_start = df[df["year"] == df["year"].min()]
df_end = df[df["year"] == df["year"].max()]

merged = df_start[["country", goal]].merge(
    df_end[["country", goal]],
    on="country",
    suffixes=("_start", "_end")
)

merged["improvement"] = merged[f"{goal}_end"] - merged[f"{goal}_start"]

top_improvers = merged.sort_values("improvement", ascending=False).head(5)

st.write("Top Improving Countries")
st.dataframe(top_improvers[["country", "improvement"]])

if not top_improvers.empty:
    st.success(
        f"Countries like **{top_improvers.iloc[0]['country']}** show strong long-term improvement."
    )

# ======================================================
# ================= HEATMAP ============================
# ======================================================

st.subheader("🌡️ Heatmap (Country vs Year)")

pivot_df = df.pivot_table(
    index="country",
    columns="year",
    values=goal
)

fig_heatmap = px.imshow(
    pivot_df,
    aspect="auto",
    color_continuous_scale="RdYlGn"
)

st.plotly_chart(fig_heatmap, use_container_width=True)
