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
    
    # Clean string columns for reliable filtering
    funds_df['Scheme Type'] = funds_df['Scheme Type'].str.strip()
    funds_df['Scheme Category'] = funds_df['Scheme Category'].str.strip()
    funds_df['Plan'] = funds_df['Plan'].str.strip()

    for col in params_info.keys():
        if col in funds_df.columns:
            funds_df[col] = pd.to_numeric(funds_df[col], errors='coerce').fillna(0)
    
    return funds_df, metadata_rows

df_master, df_metadata = load_data()

# ----------------------------------
# 3. Selection UI (Step 1)
# ----------------------------------
st.markdown("### Step 1: Select Fund Category & Plan")
col1, col2, col3 = st.columns(3)

with col1:
    st_type = st.selectbox("Scheme Type", ["Select"] + list(scheme_category_map.keys()), key="global_type")

with col2:
    if st_type != "Select":
        # MULTISELECT: User can pick multiple categories
        st_cat = st.multiselect("Scheme Categories", scheme_category_map[st_type], default=scheme_category_map[st_type], key="global_cat")
    else:
        st_cat = st.multiselect("Scheme Categories", ["Select Type First"], disabled=True)

with col3:
    if st_type != "Select":
        available_plans = df_master['Plan'].unique().tolist()
        st_plan = st.selectbox("Plan", ["All"] + available_plans, key="global_plan")
    else:
        st_plan = st.selectbox("Plan", ["Select Type First"], disabled=True)

st.divider()

# ----------------------------------
# 4. Processing & Displaying Original Data
# ----------------------------------
if st_type != "Select" and st_cat:
    mask = (df_master['Scheme Type'] == st_type)
    mask = mask & (df_master['Scheme Category'].isin(st_cat))
    
    if st_plan != "All":
        mask = mask & (df_master['Plan'] == st_plan)
        
    base_funds = df_master[mask].copy()

    if not base_funds.empty:
        # INDEPENDENT RANKING: Group by Category and rank by Score
        # We sort by Category first, then Score descending
        base_funds = base_funds.sort_values(by=["Scheme Category", "Score"], ascending=[True, False])
        base_funds['Rank'] = base_funds.groupby('Scheme Category')['Score'].rank(ascending=False, method='first').astype(int)
        
        # Metadata Setup
        meta_to_display = df_metadata.copy()
        meta_to_display['Rank'] = ["", ""]
        final_display = pd.concat([meta_to_display, base_funds], axis=0)
        
        # Column Order
        all_cols = list(final_display.columns)
        new_col_order = ['Rank'] + [c for c in all_cols if c not in ['Rank', 'Score']] + ['Score']
        final_display = final_display[new_col_order]
        
        st.subheader(f"📍 Original Rankings for Selected {st_type}s ({st_plan})")
        st.info("Note: Ranks are calculated independently for each category.")
        st.dataframe(final_display, use_container_width=True, hide_index=True)
        
        # Download Buttons
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            st.download_button(
                label="⬇️ Download Original Rankings (CSV)",
                data=final_display.to_csv(index=False),
                file_name=f"Original_Rankings.csv",
                mime="text/csv",
                key="btn_orig"
            )
        
        with btn_col2:
            if "custom_output" in st.session_state:
                st.download_button(
                    label="✅ Download Custom Ranks (With Your Modifications)",
                    data=st.session_state.custom_output.to_csv(index=False),
                    file_name=f"Custom_Modified_Rankings.csv",
                    mime="text/csv",
                    key="btn_custom_top"
                )
            else:
                st.info("💡 Modify weights below to enable custom download.")

        st.divider()

        # ----------------------------------
        # 5. Modify Weightages Section
        # ----------------------------------
        st.subheader("⚖️ Custom Score Calculation")
        
        if "editor_visible" not in st.session_state:
            st.session_state.editor_visible = False

        if st.button("🔧 Modify Weightages & Scope"):
            st.session_state.editor_visible = not st.session_state.editor_visible

        if st.session_state.editor_visible:
            st.info("Adjust category/plan or change weights to recalculate rankings.")
            
            edit_col1, edit_col2 = st.columns(2)
            with edit_col1:
                st.multiselect("Edit Category Scope", scheme_category_map[st_type], default=st_cat, key="edit_cat")
            with edit_col2:
                # Set default to st_plan index or "All"
                plans_list = ["All"] + df_master['Plan'].unique().tolist()
                try: def_plan_idx = plans_list.index(st_plan)
                except: def_plan_idx = 0
                st.selectbox("Edit Plan Scope", plans_list, index=def_plan_idx, key="edit_plan")

            # Weight inputs
            user_weights = {}
            w_cols = st.columns(4)
            for i, param in enumerate(params_info.keys()):
                with w_cols[i % 4]:
                    def_val = int(float(df_metadata.iloc[1][param])) if param in df_metadata.columns else 0
                    user_weights[param] = st.number_input(f"{param} Weight", 0, 100, def_val, key=f"w_{param}")
            
            user_sum = sum(user_weights.values())
            if user_sum == 100:
                st.success(f"Total Weightage: {user_sum}/100")
                if st.button("🚀 Calculate & Update Custom Download"):
                    # Filtering based on "Edit" boxes
                    c_mask = (df_master['Scheme Type'] == st_type)
                    if st.session_state.edit_cat:
                        c_mask &= (df_master['Scheme Category'].isin(st.session_state.edit_cat))
                    if st.session_state.edit_plan != "All":
                        c_mask &= (df_master['Plan'] == st.session_state.edit_plan)
                    
                    calc_df = df_master[c_mask].copy()

                    def apply_formula(row):
                        score = 0
                        for p, w in user_weights.items():
                            if params_info[p] == "higher": score += (row[p] * w)
                            else: score -= (row[p] * w)
                        return score

                    calc_df['Score'] = calc_df.apply(apply_formula, axis=1)
                    # RE-RANK INDEPENDENTLY FOR CUSTOM SCORES
                    calc_df = calc_df.sort_values(by=["Scheme Category", "Score"], ascending=[True, False])
                    calc_df['Rank'] = calc_df.groupby('Scheme Category')['Score'].rank(ascending=False, method='first').astype(int)
                    
                    # Metadata for result
                    custom_meta = df_metadata.iloc[0:1].copy()
                    weight_row = pd.Series(user_weights)
                    weight_row['Fund Name'] = "User Modified Weights"
                    custom_meta = pd.concat([custom_meta, pd.DataFrame([weight_row])], ignore_index=True)
                    custom_meta['Rank'] = ["", ""]
                    
                    st.session_state.custom_output = pd.concat([custom_meta, calc_df], axis=0)[new_col_order]
                    st.rerun() 
            else:
                st.warning(f"⚠️ Total weight must be 100 (Current: {user_sum})")
elif st_type != "Select" and not st_cat:
    st.warning("Please select at least one category.")
