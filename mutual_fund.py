import streamlit as st
import pandas as pd

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(page_title="MF Custom Scorer", layout="wide")
st.title("📊 Mutual Fund Rank & Score Finder")

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
    
    # Row 0: higher/lower labels
    # Row 1: default weight values
    metadata_rows = raw_df.iloc[0:2].copy()
    
    # Actual fund data starts from index 2
    funds_df = raw_df.iloc[2:].copy()
    
    # Ensure numeric columns are ready for math
    for col in params_info.keys():
        if col in funds_df.columns:
            funds_df[col] = pd.to_numeric(funds_df[col], errors='coerce').fillna(0)
    
    return funds_df, metadata_rows

df_master, df_metadata = load_data()

# ----------------------------------
# 2. Selection UI
# ----------------------------------
scheme_category_map = {
    "Equity Scheme": ["Contra Fund", "Dividend Yield Fund", "ELSS", "Focused Fund", "Large Cap Fund", "Large & Mid Cap Fund", "Mid Cap Fund", "Multi Cap Fund", "Sectoral / Thematic", "Small Cap Fund", "Value Fund", "Flexi Cap Fund", "Index Fund"],
    "Debt Scheme": ["Banking and PSU Fund", "Corporate Bond Fund", "Credit Risk Fund", "Dynamic Bond", "Floater Fund", "Gilt Fund", "Liquid Fund", "Money Market Fund", "Short Duration Fund"],
    "Hybrid Scheme": ["Arbitrage Fund", "Balanced Hybrid Fund", "Conservative Hybrid Fund", "Dynamic Asset Allocation or Balanced Advantage", "Equity Savings"],
}

st.markdown("### Step 1: Select Fund Category")
col1, col2 = st.columns(2)
with col1:
    st_type = st.selectbox("Scheme Type", ["Select"] + list(scheme_category_map.keys()))
with col2:
    if st_type != "Select":
        st_cat = st.selectbox("Scheme Category", scheme_category_map[st_type])
    else:
        st_cat = st.selectbox("Scheme Category", ["Select Type First"])

st.divider()

# ----------------------------------
# 3. Display Original Part (With Metadata)
# ----------------------------------
if st_type != "Select":
    # Filter funds
    base_funds = df_master[
        (df_master['Scheme Type'].str.strip() == st_type) & 
        (df_master['Scheme Category'].str.strip() == st_cat)
    ].copy()

    if not base_funds.empty:
        st.subheader(f"📍 Original CSV Data for {st_cat}")
        
        # Sort and Rank the funds
        base_funds = base_funds.sort_values(by="Score", ascending=False)
        base_funds['Rank'] = range(1, len(base_funds) + 1)
        
        # Combine Metadata rows with the filtered Funds
        # We ensure Rank column exists in metadata rows as empty for alignment
        meta_to_display = df_metadata.copy()
        meta_to_display['Rank'] = ""
        
        final_display = pd.concat([meta_to_display, base_funds], axis=0)
        
        # Position Score and Rank at the end
        cols = [c for c in final_display.columns if c not in ['Score', 'Rank']] + ['Score', 'Rank']
        final_display = final_display[cols]
        
        # Display the table including higher/lower and weight rows
        st.dataframe(final_display, use_container_width=True, hide_index=True)
        
        st.download_button(
            label="⬇️ Download Selected Original Data (CSV)",
            data=final_display.to_csv(index=False),
            file_name=f"{st_cat}_original_data.csv",
            mime="text/csv",
            key="btn_orig"
        )
        
        st.divider()

        # ----------------------------------
        # 4. Custom Weightage & Formula Calculation
        # ----------------------------------
        st.subheader("⚖️ Custom Score Calculation")
        
        if "editor_visible" not in st.session_state:
            st.session_state.editor_visible = False

        if st.button("🔧 Modify Weightages"):
            st.session_state.editor_visible = not st.session_state.editor_visible

        if st.session_state.editor_visible:
            st.info("The formula used: Score = Σ(Weight × Higher Params) - Σ(Weight × Lower Params)")
            
            user_weights = {}
            w_cols = st.columns(4)
            for i, param in enumerate(params_info.keys()):
                with w_cols[i % 4]:
                    # Default to the weight in the CSV (from row index 1)
                    default_w = int(float(df_metadata.iloc[1][param])) if param in df_metadata.columns else 0
                    user_weights[param] = st.number_input(f"{param} Weight", 0, 100, default_w, key=f"inp_{param}")
            
            user_sum = sum(user_weights.values())
            if user_sum == 100:
                st.success(f"✅ Total Weightage: {user_sum}/100")
            elif user_sum > 100:
                st.error(f"❌ Total Weightage: {user_sum}/100 (Reduce weights)")
            else:
                st.info(f"🔢 Total Weightage: {user_sum}/100 (Add {100 - user_sum} more)")

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

                    # Build the customized sheet
                    custom_funds = base_funds.copy()
                    custom_funds['Score'] = custom_funds.apply(apply_formula, axis=1)
                    custom_funds = custom_funds.sort_values(by="Score", ascending=False)
                    custom_funds['Rank'] = range(1, len(custom_funds) + 1)
                    
                    # Add current custom weights as metadata row for the download/display
                    custom_meta = df_metadata.iloc[0:1].copy() # keep higher/lower
                    new_weights_row = pd.Series(user_weights)
                    new_weights_row['Fund Name'] = "Custom Weights"
                    custom_meta = pd.concat([custom_meta, pd.DataFrame([new_weights_row])], ignore_index=True)
                    custom_meta['Rank'] = ""
                    
                    custom_output = pd.concat([custom_meta, custom_funds], axis=0)
                    custom_output = custom_output[cols] # Use same column order
                    
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
