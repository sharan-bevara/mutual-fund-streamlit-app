import streamlit as st
import pandas as pd

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(page_title="MF Ranker & Scorer", layout="wide")
st.title("📊 Mutual Fund Rank & Score Finder")

# Parameter Logic (Higher vs Lower)
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
    # Load data skipping the metadata rows (higher/lower/weights)
    df = pd.read_csv("Ranked_master.csv", skiprows=[1, 2])
    df.columns = df.columns.str.strip()
    
    # Pre-clean numeric columns
    for col in params_info.keys():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df_master = load_data()

# ----------------------------------
# 2. Selection UI
# ----------------------------------
# Dictionary for dropdowns
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
# 3. Display & Download Selected Part (Original CSV Data)
# ----------------------------------
if st_type != "Select":
    # Filter strictly for the selection
    display_df = df_master[
        (df_master['Scheme Type'].str.strip() == st_type) & 
        (df_master['Scheme Category'].str.strip() == st_cat)
    ].copy()

    if not display_df.empty:
        st.subheader(f"📍 Original Data for {st_cat}")
        
        # Sort by the score already present in CSV and add Rank
        display_df = display_df.sort_values(by="Score", ascending=False)
        display_df['Rank'] = range(1, len(display_df) + 1)
        
        # Move Rank after Score for consistency
        cols = [c for c in display_df.columns if c not in ['Score', 'Rank']] + ['Score', 'Rank']
        display_df = display_df[cols]
        
        # SHOW TABLE
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # DOWNLOAD BUTTON FOR SELECTED PART
        st.download_button(
            label=f"⬇️ Download {st_cat} (Original CSV Data)",
            data=display_df.to_csv(index=False),
            file_name=f"{st_cat}_Original.csv",
            mime="text/csv"
        )
        
        st.divider()

        # ----------------------------------
        # 4. Weightage Section (Separate Button)
        # ----------------------------------
        st.subheader("⚖️ Custom Weightage Analysis")
        
        if "show_weights" not in st.session_state:
            st.session_state.show_weights = False

        # THE SEPARATE WEIGHTAGE BUTTON
        if st.button("🔧 Modify Weightages"):
            st.session_state.show_weights = not st.session_state.show_weights

        if st.session_state.show_weights:
            with st.form("custom_weight_form"):
                st.write("Enter numeric weights (Sum must = 100)")
                w_cols = st.columns(4)
                user_weights = {}
                
                for i, param in enumerate(params_info.keys()):
                    with w_cols[i % 4]:
                        user_weights[param] = st.number_input(f"{param}", 0, 100, 0)
                
                # RECALCULATE BUTTON
                submitted = st.form_submit_button("Generate Custom Rank")
                
                if submitted:
                    total_w = sum(user_weights.values())
                    if total_w != 100:
                        st.error(f"Total weightage is {total_w}. It must be exactly 100.")
                    else:
                        # Scoring Logic
                        def calc_score(row):
                            s = 0
                            for p, w in user_weights.items():
                                if params_info[p] == "higher":
                                    s += (row[p] * w)
                                else:
                                    s -= (row[p] * w)
                            return s

                        # Create custom ranking
                        custom_df = display_df.copy()
                        custom_df['Score'] = custom_df.apply(calc_score, axis=1)
                        custom_df = custom_df.sort_values(by="Score", ascending=False)
                        custom_df['Rank'] = range(1, len(custom_df) + 1)
                        
                        # Fix Column order
                        cols = [c for c in custom_df.columns if c not in ['Score', 'Rank']] + ['Score', 'Rank']
                        custom_df = custom_df[cols]

                        st.success("Custom Rank Generated Successfully!")
                        st.dataframe(custom_df, use_container_width=True, hide_index=True)
                        
                        # DOWNLOAD BUTTON FOR CUSTOMIZED SHEET
                        st.download_button(
                            label="⬇️ Download Customized Rank Sheet",
                            data=custom_df.to_csv(index=False),
                            file_name=f"{st_cat}_Custom_Ranked.csv",
                            mime="text/csv"
                        )
    else:
        st.warning("No data found for this selection.")
