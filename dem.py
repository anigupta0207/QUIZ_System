import streamlit as st
import pandas as pd
import altair as alt

# ---------- Force Streamlit to stay in light mode ----------
st.set_page_config(
    page_title="Mint Green Dashboard (Fully Light)",
    page_icon="🌿",
    layout="wide",
)

# ---------- Sample Data ----------
data = pd.DataFrame({
    "Subject": ["C", "Python", "HTML", "CSS", "JavaScript"],
    "Attempts": [25, 40, 15, 10, 30]
})

# ---------- Custom CSS ----------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #ecfdf5 0%, #f9fffb 100%);
    color: #1e293b;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background: #d1fae5;
}
.navbar {
    background: linear-gradient(90deg, #059669, #10b981);
    color: white;
    padding: 16px 30px;
    font-size: 22px;
    font-weight: 700;
    border-radius: 14px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(16,185,129,0.3);
}
.card {
    background: #ffffff;
    border-radius: 16px;
    padding: 25px;
    margin-bottom: 20px;
    border: 1px solid #a7f3d0;
    box-shadow: 0 4px 10px rgba(16,185,129,0.08);
}
.metric-box {
    text-align: center;
    background: linear-gradient(135deg, #d1fae5, #ecfdf5);
    border: 1px solid #a7f3d0;
    border-radius: 14px;
    padding: 18px 10px;
    margin: 8px 0;
}
.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #059669;
}
.metric-label {
    font-size: 15px;
    color: #475569;
}
h1, h2, h3, h4 {
    color: #059669;
    font-weight: 700;
}
button {
    background-color: #10b981 !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 8px 18px !important;
}
button:hover {
    background-color: #059669 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("<div class='navbar'>🌿 Mint Green Dashboard — Locked Light Theme</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ---------- Metrics ----------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<div class='metric-box'><div class='metric-value'>32.79%</div><div class='metric-label'>Similarity Score</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='metric-box'><div class='metric-value'>13/42</div><div class='metric-label'>Skills Match</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='metric-box'><div class='metric-value'>0 years</div><div class='metric-label'>Experience</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown("<div class='metric-box'><div class='metric-value'>Bachelor’s</div><div class='metric-label'>Education</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------- Chart ----------
st.markdown("<div class='card'><h3>📊 Subject Attempt Distribution</h3>", unsafe_allow_html=True)

chart = (
    alt.Chart(data, background="#ffffff")  # Force white chart background
    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X("Subject", sort=None),
        y="Attempts",
        color=alt.value("#10b981")
    )
    .configure_axis(
        gridColor="#e5e7eb",
        labelColor="#374151",
        titleColor="#374151"
    )
    .configure_view(
        strokeOpacity=0,
        fill="#ffffff"   # Keep chart white even in dark mode
    )
    .configure_title(
        color="#059669"
    )
)
st.altair_chart(chart, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ---------- Table ----------
st.markdown("<div class='card'><h3>🧑‍💻 User Scores</h3>", unsafe_allow_html=True)

sample_df = pd.DataFrame({
    "Username": ["Arshita", "Rahul", "Priya", "Aman", "Neha"],
    "Score": [95, 88, 90, 84, 92],
    "Quiz": ["Python", "C", "HTML", "CSS", "JS"]
})

# Custom HTML table (to avoid Streamlit theme override)
table_html = sample_df.to_html(index=False, classes='table table-striped', border=0)
st.markdown(f"""
<div style="
    background:white;
    border:1px solid #a7f3d0;
    border-radius:12px;
    box-shadow:0 4px 10px rgba(16,185,129,0.1);
    padding:15px;
">
{table_html}
</div>
""", unsafe_allow_html=True)

st.markdown("<center>✨ Mint Green Dashboard — Everything Light & Consistent ✨</center>", unsafe_allow_html=True)
