import streamlit as st

st.set_page_config(page_title="Mutual Fund Rank & Score", layout="centered")
st.title("📊 Mutual Fund Rank & Score Finder")

st.markdown("### Select Fund Details")
st.write("")

# -------------------------------
# Scheme Type → Scheme Category mapping
# -------------------------------
scheme_category_map = {
    "Equity Scheme": [
        "Equity Scheme - Contra Fund",
        "Equity Scheme - Dividend Yield Fund",
        "Equity Scheme - ELSS",
        "Equity Scheme - Focused Fund",
        "Equity Scheme - Large Cap Fund",
        "Equity Scheme - Large & Mid Cap Fund",
        "Equity Scheme - Mid Cap Fund",
        "Equity Scheme - Multi Cap Fund",
        "Equity Scheme - Sectoral / Thematic",
        "Equity Scheme - Small Cap Fund",
        "Equity Scheme - Value Fund",
    ],
    "Debt Scheme": [
        "Debt Scheme - Banking and PSU Fund",
        "Debt Scheme - Corporate Bond Fund",
        "Debt Scheme - Credit Risk Fund",
        "Debt Scheme - Dynamic Bond",
        "Debt Scheme - Floater Fund",
        "Debt Scheme - Gilt Fund",
        "Debt Scheme - Gilt Fund with 10 year constant duration",
        "Debt Scheme - Liquid Fund",
        "Debt Scheme - Long Duration Fund",
        "Debt Scheme - Low Duration Fund",
        "Debt Scheme - Medium Duration Fund",
        "Debt Scheme - Medium to Long Duration Fund",
        "Debt Scheme - Money Market Fund",
        "Debt Scheme - Overnight Fund",
        "Debt Scheme - Short Duration Fund",
        "Debt Scheme - Ultra Short Duration Fund",
    ],
    "Hybrid Scheme": [
        "Hybrid Scheme - Arbitrage Fund",
        "Hybrid Scheme - Balanced Hybrid Fund",
        "Hybrid Scheme - Conservative Hybrid Fund",
        "Hybrid Scheme - Dynamic Asset Allocation or Balanced Advantage",
        "Hybrid Scheme - Equity Savings",
        "Hybrid Scheme - Multi Asset Allocation",
    ],
    "Other Scheme": [
        "Other Scheme - FoF Domestic",
        "Other Scheme - FoF Overseas",
        "Other Scheme - Gold ETF",
        "Other Scheme - Index Funds",
        "Other Scheme - Other ETFs",
    ],
    "Solution Oriented Scheme": [
        "Solution Oriented Scheme - Children’s Fund",
        "Solution Oriented Scheme - Retirement Fund",
    ],
}

# -------------------------------
# Scheme Type selectbox
# -------------------------------
scheme_type = st.selectbox(
    "Scheme Type",
    list(scheme_category_map.keys())
)

# -------------------------------
# Scheme Category selectbox (dependent)
# -------------------------------
scheme_category = st.selectbox(
    "Scheme Category",
    scheme_category_map[scheme_type]
)

# -------------------------------
# Fund Name
# -------------------------------
fund_name = st.selectbox(
    "Fund Name",
    [
        "ABC Equity Growth Fund",
        "XYZ Debt Opportunity Fund",
        "PQR Hybrid Advantage Fund"
    ]
)

st.divider()

# -------------------------------
# Submit
# -------------------------------
submit = st.button("🔍 Submit")

if submit:
    st.success("Fund Found ✅")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rank", "3")
    with col2:
        st.metric("Score", "87.45")

    st.divider()

    st.button("⬇️ Download Full Excel File")
