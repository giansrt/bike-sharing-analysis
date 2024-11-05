import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style="dark")

import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

# Baca file CSV dan konversi tanggal
day_df = pd.read_csv("cleaned_day.csv")
hour_df = pd.read_csv("cleaned_hour.csv")

day_df["dteday"] = pd.to_datetime(day_df["dteday"])


# Data RFM Analysis
def make_rfm_data(data):
    current_date = data["dteday"].max()
    rfm_df = (
        data.groupby("season")
        .agg(
            Recency=("dteday", lambda x: (current_date - x.max()).days),
            Frequency=("cnt", "count"),
            Monetary=("cnt", "sum"),
        )
        .reset_index()
    )
    return rfm_df


# Sidebar filter
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    st.image(
        "https://github.com/giansrt/bike-sharing-analysis/blob/main/Full%20Color.png?raw=true"
    )
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )
main_day_df = day_df[
    (day_df["dteday"] >= str(start_date)) & (day_df["dteday"] <= str(end_date))
]
main_hour_df = hour_df[
    (hour_df["dteday"] >= str(start_date)) & (hour_df["dteday"] <= str(end_date))
]

# Membuat agregasi data
season_data = (
    main_day_df.groupby(by=["season"])
    .agg({"casual": "sum", "registered": "sum", "cnt": "sum"})
    .reset_index()
)
season_data_unpivot = pd.melt(
    season_data,
    id_vars=["season"],
    value_vars=["casual", "registered"],
    var_name="status",
    value_name="Count",
)

year_data = (
    main_day_df.groupby(by=["yr", "mnth"])
    .agg({"casual": "sum", "registered": "sum"})
    .reset_index()
)
year_data["total"] = year_data["casual"] + year_data["registered"]

wheater_data = (
    main_day_df.groupby(by=["weathersit"])
    .agg({"casual": "sum", "registered": "sum", "cnt": "sum"})
    .reset_index()
)
weathersit_data_unpivot = pd.melt(
    wheater_data,
    id_vars=["weathersit"],
    value_vars=["casual", "registered"],
    var_name="status",
    value_name="Count",
)

# RFM data
rfm_df = make_rfm_data(main_day_df)

st.header("Rental Bike Sharing Dashboard 🚵‍♀️")
st.subheader("Count Rent")
col1, col2, col3 = st.columns(3)

with col1:
    total_rent = day_df.cnt.sum()
    st.metric("Total Rent", value=total_rent)
with col2:
    registered = day_df.registered.sum()
    st.metric("Total Registered", value=registered)
with col3:
    casual = day_df.casual.sum()
    st.metric("Total Casual", value=casual)

st.subheader("Bicycle Rental Count by day")
# Pilihan y-axis untuk plot
y_axis = st.selectbox(
    "Pilih kolom Y-Axis untuk grafik",
    options=["registered", "casual", "cnt"],  # Pilihan kolom untuk y-axis
    index=0,  # Default memilih "registered"
)


# Fungsi untuk memperbarui dan menampilkan grafik berdasarkan pilihan y-axis
def update_plot(y_axis):
    plt.figure(figsize=(15, 5))
    sns.barplot(
        x="weekday",
        y=y_axis,
        data=main_day_df,
        palette="magma",
        order=[
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ],
    )
    plt.title(f"Bicycle Rental Count by day {y_axis.capitalize()}")
    plt.xlabel("Weekday")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    st.pyplot(plt)


# Memanggil fungsi untuk memperbarui dan menampilkan grafik
update_plot(y_axis)

st.subheader("Hourly Count of casual and registered bikeshere riders")
plt.figure(figsize=(16, 5))
sns.lineplot(data=main_hour_df, x="hr", y="casual", label="Casual", ci=None)
sns.lineplot(data=main_hour_df, x="hr", y="registered", label="Registered", ci=None)
sns.lineplot(data=main_hour_df, x="hr", y="cnt", label="ALL", ci=None)
plt.title("Hourly Count of casual and registered bikeshere riders")
plt.xlabel("Hour")
plt.ylabel("Total Riders")
plt.xticks(ticks=range(0, 24), labels=[str(i) for i in range(24)])
st.pyplot(plt)


st.subheader("Bikeshere riders by Season")
plt.figure(figsize=(10, 6))
sns.barplot(x="season", y="Count", data=season_data_unpivot, hue="status")
plt.xlabel("Season")
plt.ylabel("Total Rides")
plt.title("Count of bikeshare rides by Season")
st.pyplot(plt)


st.subheader("Monthly Count of casual and registered bikeshere riders")
plt.figure(figsize=(16, 5))
sns.lineplot(data=year_data, x="mnth", y="casual", label="Casual", ci=None)
sns.lineplot(data=year_data, x="mnth", y="registered", label="Registered", ci=None)
sns.lineplot(data=year_data, x="mnth", y="total", label="Total", ci=None)
plt.title("Monthly Count of casual and registered bikeshere riders")
plt.xlabel("Month")
plt.ylabel("Total Riders")
st.pyplot(plt)


st.subheader("Count of bikeshare rides by Season")
plt.figure(figsize=(10, 6))
sns.barplot(
    x="weathersit",
    y=weathersit_data_unpivot["Count"],
    data=weathersit_data_unpivot,
    hue="status",
)
plt.xlabel("Season")
plt.ylabel("Total Rides")
plt.title("Count of bikeshare rides by Season")
st.pyplot(plt)


st.subheader("RFM Analysis Season")
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df["Recency"].mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df["Frequency"].mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = round(rfm_df["Monetary"].mean(), 2)
    st.metric("Average Monetary", value=avg_monetary)

# Membuat visualisasi bar plot untuk RFM berdasarkan setiap musim
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

# Recency
sns.barplot(
    y="Recency",
    x="season",
    data=rfm_df.sort_values(by="Recency", ascending=True),
    palette=colors,
    ax=ax[0],
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Season", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis="y", labelsize=30)
ax[0].tick_params(axis="x", labelsize=35)

# Frequency
sns.barplot(
    y="Frequency",
    x="season",
    data=rfm_df.sort_values(by="Frequency", ascending=False),
    palette=colors,
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Season", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis="y", labelsize=30)
ax[1].tick_params(axis="x", labelsize=35)

# Monetary
sns.barplot(
    y="Monetary",
    x="season",
    data=rfm_df.sort_values(by="Monetary", ascending=False),
    palette=colors,
    ax=ax[2],
)
ax[2].set_ylabel(None)
ax[2].set_xlabel("Season", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis="y", labelsize=30)
ax[2].tick_params(axis="x", labelsize=35)
st.pyplot(fig)

# expander explanation RFM Analysis
with st.expander("See Explanation of RFM Analysis"):
    st.write(
        "1. **Average Recency (76.2 days)**: Represents the average number of days since the last rental. Spring has the lowest recency value (most recent interactions), while summer has the highest (longer time since last use)."
    )
    st.write(
        "2. **Average Frequency (182.75 days)**: Indicates the average number of days bikes were used per season, with fall and summer showing the highest frequency, and winter and spring slightly lower but still high."
    )
    st.write(
        "3. **Average Monetary (823169.75)**: Reflects the average total number of bikes rented per season. Fall has the highest value, followed by summer and winter, with spring having the lowest, indicating peak demand in fall and the lowest demand in spring."
    )
