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
# Load Data
# ----------------------------------
@st.cache_data
def load_scheme_data():
    df = pd.read_csv("SchemeData2301262313SS.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

@st.cache_data
def load_fund_details():
    df = pd.read_excel("MutualFund_Final_Output 16.xlsx")
    df.columns = df.columns.str.strip().str.lower()
    return df

scheme_df = load_scheme_data()
details_df = load_fund_details()

# ----------------------------------
# Scheme Type → Scheme Category mapping
# ----------------------------------
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

# ----------------------------------
# Side-by-side Selectboxes
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
# Scheme NAV Name (Dynamic)
# ----------------------------------
scheme_nav_name = None

if scheme_type != "Select Scheme Type":
    combined_category = f"{scheme_type} - {scheme_category}".lower()

    nav_df = scheme_df[
        scheme_df["scheme category"].str.strip().str.lower() == combined_category
    ]

    nav_names = sorted(
        nav_df["scheme nav name"]
        .dropna()
        .unique()
        .tolist()
    )

    if nav_names:
        scheme_nav_name = st.selectbox(
            "Scheme NAV Name",
            nav_names
        )
    else:
        st.warning("No Scheme NAV Names found")

st.divider()

# ----------------------------------
# Submit Button
# ----------------------------------
submit = st.button("🔍 Submit")

if submit:
    if not scheme_nav_name:
        st.warning("Please complete all selections")
    else:
        selected_fund = scheme_nav_name.strip().lower()

        # ----------------------------------
        # Search Fund Name in Details Excel
        # ----------------------------------
        final_df = details_df[
            details_df["fund name"].str.strip().str.lower() == selected_fund
        ]

        if final_df.empty:
            st.error("No fund details found ❌")
        else:
            st.success("Fund details found ✅")

            # ----------------------------------
            # Display Results
            # ----------------------------------
            st.dataframe(final_df, use_container_width=True)

            st.divider()

            st.download_button(
                "⬇️ Download Fund Details",
                data=final_df.to_csv(index=False),
                file_name="selected_fund_details.csv",
                mime="text/csv"
            )
