import streamlit as st
from utils import utility
import pandas as pd
import os
import plotly.express as px

from datetime import datetime

st.set_page_config(
    page_title="Network Analysis Dashboard",
    page_icon=":globe_with_meridians:",
    initial_sidebar_state="auto",
)

LIST_FILE = [
    "data/dionaea_ews_log.csv",
    "data/dionaea_log_compress.csv",
    "data/honeypot_log_2023_04_27.csv",
]

dict_interval = {
    "5 minutes": "5min",
    "15 minutes": "15min",
    "30 minutes": "30min",
    "1 hour": "1H",
    "3 hours": "3H",
    "6 hours": "6H",
    "12 hours": "12H",
    "1 Day": "D",
    "1 Week": "W",
}

st.title("Network Analysis Dashboard :globe_with_meridians:")

st.sidebar.title("Select data file")
file_path = st.sidebar.selectbox(
    "Select data file", [f.split("/")[-1] for f in LIST_FILE]
)

df = utility.load_data(os.path.join("data", file_path))

DATE_START = df["timestamp"].min()
DATE_END = df["timestamp"].max()

st.sidebar.title("Select time period")

start_date = st.sidebar.date_input(
    "Start date", datetime.strptime(DATE_START, "%Y-%m-%d %H:%M:%S")
)
end_date = st.sidebar.date_input(
    "End date", datetime.strptime(DATE_END, "%Y-%m-%d %H:%M:%S")
)

df = utility.filter_data_by_date(df, "timestamp", start_date, end_date)

st.subheader("Sample data")
st.table(df.head())
st.write(f"Total rows retrieved: `{df.shape[0]}`")

st.subheader("Data Analysis")

if file_path == "honeypot_log_2023_04_27.csv":
    fig = utility.create_plot(
        df=df,
        columns="honeypot",
        agg={"honeypot": "count"},
        x_col="honeypot",
        rename_col="honeypot",
        target_col="count",
        sort_column="count",
        title="Frequency of Honeypot Types",
        x_label="Honeypot Types",
        y_label="Frequency",
    )
    st.plotly_chart(fig)

    st.subheader("Login Attempts Over Time")
    interval = st.selectbox(
        "Select interval",
        [
            "5 minutes",
            "15 minutes",
            "30 minutes",
            "1 hour",
            "3 hours",
            "6 hours",
            "12 hours",
        ],
        index=0,
    )

    attempt_by_time = df.groupby(by=["timestamp", "login"]).size().unstack(fill_value=0).reset_index()
    attempt_by_time["timestamp"] = pd.to_datetime(attempt_by_time["timestamp"])
    attempt_by_time = attempt_by_time.set_index("timestamp").resample(dict_interval[interval]).sum().reset_index()

    fig = px.line(
        attempt_by_time,
        x="timestamp",
        y=["Success", "Fail"],
        title=f"Login Attempts Over Time ({interval} interval)",
        labels={"value": "Count", "timestamp": "Time"},
        color_discrete_sequence=px.colors.qualitative.Vivid,
        markers=True,
    )
    st.plotly_chart(fig)

    st.subheader("Login Rates")

    fig = utility.create_plot(
        df=df,
        columns=["login"],
        agg={"login": "count"},
        x_col="login",
        rename_col="login",
        target_col="count",
        sort_column="count",
        title="Login Rates by Status",
        x_label="Status Login",
        y_label="Jumlah",
        type_plot="pie",
    )
    st.plotly_chart(fig)

    st.subheader("Login Succsess by IP")
    fig = utility.create_plot(
        df=df[df["login"] == "Success"],
        columns=["source_address"],
        agg={"source_address": "count"},
        x_col="source_address",
        rename_col="source_address",
        target_col="count",
        sort_column="count",
        title="Login Success by IP",
        x_label="IP Address",
        y_label="Jumlah",
    )
    st.plotly_chart(fig)

    st.subheader("Login Failed by IP")
    fig = utility.create_plot(
        df=df[df["login"] == "Fail"],
        columns=["source_address"],
        agg={"source_address": "count"},
        x_col="source_address",
        rename_col="source_address",
        target_col="count",
        sort_column="count",
        title="Login Failed by IP",
        x_label="IP Address",
        y_label="Jumlah",
    )
    st.plotly_chart(fig)

    st.subheader("Top 10 Source Address")
    fig = utility.create_plot(
        df=df,
        columns=["source_address", "target_address"],
        agg={"target_address": "count"},
        x_col="source_address",
        rename_col="target_address",
        target_col="count",
        sort_column="count",
        title="Top 10 Source Address",
        x_label="IP Address",
        y_label="Jumlah",
    )
    st.plotly_chart(fig)

