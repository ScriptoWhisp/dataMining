# streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import matplotlib.pyplot as plt

st.title("Electricity Consumption Visualization")

# Sidebar: fetch and select datasets
st.sidebar.header("Datasets Configuration")
if 'catalog' not in st.session_state:
    if st.sidebar.button("Load Dataset Catalog"):
        resp = requests.get("https://decision.cs.taltech.ee/electricity/api/")
        resp.raise_for_status()
        st.session_state.catalog = resp.json()

if 'catalog' in st.session_state:
    catalog = st.session_state.catalog
    hashes = [entry['dataset'] for entry in catalog]
    selected = st.sidebar.multiselect("Select up to 5 datasets", hashes, default=hashes[:3], max_selections=5)
else:
    st.sidebar.info("Click 'Load Dataset Catalog'")


# Function to load a dataset given its hash
@st.cache_data
def load_dataset(hash_id):
    url = f"https://decision.cs.taltech.ee/electricity/data/{hash_id}.csv"
    txt = requests.get(url).text.splitlines()
    start = next(i for i, l in enumerate(txt) if l.startswith("Periood;"))
    data = "\n".join(txt[start:])
    df = pd.read_csv(io.StringIO(data), sep=';', decimal=',')
    print(df.columns)
    df = df.rename(columns={'Periood': 'Datetime', 'Tarbitud energia (vÃµrgust) / kWh': 'Tarbitud energia'})

    df['Datetime'] = pd.to_datetime(df['Datetime'], format='%d.%m.%Y %H:%M', dayfirst=True)
    return df.set_index('Datetime').sort_index()


# Main: visualizations
if 'catalog' in st.session_state and selected:
    # Load dataframes
    datasets = {h: load_dataset(h) for h in selected}

    st.subheader("1) Single-dataset 100-day Heatmap")
    ds_hash = st.selectbox("Choose dataset", selected)
    days = st.slider("Number of days", min_value=7, max_value=365, value=100)
    df0 = datasets[ds_hash]
    if len(df0) >= days * 24:
        block = df0['Tarbitud energia'].iloc[:days * 24].values.reshape(days, 24)
        fig, ax = plt.subplots(figsize=(8, 4))
        im = ax.imshow(block, aspect='auto')
        fig.colorbar(im, ax=ax, label='kWh')
        ax.set_xlabel("Hour of day")
        ax.set_ylabel("Day index")
        st.pyplot(fig)
    else:
        st.error("Dataset has fewer than requested hours")

    st.subheader("2) Multi-dataset Same-day Overlay")
    date = st.date_input("Select date for overlay", df0.index[0].date())
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    for name, df in datasets.items():
        if date in df.index.date:
            series = df.loc[df.index.date == date, 'Tarbitud energia']
            ax2.plot(series.index.hour, series.values, alpha=0.3, label=name)
    ax2.set_xlabel("Hour of day")
    ax2.set_ylabel("kWh")
    ax2.legend(fontsize='small')
    st.pyplot(fig2)

    st.markdown("📌 The app runs on Streamlit; deploy to [Streamlit Cloud](https://share.streamlit.io/) by pushing this file to GitHub.")
