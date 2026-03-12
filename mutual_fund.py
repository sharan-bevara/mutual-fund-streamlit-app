import streamlit as st
import pandas as pd

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(page_title="Mutual Fund Rank & Score", layout="wide")
st.title("📊 Mutual Fund Rank & Score Finder")

# ----------------------------------
# 1. REFERENCE DICTIONARY (Mapping)
# ----------------------------------
# Add or edit this list to match your future data updates
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
        "Index Fund",
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
# 2. Load Data
# ----------------------------------
@st.cache_data
def load_data():
    # Reading 'Ranked_master.csv'
    # skiprows=[1, 2] ignores the logic/weight rows from your source file
    df = pd.read_csv("Ranked_master.csv", skiprows=[1, 2])
    
    # Clean column names (removes hidden spaces)
    df.columns = df.columns.str.strip()
    
    # Convert Score to a number for correct sorting
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
    
    return df

df_master = load_data()

# ----------------------------------
# 3. Selection UI (Dropdowns)
# ----------------------------------
st.markdown("### Select Fund Details")
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
# 4. Processing & Display
# ----------------------------------
if scheme_type != "Select Scheme Type":
    # Filter the master data based on the two separate columns
    selected_data = df_master[
        (df_master['Scheme Type'].str.strip() == scheme_type) & 
        (df_master['Scheme Category'].str.strip() == scheme_category)
    ].copy()
    
    if not selected_data.empty:
        # Sort by Score (Descending order: highest score at top)
        selected_data = selected_data.sort_values(by="Score", ascending=False)
        
        # Calculate Rank (1, 2, 3...)
        selected_data['Rank'] = range(1, len(selected_data) + 1)
        
        # Move Rank column to appear after the Score column
        cols = list(selected_data.columns)
        if 'Rank' in cols and 'Score' in cols:
            cols.remove('Rank')
            score_idx = cols.index('Score')
            cols.insert(score_idx + 1, 'Rank')
            selected_data = selected_data[cols]

        # Success Message
        st.success(f"Found {len(selected_data)} fund(s) for {scheme_category}")

        # Display strictly the selected part
        st.dataframe(selected_data, use_container_width=True, hide_index=True)

        # Download button for the filtered results
        csv_file = selected_data.to_csv(index=False)
        st.download_button(
            label=f"⬇️ Download {scheme_category} Ranked List",
            data=csv_file,
            file_name=f"{scheme_category.replace(' ', '_')}_Ranked.csv",
            mime="text/csv"
        )
    else:
        st.warning(f"No funds found in the CSV for '{scheme_type} - {scheme_category}'")
else:
    st.info("Choose a Scheme Type and Category above to view ranked results.")
