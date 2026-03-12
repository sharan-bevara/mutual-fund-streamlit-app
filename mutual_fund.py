import streamlit as st
import pandas as pd

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(page_title="MF Ranker", layout="wide")
st.title("📊 Mutual Fund Rank & Score Finder")

# 1. Parameter Metadata (Directions)
params_info = {
    "AUM": "higher", "TER": "lower", "PE": "lower", "PB": "lower",
    "Top 3 Holdings": "lower", "Top 5 Holdings": "lower", "Top 10 Holdings": "lower",
    "Sharpe": "higher", "Sortino": "higher", "St Dev": "lower",
    "Inception": "higher", "Age in yrs": "higher"
}

# 2. Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("Ranked_master.csv", skiprows=[1, 2])
    df.columns = df.columns.str.strip()
    for col in params_info.keys():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df_master = load_data()

# 3. Selection UI
col1, col2 = st.columns(2)
with col1:
    st_type = st.selectbox("Scheme Type", ["Select"] + sorted(df_master['Scheme Type'].unique().tolist()))
with col2:
    if st_type != "Select":
        cats = sorted(df_master[df_master['Scheme Type'] == st_type]['Scheme Category'].unique().tolist())
        st_cat = st.selectbox("Scheme Category", cats)
    else:
        st_cat = st.selectbox("Scheme Category", ["First select type"])

st.divider()

# 4. Separate Weightage Button Logic
if "show_weights" not in st.session_state:
    st.session_state.show_weights = False

# The "Weightage Button" to toggle settings
if st.button("⚖️ Set/Modify Weightages"):
    st.session_state.show_weights = not st.session_state.show_weights

user_weights = {}
total_w = 0

if st.session_state.show_weights:
    st.info("Assign numeric values to parameters. Total must equal 100.")
    w_cols = st.columns(4)
    for i, param in enumerate(params_info.keys()):
        with w_cols[i % 4]:
            # Default values provided for convenience
            user_weights[param] = st.number_input(f"{param}", 0, 100, 5 if i > 0 else 45)
            total_w += user_weights[param]
    
    st.write(f"**Current Total Weightage: {total_w}**")
    if total_w != 100:
        st.error("Total weightage must be exactly 100 to proceed.")

st.divider()

# 5. Final Action Button
if st.button("🚀 Calculate & Rank"):
    if total_w != 100:
        st.error("Please ensure total weightage equals 100 in the settings above.")
    elif st_type == "Select":
        st.warning("Please select a Scheme Type and Category.")
    else:
        # Filtering strictly for the selected part
        data = df_master[(df_master['Scheme Type'] == st_type) & (df_master['Scheme Category'] == st_cat)].copy()
        
        # Scoring Logic: (Higher * Weight) - (Lower * Weight)
        def score_row(row):
            val = 0
            for p, w in user_weights.items():
                if params_info[p] == "higher":
                    val += (row[p] * w)
                else:
                    val -= (row[p] * w)
            return val

        data['Score'] = data.apply(score_row, axis=1)
        data = data.sort_values("Score", ascending=False)
        data['Rank'] = range(1, len(data) + 1)

        # Move Rank after Score
        cols = [c for c in data.columns if c not in ['Score', 'Rank']] + ['Score', 'Rank']
        data = data[cols]

        st.success(f"Calculations complete for {st_cat}")
        st.dataframe(data, use_container_width=True, hide_index=True)
        
        st.download_button("⬇️ Download Custom CSV", data.to_csv(index=False), "custom_rank.csv")
