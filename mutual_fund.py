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

# ----------------------------------
# 3. Selection UI (Step 1)
# ----------------------------------
st.markdown("### Step 1: Select Fund Category & Plan")
col1, col2, col3 = st.columns(3)

with col1:
    st_type = st.selectbox("Scheme Type", ["Select"] + list(scheme_category_map.keys()), key="global_type")

with col2:
    if st_type != "Select":
        # Synced with session state so changing here updates the custom section
        st_cat = st.selectbox("Scheme Category", ["All"] + scheme_category_map[st_type], key="global_cat")
    else:
        st_cat = st.selectbox("Scheme Category", ["Select Type First"], disabled=True)

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
if st_type != "Select":
    mask = (df_master['Scheme Type'].str.strip() == st_type)
    if st_cat != "All":
        mask = mask & (df_master['Scheme Category'].str.strip() == st_cat)
    if st_plan != "All":
        mask = mask & (df_master['Plan'].str.strip() == st_plan)
        
    base_funds = df_master[mask].copy()

    if not base_funds.empty:
        # Sort and Rank
        base_funds = base_funds.sort_values(by="Score", ascending=False)
        base_funds['Rank'] = range(1, len(base_funds) + 1)
        
        # Metadata Setup
        meta_to_display = df_metadata.copy()
        meta_to_display['Rank'] = ["", ""]
        final_display = pd.concat([meta_to_display, base_funds], axis=0)
        
        # Column Order
        all_cols = list(final_display.columns)
        new_col_order = ['Rank'] + [c for c in all_cols if c not in ['Rank', 'Score']] + ['Score']
        final_display = final_display[new_col_order]
        
        st.subheader(f"📍 Original Rankings for {st_cat} ({st_plan})")
        st.dataframe(final_display, use_container_width=True, hide_index=True)
        
        # --- DOWNLOAD BUTTONS AREA ---
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            st.download_button(
                label="⬇️ Download Rankings (CSV)",
                data=final_display.to_csv(index=False),
                file_name=f"{st_cat}_Original.csv",
                mime="text/csv",
                key="btn_orig"
            )
        
        with btn_col2:
            # THIS IS THE REQUESTED BUTTON: It shows up only if a custom calculation was done
            if "custom_output" in st.session_state:
                st.download_button(
                    label="✅ Download Custom Ranks (With Your Modifications)",
                    data=st.session_state.custom_output.to_csv(index=False),
                    file_name=f"{st_cat}_Custom_Modified.csv",
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
            
            # Category and Plan selects also inside Modify Weightage
            edit_col1, edit_col2 = st.columns(2)
            with edit_col1:
                # Linked to global_cat via session_state if you want them synced, 
                # or separate if you want to experiment. 
                # Here they are synced with the top ones.
                st.selectbox("Edit Category Scope", ["All"] + scheme_category_map[st_type], key="edit_cat")
            with edit_col2:
                st.selectbox("Edit Plan Scope", ["All"] + df_master['Plan'].unique().tolist(), key="edit_plan")

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
                    c_mask = (df_master['Scheme Type'].str.strip() == st_type)
                    if st.session_state.edit_cat != "All":
                        c_mask &= (df_master['Scheme Category'].str.strip() == st.session_state.edit_cat)
                    if st.session_state.edit_plan != "All":
                        c_mask &= (df_master['Plan'].str.strip() == st.session_state.edit_plan)
                    
                    calc_df = df_master[c_mask].copy()

                    def apply_formula(row):
                        score = 0
                        for p, w in user_weights.items():
                            if params_info[p] == "higher": score += (row[p] * w)
                            else: score -= (row[p] * w)
                        return score

                    calc_df['Score'] = calc_df.apply(apply_formula, axis=1)
                    calc_df = calc_df.sort_values(by="Score", ascending=False)
                    calc_df['Rank'] = range(1, len(calc_df) + 1)
                    
                    # Metadata for result
                    custom_meta = df_metadata.iloc[0:1].copy()
                    weight_row = pd.Series(user_weights)
                    weight_row['Fund Name'] = "User Modified Weights"
                    custom_meta = pd.concat([custom_meta, pd.DataFrame([weight_row])], ignore_index=True)
                    custom_meta['Rank'] = ["", ""]
                    
                    st.session_state.custom_output = pd.concat([custom_meta, calc_df], axis=0)[new_col_order]
                    st.rerun() # Refresh to show the download button at the top
            else:
                st.warning(f"⚠️ Total weight must be 100 (Current: {user_sum})")
    else:
        st.warning(f"No data matches {st_cat} / {st_plan}.")
