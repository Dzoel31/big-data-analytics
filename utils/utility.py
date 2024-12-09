import pandas as pd
import numpy as np

import plotly.express as px

from datetime import datetime, timedelta

from plotly.graph_objs._figure import Figure

from typing import List, Dict


def get_year(date: str | datetime) -> int:
    """Extract the year from a date string or datetime object."""
    if isinstance(date, str):
        date = pd.to_datetime(date)
    return date.year


def create_time_series(
    df: pd.DataFrame, date_col: str, freq: str = "D"
) -> pd.DataFrame:
    """Create a time series from a DataFrame."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df.set_index(date_col, inplace=True)
    df = df.resample(freq).sum()
    df.reset_index(inplace=True)
    return df


def load_data(file_path: str, compress: bool = True) -> pd.DataFrame:
    """Load data from a CSV file."""
    df = pd.read_csv(file_path)
    if compress:
        df = compress_data(df)
    return df


def is_convertible_to_datetime(series: pd.Series) -> bool:
    """Check if a series can be converted to datetime."""
    try:
        pd.to_datetime(series)
        return True
    except (ValueError, TypeError):
        return False


def compress_data(df: pd.DataFrame) -> pd.DataFrame:
    """Compress data types to reduce memory usage."""
    for col in df.select_dtypes(include=[np.float64]):
        df[col] = pd.to_numeric(df[col], downcast="float")
    for col in df.select_dtypes(include=[np.int64]):
        df[col] = pd.to_numeric(df[col], downcast="signed")

    # Check if Object data can be converted to datetime
    for col in df.select_dtypes(include=["object"]):
        if is_convertible_to_datetime(df[col]):
            df[col] = pd.to_datetime(df[col], format="mixed").dt.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    return df


def filter_data_by_date(
    df: pd.DataFrame, date_col: str, start_date: str, end_date: str
) -> pd.DataFrame:
    """Filter data between two dates."""
    df["filter_date"] = pd.to_datetime(df[date_col]).dt.date
    mask = (df["filter_date"] >= start_date) & (df["filter_date"] <= end_date)
    df.drop(columns=["filter_date"], inplace=True)
    return df.loc[mask]


def create_plot(
    df: pd.DataFrame,
    columns: List[str] | str,
    agg: Dict[str, str],
    x_col: str,
    rename_col: str,
    target_col: str,
    sort_column: str,
    title: str,
    x_label: str,
    y_label: str,
    ntop: int = 10,
    pallette: str = "viridis",
    type_plot: str = "bar",
) -> Figure | None:
    """Create a plotly plot."""
    df_filtered = (
        df.groupby(by=columns).agg(agg).rename(columns={rename_col: target_col})
    )
    df_filtered.reset_index(inplace=True)
    df_filtered.sort_values(by=sort_column, ascending=False, inplace=True)

    if type_plot == "bar":
        fig = px.bar(
            df_filtered.head(ntop),
            x=x_col,
            y=target_col,
            color=x_col,
            text=target_col,
            title=title,
            labels={x_col: x_label, target_col: y_label},
            color_discrete_sequence=px.colors.qualitative.Vivid,
            text_auto=True,
        )

        fig.update_layout(
            xaxis=dict(type="category"),
            yaxis=dict(title=y_label),
            legend_title_text=x_label,
        )
        return fig
    elif type_plot == "line":
        return px.line(
            df_filtered,
            x=x_col,
            y=target_col,
            title=title,
            labels={x_col: x_label, target_col: y_label},
            color_discrete_sequence=px.colors.qualitative.Vivid,
            markers=True,
        )

    elif type_plot == "pie":
        return px.pie(
            df_filtered,
            names=x_col,
            values=target_col,
            title=title,
            labels={x_col: x_label, target_col: y_label},
            width=800,
            height=600,
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
