import streamlit as st
import pandas as pd

st.set_page_config(page_title="MF Scorer", layout="wide")
st.title("📊 Mutual Fund Custom Scorer")

# 1. Configuration for Logic
params_info = {
    "AUM": "higher", "TER": "lower", "PE": "lower", "PB": "lower",
    "Top 3 Holdings": "lower", "Top 5 Holdings": "lower", "Top 10 Holdings": "lower",
    "Sharpe": "higher", "Sortino": "higher", "St Dev": "lower",
    "Inception": "higher", "Age in yrs": "higher"
}

@st.cache_data
def load_data():
    # Load and clean data (skipping metadata rows)
    df = pd.read_csv("Ranked_master.csv", skiprows=[1, 2])
    df.columns = df.columns.str.strip()
    # Convert numeric columns for calculation
    for col in params_info.keys():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df_master = load_data()

# 2. UI: Selection Boxes (Always Visible)
col1, col2 = st.columns(2)
with col1:
    st_type = st.selectbox("Scheme Type", ["Select"] + sorted(df_master['Scheme Type'].unique().tolist()))
with col2:
    if st_type != "Select":
        cats = sorted(df_master[df_master['Scheme Type'] == st_type]['Scheme Category'].unique().tolist())
        st_cat = st.selectbox("Scheme Category", cats)

# 3. UI: Weightage Button/Section
st.write("### ⚙️ Weightage Settings")
with st.expander("Click here to adjust Weightages (Total must = 100)"):
    user_weights = {}
    total_w = 0
    # Create 3 columns of inputs to save space
    cols = st.columns(3)
    for i, param in enumerate(params_info.keys()):
        with cols[i % 3]:
            # Setting default weights (can be adjusted)
            val = st.number_input(f"{param} Weight", 0, 100, 10 if i < 10 else 0)
            user_weights[param] = val
            total_w += val
    
    st.write(f"**Current Total Weightage: {total_w}**")
    if total_w != 100:
        st.warning("⚠️ Total must be exactly 100 to calculate.")

# 4. THE ACTION BUTTON
# This is the "Weightage Button" logic you requested
if st.button("📊 Calculate & Rank Now"):
    if total_w != 100:
        st.error("Error: The sum of weights is not 100.")
    elif st_type == "Select":
        st.error("Error: Please select a Scheme Type.")
    else:
        # Filter strictly the selected part
        data = df_master[(df_master['Scheme Type'] == st_type) & (df_master['Scheme Category'] == st_cat)].copy()
        
        # Calculation: (Higher Params * Weight) - (Lower Params * Weight)
        def get_score(row):
            s = 0
            for p, w in user_weights.items():
                if params_info[p] == "higher":
                    s += (row[p] * w)
                else:
                    s -= (row[p] * w)
            return s

        data['Score'] = data.apply(get_score, axis=1)
        data = data.sort_values("Score", ascending=False)
        data['Rank'] = range(1, len(data) + 1)

        # Move Rank after Score
        cols = [c for c in data.columns if c not in ['Score', 'Rank']] + ['Score', 'Rank']
        data = data[cols]

        # Display results only after clicking
        st.success(f"Calculated ranking for {len(data)} funds.")
        st.dataframe(data, use_container_width=True, hide_index=True)
        
        st.download_button("⬇️ Download This Ranked List", data.to_csv(index=False), "ranked_output.csv")
