import streamlit as st
import pandas as pd

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(page_title="Mutual Fund Rank & Score", layout="centered")
st.title("📊 Mutual Fund Rank & Score Finder")

st.markdown("### Select Fund Details")
st.write("")

# ----------------------------------
# Load Excel / CSV files
# ----------------------------------
@st.cache_data
def load_scheme_master():
    return pd.read_csv("SchemeData2301262313SS.csv")

@st.cache_data
def load_fund_details():
    return pd.read_excel("MutualFund_Final_Output 16.xlsx")

scheme_df = load_scheme_master()      # For NAV names
details_df = load_fund_details()      # For final details

# ----------------------------------
# Scheme Type → Scheme Category mapping
# ----------------------------------
scheme_category_map = {
    "Equity Scheme": [
        "Contra Fund", "Dividend Yield Fund", "ELSS", "Focused Fund",
        "Large Cap Fund", "Large & Mid Cap Fund", "Mid Cap Fund",
        "Multi Cap Fund", "Sectoral / Thematic", "Small Cap Fund",
        "Value Fund",
    ],
    "Debt Scheme": [
        "Banking and PSU Fund", "Corporate Bond Fund", "Credit Risk Fund",
        "Dynamic Bond", "Floater Fund", "Gilt Fund",
        "Gilt Fund with 10 year constant duration", "Liquid Fund",
        "Long Duration Fund", "Low Duration Fund", "Medium Duration Fund",
        "Medium to Long Duration Fund", "Money Market Fund",
        "Overnight Fund", "Short Duration Fund", "Ultra Short Duration Fund",
    ],
    "Hybrid Scheme": [
        "Arbitrage Fund", "Balanced Hybrid Fund",
        "Conservative Hybrid Fund",
        "Dynamic Asset Allocation or Balanced Advantage",
        "Equity Savings", "Multi Asset Allocation",
    ],
    "Other Scheme": [
        "FoF Domestic", "FoF Overseas", "Gold ETF",
        "Index Funds", "Other ETFs",
    ],
    "Solution Oriented Scheme": [
        "Children’s Fund", "Retirement Fund",
    ],
}

# ----------------------------------
# Scheme Type & Category
# ----------------------------------
col1, col2 = st.columns(2)

with col1:
    scheme_type = st.selectbox(
        "Scheme Type",
        ["Select Scheme Type"] + list(scheme_category_map.keys())
    )

with col2:
    if scheme_type != "Select Scheme Type":
        scheme_category = st.selectbox(
            "Scheme Category",
            scheme_category_map[scheme_type]
        )
    else:
        scheme_category = st.selectbox(
            "Scheme Category",
            ["Select Scheme Type first"]
        )

# ----------------------------------
# Get Scheme NAV Names from CSV
# ----------------------------------
scheme_nav_names = []

if scheme_type != "Select Scheme Type":
    combined_category = f"{scheme_type} - {scheme_category}".strip().lower()

    nav_df = scheme_df[
        scheme_df["Scheme Category"]
        .astype(str)
        .str.strip()
        .str.lower()
        == combined_category
    ]

    scheme_nav_names = (
        nav_df["Scheme NAV Name"]
        .dropna()
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

scheme_nav_name = st.selectbox(
    "Scheme NAV Name",
    ["Select Scheme NAV Name"] + scheme_nav_names
)

st.divider()

# ----------------------------------
# Submit
# ----------------------------------
submit = st.button("🔍 Submit")

if submit:
    if scheme_nav_name == "Select Scheme NAV Name":
        st.warning("Please select Scheme Type, Category, and NAV Name")
    else:
        # ----------------------------------
        # Search FINAL Excel using NAV Name
        # ----------------------------------
        final_df = details_df[
            details_df["Scheme NAV Name"]
            .astype(str)
            .str.strip()
            == scheme_nav_name
        ]

        if final_df.empty:
            st.error("No fund details found ❌")
        else:
            st.success("Fund details found ✅")
            st.markdown("### 📄 Fund Details")
            st.dataframe(final_df, use_container_width=True)

            st.divider()

            st.download_button(
                "⬇️ Download Fund Details",
                data=final_df.to_csv(index=False),
                file_name=f"{scheme_nav_name}.csv",
                mime="text/csv"
            )
