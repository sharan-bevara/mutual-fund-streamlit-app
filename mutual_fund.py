import streamlit as st
import pandas as pd

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(page_title="MF Ranker", layout="wide")
st.title("📊 Mutual Fund Rank & Score Finder")

# 1. Parameter Metadata (Directions for scoring logic)
params_info = {
    "AUM": "higher", "TER": "lower", "PE": "lower", "PB": "lower",
    "Top 3 Holdings": "lower", "Top 5 Holdings": "lower", "Top 10 Holdings": "lower",
    "Sharpe": "higher", "Sortino": "higher", "St Dev": "lower",
    "Inception": "higher", "Age in yrs": "higher"
}

# ----------------------------------
# 2. Load Data
# ----------------------------------
@st.cache_data
def load_data():
    # Load data skipping the metadata rows for the main dataframe
    df = pd.read_csv("Ranked_master.csv", skiprows=[1, 2])
    df.columns = df.columns.str.strip()
    
    # Pre-clean numeric columns
    for col in params_info.keys():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Load row 2 to get default weights from the CSV for the reference
    weights_row = pd.read_csv("Ranked_master.csv", nrows=1, skiprows=1)
    return df

df_master = load_data()

# ----------------------------------
# 3. Selection UI
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
# 4. Initial Display (Whatever is in the CSV)
# ----------------------------------
if st_type != "Select":
    # Filter the data strictly for the selection
    display_df = df_master[
        (df_master['Scheme Type'].str.strip() == st_type) & 
        (df_master['Scheme Category'].str.strip() == st_cat)
    ].copy()

    if not display_df.empty:
        st.subheader(f"Current Data for {st_cat} (From CSV)")
        
        # Sort by the score already present in CSV and add Rank
        display_df = display_df.sort_values(by="Score", ascending=False)
        display_df['Rank'] = range(1, len(display_df) + 1)
        
        # Display Table
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.divider()

        # ----------------------------------
        # 5. Weightage Button Section (Appears AFTER display)
        # ----------------------------------
        st.subheader("⚖️ Custom Scoring & Re-Ranking")
        
        if "show_editor" not in st.session_state:
            st.session_state.show_editor = False

        if st.button("Modify Weightages & Recalculate"):
            st.session_state.show_editor = not st.session_state.show_editor

        if st.session_state.show_editor:
            with st.form("weightage_form"):
                st.write("Enter weights for each parameter (Sum must = 100)")
                w_cols = st.columns(4)
                user_weights = {}
                
                # Create input fields for each parameter
                for i, param in enumerate(params_info.keys()):
                    with w_cols[i % 4]:
                        user_weights[param] = st.number_input(f"{param}", 0, 100, 0)
                
                submitted = st.form_submit_button("Generate New Score & Rank")
                
                if submitted:
                    total_w = sum(user_weights.values())
                    if total_w != 100:
                        st.error(f"Total weightage is {total_w}. It must be exactly 100.")
                    else:
                        # Calculation Logic
                        def calc_new_score(row):
                            score = 0
                            for p, w in user_weights.items():
                                if params_info[p] == "higher":
                                    score += (row[p] * w)
                                else:
                                    score -= (row[p] * w)
                            return score

                        # Create new version of data
                        custom_df = display_df.copy()
                        custom_df['Score'] = custom_df.apply(calc_new_score, axis=1)
                        custom_df = custom_df.sort_values(by="Score", ascending=False)
                        custom_df['Rank'] = range(1, len(custom_df) + 1)
                        
                        # Move columns
                        cols = [c for c in custom_df.columns if c not in ['Score', 'Rank']] + ['Score', 'Rank']
                        custom_df = custom_df[cols]

                        st.success("New Ranking Generated!")
                        st.dataframe(custom_df, use_container_width=True, hide_index=True)
                        st.download_button("Download Custom Ranked CSV", custom_df.to_csv(index=False), "custom_ranks.csv")
    else:
        st.warning("No matching funds found in CSV.")
