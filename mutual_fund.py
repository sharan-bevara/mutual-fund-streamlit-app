import streamlit as st
import pandas as pd

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(page_title="MF Custom Scorer", layout="wide")
st.title("📊 Mutual Fund Rank & Score Finder")

# Parameter Logic Map
params_info = {
    "AUM": "higher", "TER": "lower", "PE": "lower", "PB": "lower",
    "Top 3 Holdings": "lower", "Top 5 Holdings": "lower", "Top 10 Holdings": "lower",
    "Sharpe": "higher", "Sortino": "higher", "St Dev": "lower",
    "Inception": "higher", "Age in yrs": "higher"
}

# ----------------------------------
# 1. Load Data
# ----------------------------------
@st.cache_data
def load_data():
    # Load raw to extract metadata rows
    raw_df = pd.read_csv("Ranked_master.csv")
    raw_df.columns = raw_df.columns.str.strip()
    
    # Row 0: higher/lower labels | Row 1: default weight values
    metadata_rows = raw_df.iloc[0:2].copy()
    
    # Actual fund data starts from index 2
    funds_df = raw_df.iloc[2:].copy()
    
    # Ensure numeric columns are ready for math
    for col in params_info.keys():
        if col in funds_df.columns:
            funds_df[col] = pd.to_numeric(funds_df[col], errors='coerce').fillna(0)
    
    return funds_df, metadata_rows

df_master, df_metadata = load_data()
# ... [Page Config and load_data function] ...

df_master, df_metadata = load_data()

# ----------------------------------
# 2. Selection UI 
# ----------------------------------

# MOVE THIS HERE (Above the selectbox)
scheme_category_map = {
    "Equity Scheme": ["Contra Fund", "Dividend Yield Fund", "ELSS", "Focused Fund", "Large Cap Fund", "Large & Mid Cap Fund", "Mid Cap Fund", "Multi Cap Fund", "Sectoral / Thematic", "Small Cap Fund", "Value Fund", "Flexi Cap Fund", "Index Fund"],
    "Debt Scheme": ["Banking and PSU Fund", "Corporate Bond Fund", "Credit Risk Fund", "Dynamic Bond", "Floater Fund", "Gilt Fund", "Liquid Fund", "Money Market Fund", "Short Duration Fund"],
    "Hybrid Scheme": ["Arbitrage Fund", "Balanced Hybrid Fund", "Conservative Hybrid Fund", "Dynamic Asset Allocation or Balanced Advantage", "Equity Savings"],
}

st.markdown("### Step 1: Select Fund Category & Plan")
col1, col2, col3 = st.columns(3)

with col1:
    # Now this will find scheme_category_map successfully
    st_type = st.selectbox("Scheme Type", ["Select"] + list(scheme_category_map.keys()))

with col2:
    if st_type != "Select":
        st_cat = st.selectbox("Scheme Category", ["All"] + scheme_category_map[st_type])
    else:
        st_cat = st.selectbox("Scheme Category", ["Select Type First"])

with col3:
    if st_type != "Select":
        available_plans = df_master['Plan'].unique().tolist()
        st_plan = st.selectbox("Plan", ["All"] + available_plans)
    else:
        st_plan = st.selectbox("Plan", ["Select Type First"])