elif file_path == "dionaea_log_compress.csv":

    df_mapping = pd.read_csv("data/dionaea_log_category.csv")
    st.subheader("Top 10 Source Address")
    fig = utility.create_plot(
        df=df,
        columns=["src_ip"],
        agg={"src_ip": "count"},
        x_col="src_ip",
        rename_col="src_ip",
        target_col="count",
        sort_column="count",
        title="Top 10 Source IP Address",
        x_label="IP Address",
        y_label="Jumlah",
    )
    st.plotly_chart(fig)

    st.subheader("Trend of Attempts Over Time")

    interval = st.selectbox(
        "Select interval",
        [
            "30 minutes",
            "1 hour",
            "3 hours",
            "6 hours",
            "12 hours",
            "1 Day",
            "1 Week",
        ],
        index=0,
    )

    attempt_by_time = df.groupby(by="timestamp").agg({
        "src_ip": "count"
    }).rename(columns={"src_ip": "count"}).reset_index()
    attempt_by_time["timestamp"] = pd.to_datetime(attempt_by_time["timestamp"])
    attempt_by_time = attempt_by_time.set_index("timestamp").resample(dict_interval[interval]).sum().reset_index()

    fig = px.line(
        attempt_by_time,
        x="timestamp",
        y="count",
        title=f"Login Attempts Over Time ({interval} interval)",
        labels={"value": "Count", "timestamp": "Time"},
        color_discrete_sequence=px.colors.qualitative.Vivid,
        markers=True,
    )
    st.plotly_chart(fig)

    st.subheader("Top 10 Username and Password")

    fig = utility.create_plot(
        df=df,
        columns=["username"],
        agg={"username": "count"},
        x_col="username",
        rename_col="username",
        target_col="count",
        sort_column="count",
        title="Top 10 Username",
        x_label="Username",
        y_label="Jumlah",
    )
    st.plotly_chart(fig)

    fig = utility.create_plot(
        df=df,
        columns=["password"],
        agg={"password": "count"},
        x_col="password",
        rename_col="password",
        target_col="count",
        sort_column="count",
        title="Top 10 Password",
        x_label="Password",
        y_label="Jumlah",
    )
    st.plotly_chart(fig)

    st.subheader("Rate of Login Attempts by type")
    df["type"] = df_mapping["type"]

    fig = utility.create_plot(
        df=df,
        columns=["type"],
        agg={"type": "count"},
        x_col="type",
        rename_col="type",
        target_col="count",
        sort_column="count",
        title="Rate of Login Attempts by type",
        x_label="Type",
        y_label="Jumlah",
        type_plot="pie",
    )
    st.plotly_chart(fig)

    st.subheader("Rate of Login Attempts by protocol")
    df["protocol"] = df_mapping["protocol"]

    fig = utility.create_plot(
        df=df,
        columns=["protocol"],
        agg={"protocol": "count"},
        x_col="protocol",
        rename_col="protocol",
        target_col="count",
        sort_column="count",
        title="Rate of Login Attempts by protocol",
        x_label="Protocol",
        y_label="Jumlah",
        type_plot="pie",
    )
    st.plotly_chart(fig)

    st.subheader("Rate of Login Attempts by transport")
    df["transport"] = df_mapping["transport"]

    fig = utility.create_plot(
        df=df,
        columns=["transport"],
        agg={"transport": "count"},
        x_col="transport",
        rename_col="transport",
        target_col="count",
        sort_column="count",
        title="Rate of Login Attempts by transport",
        x_label="Transport",
        y_label="Jumlah",
        type_plot="pie",
    )
    st.plotly_chart(fig)

    st.subheader("Total Attempts each destination ip")
    fig = utility.create_plot(
        df=df,
        columns=["dst_ip"],
        agg={"dst_ip": "count"},
        x_col="dst_ip",
        rename_col="dst_ip",
        target_col="count",
        sort_column="count",
        title="Total Attempts each destination ip",
        x_label="IP Address",
        y_label="Jumlah",
    )
    st.plotly_chart(fig)

elif file_path == "dionaea_ews_log.csv":
    
    # Change to object
    df["src_port"] = df["src_port"].apply(lambda x: str(x))
    df["dest_port"] = df["dest_port"].apply(lambda x: str(x))

    st.subheader("Total Access by Source Port")
    fig = utility.create_plot(
        df=df,
        columns=["src_port"],
        agg={"src_port": "count"},
        x_col="src_port",
        rename_col="src_port",
        target_col="count",
        sort_column="count",
        title="Total Access by Source Port",
        x_label="Source Port",
        y_label="Jumlah",
    )
    st.plotly_chart(fig)

    st.subheader("Total Access by Destination Port")

    fig = utility.create_plot(
        df=df,
        columns=["dest_port"],
        agg={"dest_port": "count"},
        x_col="dest_port",
        rename_col="dest_port",
        target_col="count",
        sort_column="count",
        title="Total Access by Destination Port",
        x_label="Destination Port",
        y_label="Jumlah",
    )
    st.plotly_chart(fig)

    st.subheader("Total Access by Source IP")
    fig = utility.create_plot(
        df=df,
        columns=["src_ip"],
        agg={"src_ip": "count"},
        x_col="src_ip",
        rename_col="src_ip",
        target_col="count",
        sort_column="count",
        title="Total Access by Source IP",
        x_label="Source IP",
        y_label="Jumlah",
    )
    st.plotly_chart(fig)


    interval = st.selectbox(
        "Select interval",
        [
            "30 minutes",
            "1 hour",
            "3 hours",
            "6 hours",
            "12 hours",
            "1 Day",
            "1 Week",
        ],
        index=0,
    )

    attempt_by_time = df.groupby(by="timestamp").agg({
        "src_ip": "count"
    }).rename(columns={"src_ip": "count"}).reset_index()
    attempt_by_time["timestamp"] = pd.to_datetime(attempt_by_time["timestamp"])
    attempt_by_time = attempt_by_time.set_index("timestamp").resample(dict_interval[interval]).sum().reset_index()

    fig = px.line(
        attempt_by_time,
        x="timestamp",
        y="count",
        title=f"Total Access Over Time ({interval} interval)",
        labels={"value": "Count", "timestamp": "Time"},
        color_discrete_sequence=px.colors.qualitative.Vivid,
        markers=True,
    )
    st.plotly_chart(fig)

    st.subheader("Anomaly Detection")
    df_ip = df.groupby(by=["src_ip"]).agg({
        "src_ip": "count",
    }).rename(columns={"src_ip": "count"}).reset_index().sort_values(by="count", ascending=False)
    df_anomaly = df_ip[df_ip["count"] > df_ip["count"].mean() + 2 * df_ip["count"].std()]
    df_anomaly.reset_index(inplace=True, drop=True)
    st.table(df_anomaly)
