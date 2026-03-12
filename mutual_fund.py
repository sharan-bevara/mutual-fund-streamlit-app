import streamlit as st
import pandas as pd

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(page_title="Mutual Fund Rank & Score", layout="wide")
st.title("📊 Mutual Fund Rank & Score Finder")

# ----------------------------------
# 1. Manual Scheme Type → Scheme Category mapping
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
        "Flexi Cap Fund", 
    ],
    "Debt Scheme": [
        "Banking and PSU Fund", "Corporate Bond Fund", "Credit Risk Fund",
        "Dynamic Bond", "Floater Fund", "Gilt Fund", "Liquid Fund",
        "Money Market Fund", "Short Duration Fund",
    ],
    "Hybrid Scheme": [
        "Arbitrage Fund", "Balanced Hybrid Fund", "Conservative Hybrid Fund",
        "Dynamic Asset Allocation or Balanced Advantage", "Equity Savings",
    ],
}

# ----------------------------------
# 2. Load Data (Cleans metadata rows automatically)
# ----------------------------------
@st.cache_data
def load_data():
    # skiprows=[1, 2] removes the "higher/lower" and "weight" rows immediately
    df = pd.read_csv("Ranked_master(in).csv", skiprows=[1, 2])
    df.columns = df.columns.str.strip()
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
    return df

df_master = load_data()

# ----------------------------------
# 3. Selection UI
# ----------------------------------
st.markdown("### Select Fund Details")
col1, col2 = st.columns(2)

with col1:
    scheme_type = st.selectbox("Scheme Type", ["Select Scheme Type"] + list(scheme_category_map.keys()))

with col2:
    if scheme_type != "Select Scheme Type":
        scheme_category = st.selectbox("Scheme Category", scheme_category_map[scheme_type])
    else:
        scheme_category = st.selectbox("Scheme Category", ["Select Scheme Type first"])

st.divider()

# ----------------------------------
# 4. Strictly Filtered Display & Download
# ----------------------------------
if scheme_type != "Select Scheme Type":
    # Step A: Filter ONLY the selected category
    # This ensures only the 'selected part' is used
    search_query = f"{scheme_type} - {scheme_category}".lower().strip()
    
    # Create a copy so we don't affect the master data
    selected_data = df_master[df_master['Scheme Category'].str.lower().str.strip() == search_query].copy()
    
    if not selected_data.empty:
        # Step B: Sort by Score (Descending)
        selected_data = selected_data.sort_values(by="Score", ascending=False)
        
        # Step C: Add Rank at the end
        selected_data['Rank'] = range(1, len(selected_data) + 1)
        
        # Step D: Move Rank to be after Score
        cols = list(selected_data.columns)
        if 'Rank' in cols and 'Score' in cols:
            cols.remove('Rank')
            score_idx = cols.index('Score')
            cols.insert(score_idx + 1, 'Rank')
            selected_data = selected_data[cols]

        # UI Feedback
        st.success(f"Displaying {len(selected_data)} funds for: {scheme_category}")

        # Step E: Display the table
        st.dataframe(selected_data, use_container_width=True, hide_index=True)

        # Step F: Download ONLY the filtered part
        csv_data = selected_data.to_csv(index=False)
        st.download_button(
            label=f"⬇️ Download {scheme_category} Report",
            data=csv_data,
            file_name=f"{scheme_category.replace(' ', '_')}_Ranked.csv",
            mime="text/csv"
        )
    else:
        st.warning("No matching funds found in the master file for this selection.")
else:
    st.info("Select a Type and Category to view the Ranked Score table.")
