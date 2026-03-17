import streamlit as st
import pandas as pd

# ----------------------------------
# 1. Configuration & Metadata Maps
# ----------------------------------
st.set_page_config(page_title="MF Custom Scorer", layout="wide")
st.title("📊 Mutual Fund Rank & Score Finder")

# Parameter Logic (Used for calculation, not displayed in output)
params_info = {
    "AUM": "higher", "TER": "lower", "PE": "lower", "PB": "lower",
    "Top 3 Holdings": "lower", "Top 5 Holdings": "lower", "Top 10 Holdings": "lower",
    "Sharpe": "higher", "Sortino": "higher", "St Dev": "lower",
    "Inception": "higher", "Age in yrs": "higher"
}

scheme_category_map = {
    "Equity Scheme": ["Contra Fund", "Dividend Yield Fund", "ELSS", "Focused Fund", "Large Cap Fund", "Large & Mid Cap Fund", "Mid Cap Fund", "Multi Cap Fund", "Sectoral / Thematic", "Small Cap Fund", "Value Fund", "Flexi Cap Fund", "Index Fund"],
    "Debt Scheme": ["Banking and PSU Fund", "Corporate Bond Fund", "Credit Risk Fund", "Dynamic Bond", "Floater Fund", "Gilt Fund", "Liquid Fund", "Money Market Fund", "Short Duration Fund"],
    "Hybrid Scheme": ["Arbitrage Fund", "Balanced Hybrid Fund", "Conservative Hybrid Fund", "Dynamic Asset Allocation or Balanced Advantage", "Equity Savings"],
}

# ----------------------------------
# 2. Load Data
# ----------------------------------
@st.cache_data
def load_data():
    raw_df = pd.read_csv("Ranked_master.csv")
    raw_df.columns = raw_df.columns.str.strip()
    
    # Store weights for reference but skip metadata rows for the main dataset
    # Row 0: higher/lower | Row 1: weights
    csv_weights = raw_df.iloc[1].copy()
    funds_df = raw_df.iloc[2:].copy()
    
    # Clean string columns
    for col in ['Scheme Type', 'Scheme Category', 'Plan']:
        if col in funds_df.columns:
            funds_df[col] = funds_df[col].astype(str).str.strip()

    # Convert numeric columns for ranking
    cols_to_fix = list(params_info.keys()) + ['Score']
    for col in cols_to_fix:
        if col in funds_df.columns:
            funds_df[col] = pd.to_numeric(funds_df[col], errors='coerce').fillna(0)
    
    return funds_df, csv_weights

df_master, df_csv_weights = load_data()

# ----------------------------------
# 3. Selection UI (Step 1)
# ----------------------------------
st.markdown("### Step 1: Select Fund Category & Plan")
col1, col2, col3 = st.columns(3)

with col1:
    st_type = st.selectbox("Scheme Type", ["Select"] + list(scheme_category_map.keys()), key="global_type")

with col2:
    if st_type != "Select":
        all_cats = scheme_category_map[st_type]
        st_cat = st.multiselect("Scheme Categories", all_cats, default=all_cats, key="global_cat")
    else:
        st_cat = st.multiselect("Scheme Categories", ["Select Type First"], disabled=True)

with col3:
    if st_type != "Select":
        available_plans = sorted(df_master['Plan'].unique().tolist())
        st_plan = st.selectbox("Plan", ["All"] + available_plans, key="global_plan")
    else:
        st_plan = st.selectbox("Plan", ["Select Type First"], disabled=True)

st.divider()

# ----------------------------------
# 4. Processing & Displaying Original Data
# ----------------------------------
if st_type != "Select" and st_cat:
    mask = (df_master['Scheme Type'] == st_type) & (df_master['Scheme Category'].isin(st_cat))
    if st_plan != "All":
        mask = mask & (df_master['Plan'] == st_plan)
        
    base_funds = df_master[mask].copy()

    if not base_
