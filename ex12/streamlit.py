import streamlit as st
import pandas as pd
import requests, io
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Electricity Patterns", layout="wide")
st.title("Electricity Consumption Patterns")

# Sidebar: Dataset Selection
st.sidebar.header("Dataset selection")
if "catalog" not in st.session_state:
    if st.sidebar.button("Load dataset catalog"):
        resp = requests.get("https://decision.cs.taltech.ee/electricity/api/")
        resp.raise_for_status()
        st.session_state.catalog = resp.json()

if "catalog" in st.session_state:
    hashes = [entry["dataset"] for entry in st.session_state.catalog]
    hash_sel = st.sidebar.selectbox("Dataset hash", hashes)
else:
    st.sidebar.info("Click “Load dataset catalog” to begin")
    st.stop()

# Data Loading Function
@st.cache_data(ttl=3600)
def load_df(hash_id):
    url = f"https://decision.cs.taltech.ee/electricity/data/{hash_id}.csv"
    raw = requests.get(url).text.splitlines()
    start = next(i for i, l in enumerate(raw) if l.startswith("Periood;"))
    buf = "\n".join(raw[start:])
    df = pd.read_csv(io.StringIO(buf), sep=";", decimal=",")
    df.rename(columns={"Periood": "Datetime", "Tarbitud energia (vÃµrgust) / kWh": "kWh"}, inplace=True)
    df['Datetime'] = pd.to_datetime(df['Datetime'], dayfirst=True, infer_datetime_format=True)
    return df.set_index("Datetime").sort_index()

df = load_df(hash_sel)

# Sidebar: Date Control
st.sidebar.markdown("---")

# Section: Consumption Patterns
st.title("Consumption Patterns")

## Average 24h Profile by Weekday
st.subheader("Average 24h Profile by Weekday")
df_ss = df.copy()
df_ss["Weekday"] = df_ss.index.day_name()
df_ss["Hour"] = df_ss.index.hour
avg = df_ss.groupby(["Weekday","Hour"])["kWh"].mean().reset_index()
weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
fig1 = px.line(avg, x="Hour", y="kWh", color="Weekday",
               category_orders={"Weekday": weekday_order},
               labels={"kWh":"Mean kWh"}, title="Average Daily Curve per Weekday")
st.plotly_chart(fig1, use_container_width=True)

## Calendar Heatmap of Daily Consumption
st.subheader("Calendar Heatmap of Daily Consumption")
daily = df.resample("D")["kWh"].sum().reset_index(name="DailyTotal")
daily["ISOWeek"] = daily["Datetime"].dt.isocalendar().week
daily["Weekday"] = daily["Datetime"].dt.day_name()
pivot = daily.pivot_table(index="ISOWeek", columns="Weekday", values="DailyTotal", aggfunc="mean").reindex(columns=weekday_order)
fig2 = px.imshow(pivot, labels={"x":"Weekday","y":"ISO Week","color":"kWh/day"},
                 x=weekday_order, aspect="auto", color_continuous_scale="Viridis",
                 title="Daily Totals: Weeks vs Weekdays")
st.plotly_chart(fig2, use_container_width=True)

## Hourly Distribution by Weekday with Mean Curve
st.subheader("Hourly Distribution by Weekday with Mean Curve")
weekday_sel = st.selectbox("Choose weekday", weekday_order)
df_dist = df.copy()
df_dist['Weekday'] = df_dist.index.day_name()
df_dist['Hour'] = df_dist.index.hour
df_sel = df_dist[df_dist['Weekday'] == weekday_sel]
hourly_mean = df_sel.groupby('Hour')['kWh'].mean().reset_index()
fig = px.box(df_sel, x='Hour', y='kWh', points='all',
             labels={'kWh':'kWh','Hour':'Hour of day'},
             title=f'Hourly kWh Distribution on {weekday_sel}s')
fig.add_trace(go.Scatter(x=hourly_mean['Hour'], y=hourly_mean['kWh'],
                         mode='lines+markers', name='Mean',
                         line=dict(width=3), marker=dict(size=6, color='red')))
st.plotly_chart(fig, use_container_width=True)

# Section: Multi-dataset Same-Day Patterns
st.header("Multi-dataset Patterns")

DEFAULT_HASHES = [
    "1fecd574c4e953d91743336917",
    "44e2cb4caa1616d61743847885",
    "2d62a14b1045db681744471246",
    "eb18877694cc036a1742320408",
    "51938054027b94021743707452"
]

if "sampled" not in st.session_state:
    st.session_state.sampled = DEFAULT_HASHES

st.sidebar.header("Datasets Configuration")
if st.sidebar.button("Reset to default selection"):
    st.session_state.sampled = DEFAULT_HASHES

st.write(f"Selected hashes:", st.session_state.sampled)

# Load Multiple Datasets
@st.cache_data(ttl=3600)
def load_all(hlist):
    return {h: load_df(h) for h in hlist}

datasets = load_all(st.session_state.sampled)

