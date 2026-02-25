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
        "Contra Fund",
        "Dividend Yield Fund",
        "ELSS",
        "Focused Fund",
        "Large Cap Fund",
        "Large & Mid Cap Fund",
        "Mid Cap Fund",
        "Multi Cap Fund",
        "Sectoral / Thematic",
        "Small Cap Fund",
        "Value Fund",
    ],
    "Debt Scheme": [
        "Banking and PSU Fund",
        "Corporate Bond Fund",
        "Credit Risk Fund",
        "Dynamic Bond",
        "Floater Fund",
        "Gilt Fund",
        "Gilt Fund with 10 year constant duration",
        "Liquid Fund",
        "Long Duration Fund",
        "Low Duration Fund",
        "Medium Duration Fund",
        "Medium to Long Duration Fund",
        "Money Market Fund",
        "Overnight Fund",
        "Short Duration Fund",
        "Ultra Short Duration Fund",
    ],
    "Hybrid Scheme": [
        "Arbitrage Fund",
        "Balanced Hybrid Fund",
        "Conservative Hybrid Fund",
        "Dynamic Asset Allocation or Balanced Advantage",
        "Equity Savings",
        "Multi Asset Allocation",
    ],
    "Other Scheme": [
        "FoF Domestic",
        "FoF Overseas",
        "Gold ETF",
        "Index Funds",
        "Other ETFs",
    ],
    "Solution Oriented Scheme": [
        "Children’s Fund",
        "Retirement Fund",
    ],
}

# -------------------------------
# Side-by-side selection boxes
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    scheme_type = st.selectbox(
        "Scheme Type",
        list(scheme_category_map.keys())
    )

with col2:
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
