import streamlit as st
import pandas as pd

# ----------------------------------
# 1. Configuration & Metadata Maps
# ----------------------------------
st.set_page_config(page_title="MF Custom Scorer", layout="wide")
st.title("📊 Mutual Fund Rank & Score Finder")

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
    
    metadata_rows = raw_df.iloc[0:2].copy()
    funds_df = raw_df.iloc[2:].copy()
    
    for col in params_info.keys():
        if col in funds_df.columns:
            funds_df[col] = pd.to_numeric(funds_df[col], errors='coerce').fillna(0)
    
    return funds_df, metadata_rows

df_master, df_metadata = load_data()

# Initialize session state for syncing filters
if 'st_type' not in st.session_state: st.session_state.st_type = "Select"
if 'st_cat' not in st.session_state: st.session_state.st_cat = "All"
if 'st_plan' not in st.session_state: st.session_state.st_plan = "All"

# ----------------------------------
# 3. Step 1: Selection UI (Global Filters)
# ----------------------------------
st.markdown("### Step 1: Global Fund Selection")
c1, c2, c3 = st.columns(3)

with c1:
    st_type = st.selectbox("Scheme Type", ["Select"] + list(scheme_category_map.keys()), key="st_type")

with c2:
    if st_type != "Select":
        cats = ["All"] + scheme_category_map[st_type]
        st_cat = st.selectbox("Scheme Category", cats, key="st_cat")
    else:
        st_cat = st.selectbox("Scheme Category", ["Select Type First"], disabled=True)

with c3:
    if st_type != "Select":
        plans = ["All"] + df_master['Plan'].unique().tolist()
        st_plan = st.selectbox("Plan", plans, key="st_plan")
    else:
        st_plan = st.selectbox("Plan", ["Select Type First"], disabled=True)

st.divider()

# ----------------------------------
# 4. Processing & Displaying Original Data
# ----------------------------------
if st_type != "Select":
    # Base Filter Logic
    mask = (df_master['Scheme Type'].str.strip() == st_type)
    if st_cat != "All":
        mask = mask & (df_master['Scheme Category'].str.strip() == st_cat)
    if st_plan != "All":
        mask = mask & (df_master['Plan'].str.strip() == st_plan)
        
    base_funds = df_master[mask].copy()

    if not base_funds.empty:
        st.subheader(f"📍 Original Rankings: {st_cat} ({st_plan})")
        
        # Ranking Logic
        base_funds = base_funds.sort_values(by="Score", ascending=False)
        base_funds['Rank'] = range(1, len(base_funds) + 1)
        
        # Prep Metadata Display
        meta_display = df_metadata.copy()
        meta_display['Rank'] = ["", ""]
        final_display = pd.concat([meta_display, base_funds], axis=0)
        
        # Columns reorder
        all_cols = list(final_display.columns)
        new_order = ['Rank'] + [c for c in all_cols if c not in ['Rank', 'Score']] + ['Score']
        final_display = final_display[new_order]
        
        st.dataframe(final_display, use_container_width=True, hide_index=True)
        st.divider()

        # ----------------------------------
        # 5. Custom Weightage Section (Includes filters)
        # ----------------------------------
        st.subheader("⚖️ Custom Score Calculation")
        
        if "editor_visible" not in st.session_state:
            st.session_state.editor_visible = False

        if st.button("🔧 Modify Weights & Filter Scope"):
            st.session_state.editor_visible = not st.session_state.editor_visible

        if st.session_state.editor_visible:
            st.info("You can adjust weights and change the Category/Plan filters here as well.")
            
            # Sub-filters within the Custom Section (Linked to same session state)
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                # This box is synced with the top one because they share the 'st_cat' key
                st.selectbox("Change Category Scope", ["All"] + scheme_category_map[st_type], key="custom_cat")
            with f_col2:
                # Sync'd with 'st_plan'
                st.selectbox("Change Plan Scope", ["All"] + df_master['Plan'].unique().tolist(), key="custom_plan")

            # Weightage Inputs
            user_weights = {}
            w_cols = st.columns(4)
            for i, param in enumerate(params_info.keys()):
                with w_cols[i % 4]:
                    # Get default from row 1 of CSV
                    def_val = int(float(df_metadata.iloc[1][param])) if param in df_metadata.columns else 0
                    user_weights[param] = st.number_input(f"{param} Weight", 0, 100, def_val, key=f"w_{param}")
            
            user_sum = sum(user_weights.values())
            if user_sum == 100:
                st.success(f"✅ Total: {user_sum}/100")
            else:
                st.warning(f"⚠️ Total Weightage must be 100. Current: {user_sum}")

            if st.button("🚀 Calculate New Score & Rank"):
                if user_sum != 100:
                    st.error("Error: Total weightage must be exactly 100.")
                else:
                    # Apply specific filters from the custom section session state
                    custom_mask = (df_master['Scheme Type'].str.strip() == st_type)
                    if st.session_state.custom_cat != "All":
                        custom_mask &= (df_master['Scheme Category'].str.strip() == st.session_state.custom_cat)
                    if st.session_state.custom_plan != "All":
                        custom_mask &= (df_master['Plan'].str.strip() == st.session_state.custom_plan)
                    
                    calc_df = df_master[custom_mask].copy()

                    def apply_formula(row):
                        score = 0
                        for p, w in user_weights.items():
                            if params_info[p] == "higher":
                                score += (row[p] * w)
                            else:
                                score -= (row[p] * w)
                        return score

                    calc_df['Score'] = calc_df.apply(apply_formula, axis=1)
                    calc_df = calc_df.sort_values(by="Score", ascending=False)
                    calc_df['Rank'] = range(1, len(calc_df) + 1)
                    
                    # Metadata for Custom output
                    custom_meta = df_metadata.iloc[0:1].copy() # Logic labels
                    custom_weights_row = pd.Series(user_weights)
                    custom_weights_row['Fund Name'] = "Custom Weights Used"
                    custom_meta = pd.concat([custom_meta, pd.DataFrame([custom_weights_row])], ignore_index=True)
                    custom_meta['Rank'] = ["", ""]
                    
                    st.session_state.custom_output = pd.concat([custom_meta, calc_df], axis=0)[new_order]

            # Show results if they exist
            if "custom_output" in st.session_state:
                st.write("---")
                st.subheader("📊 Custom Calculation Results")
                st.dataframe(st.session_state.custom_output, use_container_width=True, hide_index=True)
                st.download_button(
                    label="⬇️ Download Custom Rankings",
                    data=st.session_state.custom_output.to_csv(index=False),
                    file_name="Custom_MF_Rankings.csv",
                    mime="text/csv"
                )
    else:
        st.warning(f"No data matches {st_cat} / {st_plan}.")