## Mean 24h Profile by Weekday (across all datasets)
st.subheader("Mean 24h Profile by Weekday (across all datasets)")
df_all = pd.concat(datasets.values(), keys=datasets.keys(), names=["Dataset","Datetime"]).reset_index(level=1).rename(columns={"level_1":"Datetime"})
df_all["Weekday"] = df_all["Datetime"].dt.day_name()
df_all["Hour"] = df_all["Datetime"].dt.hour
avg = df_all.groupby(["Weekday","Hour"])["kWh"].mean().reset_index()
fig1 = px.line(avg, x="Hour", y="kWh", color="Weekday",
               category_orders={"Weekday": weekday_order},
               labels={"kWh":"Avg kWh"}, title="Average Hourly Curve by Weekday")
st.plotly_chart(fig1, use_container_width=True)

## Same-Day Overlay for Selected Date
st.subheader("Same-Day Overlay for Selected Date")
min_date = max(df.index.min().date() for df in datasets.values())
max_date = min(df.index.max().date() for df in datasets.values())
sel_date = st.date_input("Select date", min_value=min_date, max_value=max_date, value=min_date)
fig2 = go.Figure()
for h, df in datasets.items():
    day = df.loc[df.index.date == sel_date, "kWh"]
    if not day.empty:
        fig2.add_trace(go.Scatter(x=day.index.hour, y=day.values, mode="lines",
                                  name=h, opacity=0.4, showlegend=False))
hours = sorted(set().union(*(df.loc[df.index.date==sel_date].index.hour for df in datasets.values())))
mean_vals = [np.mean([df.loc[df.index.hour==hr, "kWh"].mean() for df in datasets.values() if hr in df.index.hour]) for hr in hours]
fig2.add_trace(go.Scatter(x=hours, y=mean_vals, mode="lines+markers",
                          line=dict(width=3, color="red"), name="Mean", showlegend=True))
fig2.update_layout(title=f"Overlay of {len(datasets)} Series on {sel_date}", xaxis_title="Hour", yaxis_title="kWh")
st.plotly_chart(fig2, use_container_width=True)

## Violin: Distribution Across Datasets by Hour
st.subheader("Violin: Distribution Across Datasets by Hour")
matrix = []
for df in datasets.values():
    day = df.loc[df.index.date == sel_date, "kWh"]
    hours_idx = pd.date_range(start=sel_date, periods=24, freq="H")
    full_day = day.reindex(hours_idx, fill_value=np.nan)
    matrix.append(full_day.values)
arr = np.vstack(matrix)
series_ids = [f"Series {i+1}" for i in range(arr.shape[0])]
df_mat = pd.DataFrame(arr, index=series_ids, columns=list(range(24)))
df_v = df_mat.reset_index().melt(id_vars="index", var_name="Hour", value_name="kWh").rename(columns={"index": "Dataset"})
fig4 = px.violin(df_v, x="Hour", y="kWh", color="Dataset", box=True, points="all",
                 labels={"kWh": "kWh", "Hour": "Hour of day"},
                 title=f"Hourly Distribution Across {arr.shape[0]} Datasets on {sel_date}")
st.plotly_chart(fig4, use_container_width=True)

## Pie Chart: Total Consumption Share on Selected Date
st.subheader("Pie Chart: Total Consumption Share on Selected Date")
labels = []
values = []
for i, (h, df) in enumerate(datasets.items(), start=1):
    total = df.loc[df.index.date == sel_date, "kWh"].sum()
    if not np.isnan(total) and total > 0:
        labels.append(f"Series {i}")
        values.append(total)
if values:
    fig5 = px.pie(values=values, names=labels, title=f"Consumption share by dataset on {sel_date}", hole=0.3)
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.warning("No consumption data available for that date.")

## Pie Charts: Weekday & Month Distribution
st.subheader("Pie Charts: Weekday & Month Distribution")
col1, col2 = st.columns(2)
daily_list = [df['kWh'].resample('D').sum() for df in datasets.values()]
all_daily = pd.concat(daily_list)
df_daily = all_daily.to_frame(name='kWh')
df_daily['Weekday'] = df_daily.index.day_name()
df_daily['Month'] = df_daily.index.month_name()
weekday_avg = df_daily.groupby('Weekday')['kWh'].mean().reindex(weekday_order)
with col1:
    fig6 = px.pie(names=weekday_avg.index, values=weekday_avg.values, title="Avg Daily Consumption by Weekday", hole=0.3)
    st.plotly_chart(fig6, use_container_width=True)
month_order = ["January","February","March","April","May","June","July","August","September","October","November","December"]
month_avg = df_daily.groupby('Month')['kWh'].mean().reindex(month_order)
with col2:
    fig7 = px.pie(names=month_avg.index, values=month_avg.values, title="Avg Daily Consumption by Month", hole=0.3)
    st.plotly_chart(fig7, use_container_width=True)

## Heatmap: Dataset Index vs Hour for Selected Date
st.subheader("Heatmap: Dataset Index vs Hour for Selected Date")
matrix = [
    df.loc[df.index.date==sel_date, "kWh"].reindex(pd.date_range(
        sel_date, sel_date + pd.Timedelta(hours=23), freq="H"
    ), fill_value=np.nan).values
    for df in datasets.values()
]
fig = px.imshow(
    pivot.values,                        # shape=(n_weeks, n_days)
    x=pivot.columns,                     # length == n_days
    y=pivot.index,                       # length == n_weeks
    labels={'x':'Weekday','y':'ISO Week','color':'kWh/day'},
    color_continuous_scale='Viridis',
    title='Daily totals: weeks vs weekdays'
)
st.plotly_chart(fig, use_container_width=True)