# ----------------------------------
# 3. Display Original Part (UPDATED Filtering Logic)
# ----------------------------------
if st_type != "Select":
    # 1. Start with the Scheme Type filter
    mask = (df_master['Scheme Type'].str.strip() == st_type)
    
    # 2. Add Category filter only if a specific one is selected
    if st_cat != "All":
        mask = mask & (df_master['Scheme Category'].str.strip() == st_cat)
    
    # 3. Add Plan filter only if a specific one is selected
    if st_plan != "All":
        mask = mask & (df_master['Plan'].str.strip() == st_plan)
        
    base_funds = df_master[mask].copy()

    if not base_funds.empty:
        # Dynamic title based on selection
        display_name = st_cat if st_cat != "All" else f"All {st_type}s"
        st.subheader(f"📍 Original CSV Data for {display_name} ({st_plan})")
        
        # Sort and Rank the funds
        base_funds = base_funds.sort_values(by="Score", ascending=False)
        base_funds['Rank'] = range(1, len(base_funds) + 1)
        
        # Combine Metadata rows with the filtered Funds
        meta_to_display = df_metadata.copy()
        meta_to_display['Rank'] = ["", ""] 
        
        final_display = pd.concat([meta_to_display, base_funds], axis=0)
        
        # REORDER: Put Rank as the first column, Score as the last
        all_cols = list(final_display.columns)
        other_cols = [c for c in all_cols if c not in ['Rank', 'Score']]
        new_col_order = ['Rank'] + other_cols + ['Score']
        final_display = final_display[new_col_order]
        
        st.dataframe(final_display, use_container_width=True, hide_index=True)
        
        st.download_button(
            label="⬇️ Download Selected Data (CSV)",
            data=final_display.to_csv(index=False),
            file_name=f"{st_cat}_{st_plan}_data.csv",
            mime="text/csv",
            key="btn_orig"
        )
        st.divider()

        # ----------------------------------
        # 4. Custom Weightage Section
        # ----------------------------------
        st.subheader("⚖️ Custom Score Calculation")
        
        if "editor_visible" not in st.session_state:
            st.session_state.editor_visible = False

        if st.button("🔧 Modify Weightages"):
            st.session_state.editor_visible = not st.session_state.editor_visible

        if st.session_state.editor_visible:
            st.info("Formula: Score = Σ(Weight × Higher Params) - Σ(Weight × Lower Params)")
            
            user_weights = {}
            w_cols = st.columns(4)
            for i, param in enumerate(params_info.keys()):
                with w_cols[i % 4]:
                    # Default to values found in row index 1 of the CSV
                    default_val = int(float(df_metadata.iloc[1][param])) if param in df_metadata.columns else 0
                    user_weights[param] = st.number_input(f"{param} Weight", 0, 100, default_val, key=f"inp_{param}")
            
            user_sum = sum(user_weights.values())
            if user_sum == 100:
                st.success(f"✅ Total Weightage: {user_sum}/100")
            elif user_sum > 100:
                st.error(f"❌ Total Weightage: {user_sum}/100 (Exceeds 100!)")
            else:
                st.info(f"🔢 Total Weightage: {user_sum}/100 (Remaining: {100 - user_sum})")

            if st.button("🚀 Calculate New Score & Rank"):
                if user_sum != 100:
                    st.error("Error: Total weightage must be exactly 100.")
                else:
                    def apply_formula(row):
                        score = 0
                        for p, w in user_weights.items():
                            if params_info[p] == "higher":
                                score += (row[p] * w)
                            else:
                                score -= (row[p] * w)
                        return score

                    custom_funds = base_funds.copy()
                    custom_funds['Score'] = custom_funds.apply(apply_formula, axis=1)
                    custom_funds = custom_funds.sort_values(by="Score", ascending=False)
                    custom_funds['Rank'] = range(1, len(custom_funds) + 1)
                    
                    # Prepare metadata rows for custom output
                    custom_meta = df_metadata.iloc[0:1].copy() # Keep higher/lower
                    new_weights = pd.Series(user_weights)
                    new_weights['Fund Name'] = "Custom Weights"
                    custom_meta = pd.concat([custom_meta, pd.DataFrame([new_weights])], ignore_index=True)
                    custom_meta['Rank'] = ["", ""]
                    
                    custom_output = pd.concat([custom_meta, custom_funds], axis=0)
                    custom_output = custom_output[new_col_order] # Apply same Rank-first order
                    
                    st.session_state.custom_output = custom_output

            if "custom_output" in st.session_state:
                st.divider()
                st.subheader("📊 Results: Custom Weighted Score & Rank")
                st.dataframe(st.session_state.custom_output, use_container_width=True, hide_index=True)
                
                st.download_button(
                    label="⬇️ Download Customized Rank Sheet (CSV)",
                    data=st.session_state.custom_output.to_csv(index=False),
                    file_name=f"{st_cat}_Custom_Ranked.csv",
                    mime="text/csv",
                    key="btn_custom"
                )
    else:
        st.warning("No data found for this category.")
