import streamlit as st
import pandas as pd

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(page_title="MF Custom Scorer", layout="wide")
st.title("📊 Mutual Fund Rank & Score Finder")

# Parameter Logic Map
# Higher: Value is added to score | Lower: Value is subtracted from score
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
    # Load data skipping the metadata rows (row 1 and 2 in CSV)
    df = pd.read_csv("Ranked_master.csv", skiprows=[1, 2])
    df.columns = df.columns.str.strip()
    
    # Ensure numeric columns are ready for the math formula
    for col in params_info.keys():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df_master = load_data()

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
# 3. Display Original Part (From CSV)
# ----------------------------------
if st_type != "Select":
    # Filter for the selected part
    base_df = df_master[
        (df_master['Scheme Type'].str.strip() == st_type) & 
        (df_master['Scheme Category'].str.strip() == st_cat)
    ].copy()

    if not base_df.empty:
        st.subheader(f"📍 Original CSV Data for {st_cat}")
        
        # Initial ranking based on existing CSV scores
        original_display = base_df.sort_values(by="Score", ascending=False).copy()
        original_display['Rank'] = range(1, len(original_display) + 1)
        
        # Position Score and Rank at the end
        cols = [c for c in original_display.columns if c not in ['Score', 'Rank']] + ['Score', 'Rank']
        original_display = original_display[cols]
        
        st.dataframe(original_display, use_container_width=True, hide_index=True)
        
        # DOWNLOAD BUTTON 1: Selected Original Part
        st.download_button(
            label="⬇️ Download Selected Original Data (CSV)",
            data=original_display.to_csv(index=False),
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
            
            # Use columns to collect weights
            user_weights = {}
            w_cols = st.columns(4)
            for i, param in enumerate(params_info.keys()):
                with w_cols[i % 4]:
                    user_weights[param] = st.number_input(f"{param} Weight", 0, 100, 0, key=f"inp_{param}")
            
            # DISPLAY LIVE SUM
            user_sum = sum(user_weights.values())
            if user_sum == 100:
                st.success(f"✅ Total Weightage: {user_sum}/100")
            elif user_sum > 100:
                st.error(f"❌ Total Weightage: {user_sum}/100 (Reduce weights)")
            else:
                st.info(f"🔢 Total Weightage: {user_sum}/100 (Add {100 - user_sum} more)")

            # SEPARATE CALCULATE BUTTON
            if st.button("🚀 Calculate New Score & Rank"):
                if user_sum != 100:
                    st.error("Error: Total weightage must be exactly 100.")
                else:
                    # IMPLEMENTING THE FORMULA
                    def apply_formula(row):
                        score = 0
                        for p, w in user_weights.items():
                            if params_info[p] == "higher":
                                score += (row[p] * w) # Add for higher
                            else:
                                score -= (row[p] * w) # Subtract for lower
                        return score

                    # Build the customized sheet
                    custom_df = base_df.copy()
                    custom_df['Score'] = custom_df.apply(apply_formula, axis=1)
                    custom_df = custom_df.sort_values(by="Score", ascending=False)
                    custom_df['Rank'] = range(1, len(custom_df) + 1)
                    
                    # Finalize column placement
                    f_cols = [c for c in custom_df.columns if c not in ['Score', 'Rank']] + ['Score', 'Rank']
                    st.session_state.custom_output = custom_df[f_cols]

            # ----------------------------------
            # 5. Display Custom Results & Download
            # ----------------------------------
            if "custom_output" in st.session_state:
                st.divider()
                st.subheader("📊 Results: Custom Weighted Score & Rank")
                st.dataframe(st.session_state.custom_output, use_container_width=True, hide_index=True)
                
                # DOWNLOAD BUTTON 2: Custom Sheet
                st.download_button(
                    label="⬇️ Download Customized Rank Sheet (CSV)",
                    data=st.session_state.custom_output.to_csv(index=False),
                    file_name=f"{st_cat}_Custom_Ranked.csv",
                    mime="text/csv",
                    key="btn_custom"
                )
    else:
        st.warning("No data found for this category.")
