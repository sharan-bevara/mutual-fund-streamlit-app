import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mutual Fund Rank & Score", layout="centered")
st.title("📊 Mutual Fund Rank & Score Finder")

FILE_PATH = "data/MutualFund_Final_Output 16.xlsx"

@st.cache_data
def load_data(path):
    return pd.read_excel(path)

try:
    df = load_data(FILE_PATH)

    FUND_COL = "Fund Name"
    SCHEME_TYPE_COL = "Scheme Type"
    SCHEME_CAT_COL = "Scheme Category"
    RANK_COL = "Rank"
    SCORE_COL = "Score"

    # Validate required columns
    required_cols = {
        FUND_COL,
        SCHEME_TYPE_COL,
        SCHEME_CAT_COL,
        RANK_COL,
        SCORE_COL
    }
    if not required_cols.issubset(df.columns):
        st.error("Required columns missing in Excel file.")
        st.stop()

    # 🔽 Scheme Type (fixed options)
    scheme_type = st.radio(
        "Select Scheme Type",
        ["Open Ended", "Close Ended"]
    )

    # 🔽 Scheme Category (fixed options)
    scheme_category = st.selectbox(
        "Select Scheme Category",
        ["Equity Scheme", "Debt Scheme", "Hybrid Scheme"]
    )

    # 🔍 Filter dataframe by both selections
    filtered_df = df[
        (df[SCHEME_TYPE_COL].str.strip().str.lower() == scheme_type.lower()) &
        (df[SCHEME_CAT_COL].str.strip().str.lower() == scheme_category.lower())
    ]

    if filtered_df.empty:
        st.warning("No funds found for selected filters.")
        st.stop()

    # 🔽 Fund Name selection
    fund_name = st.selectbox(
        "Select Fund Name",
        sorted(filtered_df[FUND_COL].unique())
    )

    if fund_name:
        fund_data = filtered_df[filtered_df[FUND_COL] == fund_name].iloc[0]

        st.success("Fund Found ✅")
        st.metric("Rank", fund_data[RANK_COL])
        st.metric("Score", fund_data[SCORE_COL])

        with open(FILE_PATH, "rb") as file:
            st.download_button(
                label="⬇️ Download Full Excel File",
                data=file,
                file_name="MutualFund_Final_Output_16.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

except FileNotFoundError:
    st.error("Excel file not found. Please check file path and name.")
except Exception as e:
    st.error(f"Error loading file: {e}")
