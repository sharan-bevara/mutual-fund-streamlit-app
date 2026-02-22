import streamlit as st
import pandas as pd

# App title
st.set_page_config(page_title="Mutual Fund Rank & Score", layout="centered")
st.title("📊 Mutual Fund Rank & Score Finder")

# Upload Excel file
uploaded_file = st.file_uploader(
    "Upload the Mutual Fund Excel file",
    type=["xlsx", "xls"]
)

if uploaded_file:
    try:
        # Read Excel
        df = pd.read_excel(uploaded_file)

        # Expected column names (edit if needed)
        FUND_COL = "Fund Name"
        RANK_COL = "Rank"
        SCORE_COL = "Score"

        # Validate required columns
        required_cols = {FUND_COL, RANK_COL, SCORE_COL}
        if not required_cols.issubset(df.columns):
            st.error(
                f"Excel file must contain columns: {', '.join(required_cols)}"
            )
        else:
            # Normalize fund names for search
            df[FUND_COL] = df[FUND_COL].astype(str)

            # User input
            fund_name = st.text_input("Enter Fund Name")

            if fund_name:
                # Case-insensitive match
                result = df[df[FUND_COL].str.lower() == fund_name.lower()]

                if not result.empty:
                    rank = result.iloc[0][RANK_COL]
                    score = result.iloc[0][SCORE_COL]

                    st.success("✅ Fund Found")
                    st.metric("Rank", rank)
                    st.metric("Score", score)

                else:
                    st.warning("⚠️ Fund name not found. Please check spelling.")

    except Exception as e:
        st.error(f"Error reading file: {e}")
