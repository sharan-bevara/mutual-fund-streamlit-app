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
# Load Excel / CSV
# ----------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("/mnt/data/SchemeData2301262313SS.csv")

df = load_data()

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

st.divider()

# ----------------------------------
# Submit Button
# ----------------------------------
submit = st.button("🔍 Submit")

if submit:
    if scheme_type == "Select Scheme Type":
        st.warning("Please select Scheme Type and Scheme Category")
    else:
        # ----------------------------------
        # Combine user selection
        # ----------------------------------
        combined_category = f"{scheme_type} - {scheme_category}"

        # ----------------------------------
        # Search in Excel (Scheme Category column)
        # ----------------------------------
        filtered_df = df[
            df["Scheme Category"].str.strip() == combined_category
        ]

        if filtered_df.empty:
            st.error("No schemes found for the selected criteria ❌")
        else:
            st.success(f"Found {len(filtered_df)} schemes ✅")

            # ----------------------------------
            # Display Scheme NAV Names
            # ----------------------------------
            st.markdown("### 📌 Scheme NAV Names")
            st.dataframe(
                filtered_df[["Scheme NAV Name"]].drop_duplicates(),
                use_container_width=True
            )

            st.divider()

            # ----------------------------------
            # Download Button
            # ----------------------------------
            st.download_button(
                "⬇️ Download Filtered Excel",
                data=filtered_df.to_csv(index=False),
                file_name="filtered_schemes.csv",
                mime="text/csv"
            )
