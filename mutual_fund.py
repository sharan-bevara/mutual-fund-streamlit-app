import streamlit as st

st.set_page_config(page_title="Mutual Fund Rank & Score", layout="centered")
st.title("📊 Mutual Fund Rank & Score Finder")

st.markdown("### Select Fund Details")

# 🔘 Scheme Type
scheme_type = st.selectbox(
    "Scheme Type",
    ["Open Ended", "Close Ended"]
)

# 🔽 Scheme Category
scheme_category = st.selectbox(
    "Scheme Category",
    ["Equity Scheme", "Debt Scheme", "Hybrid Scheme"]
)

# 🔽 Fund Name (placeholder values)
fund_name = st.selectbox(
    "Fund Name",
    [
        "ABC Equity Growth Fund",
        "XYZ Debt Opportunity Fund",
        "PQR Hybrid Advantage Fund"
    ]
)

st.divider()

# 📊 Result section (static preview)
st.success("Fund Found ✅")

col1, col2 = st.columns(2)
with col1:
    st.metric("Rank", "3")
with col2:
    st.metric("Score", "87.45")

st.divider()

# ⬇️ Download button (disabled preview)
st.button("⬇️ Download Full Excel File", disabled=True)
