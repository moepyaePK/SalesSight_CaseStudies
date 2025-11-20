"""
forecasting_engine.py

This module contains the core business logic for time series forecasting.
It encapsulates data preparation, model training, prediction, and visualization,
separating these concerns from the Streamlit user interface. It primarily uses
the Prophet library for forecasting.
"""

import logging
from typing import Tuple, Dict, Any

import pandas as pd
import plotly.graph_objects as go
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly

# Configure logging for the module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def prepare_data_for_prophet(
    df: pd.DataFrame,
    date_col: str,
    value_col: str
) -> pd.DataFrame:
    """
    Prepares a DataFrame for use with the Prophet forecasting library.

    This function performs the following steps:
    1. Validates the presence of the specified date and value columns.
    2. Selects and renames the columns to 'ds' (datestamp) and 'y' (value)
       as required by Prophet.
    3. Converts the 'ds' column to datetime objects, handling parsing errors.
    4. Converts the 'y' column to a numeric type, handling conversion errors.
    5. Removes any rows with missing values in 'ds' or 'y'.
    6. Sorts the DataFrame by date.
    7. Removes duplicate timestamps, keeping the last observed value.

    Args:
        df (pd.DataFrame): The input DataFrame containing time series data.
        date_col (str): The name of the column containing dates.
        value_col (str): The name of the column containing the values to forecast.

    Returns:
        pd.DataFrame: A new DataFrame formatted for Prophet with 'ds' and 'y' columns.

    Raises:
        ValueError: If the specified date or value columns are not in the DataFrame,
                    or if the date column cannot be parsed into datetime objects,
                    or if the value column cannot be converted to a numeric type.
    """
    logger.info(f"Preparing data with date column '{date_col}' and value column '{value_col}'.")

    if date_col not in df.columns or value_col not in df.columns:
        msg = f"Columns '{date_col}' or '{value_col}' not found in DataFrame."
        logger.error(msg)
        raise ValueError(msg)

    # Create a new DataFrame to avoid modifying the original
    prepared_df = df[[date_col, value_col]].copy()
    prepared_df.rename(columns={date_col: 'ds', value_col: 'y'}, inplace=True)

    # Convert 'ds' to datetime
    prepared_df['ds'] = pd.to_datetime(prepared_df['ds'], errors='coerce')
    if prepared_df['ds'].isnull().any():
        msg = "Failed to parse one or more dates in the date column. Please check the format."
        logger.error(msg)
        raise ValueError(msg)

    # Convert 'y' to numeric
    prepared_df['y'] = pd.to_numeric(prepared_df['y'], errors='coerce')
    if prepared_df['y'].isnull().any():
        num_nulls = prepared_df['y'].isnull().sum()
        logger.warning(f"Found and removed {num_nulls} non-numeric or null values in the value column.")
        prepared_df.dropna(subset=['y'], inplace=True)

    if prepared_df.empty:
        msg = "DataFrame is empty after cleaning. Cannot proceed with forecasting."
        logger.error(msg)
        raise ValueError(msg)

    # Sort by date and remove duplicates
    prepared_df.sort_values(by='ds', inplace=True)
    prepared_df.drop_duplicates(subset=['ds'], keep='last', inplace=True)

    logger.info(f"Data preparation complete. Shape of prepared data: {prepared_df.shape}")
    return prepared_df


def generate_forecast(
    prepared_data: pd.DataFrame,
    periods: int,
    freq: str = 'D',
    **prophet_kwargs: Any
) -> Tuple[Prophet, pd.DataFrame]:
    """
    Generates a forecast using the Prophet model.

    Args:
        prepared_data (pd.DataFrame): A DataFrame prepared by `prepare_data_for_prophet`.
                                      Must contain 'ds' and 'y' columns.
        periods (int): The number of future periods to forecast.
        freq (str): The frequency of the forecast (e.g., 'D' for day, 'W' for week, 'M' for month).
        **prophet_kwargs: Additional keyword arguments to pass to the Prophet model constructor
                          (e.g., seasonality_mode, changepoint_prior_scale).

    Returns:
        Tuple[Prophet, pd.DataFrame]: A tuple containing the fitted Prophet model
                                      and the forecast DataFrame.

    Raises:
        ValueError: If the prepared data has fewer than two data points.
        Exception: For any errors encountered during model fitting or prediction.
    """
    if len(prepared_data) < 2:
        msg = "Insufficient data for forecasting. Prophet requires at least two data points."
        logger.error(msg)
        raise ValueError(msg)

    logger.info(f"Generating forecast for {periods} periods with frequency '{freq}'.")
    logger.info(f"Prophet parameters: {prophet_kwargs}")

    try:
        # Instantiate and fit the model
        model = Prophet(**prophet_kwargs)
        model.fit(prepared_data)

        # Create future dataframe and make predictions
        future = model.make_future_dataframe(periods=periods, freq=freq)
        forecast = model.predict(future)

        logger.info("Forecast generated successfully.")
        return model, forecast

    except Exception as e:
        logger.error(f"An error occurred during forecasting: {e}", exc_info=True)
        raise


def plot_forecast(
    model: Prophet,
    forecast: pd.DataFrame
) -> go.Figure:
    """
    Creates an interactive Plotly figure of the forecast.

    Args:
        model (Prophet): The fitted Prophet model.
        forecast (pd.DataFrame): The forecast DataFrame generated by the model.

    Returns:
        go.Figure: A Plotly figure object showing the forecast, actuals, and uncertainty intervals.
    """
    logger.info("Generating forecast plot.")
    try:
        fig = plot_plotly(model, forecast)
        fig.update_layout(
            title="Sales Forecast",
            xaxis_title="Date",
            yaxis_title="Sales",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        return fig
    except Exception as e:
        logger.error(f"Failed to create forecast plot: {e}", exc_info=True)
        # Return an empty figure as a fallback
        return go.Figure().update_layout(title="Error: Could not generate forecast plot")


def plot_forecast_components(
    model: Prophet,
    forecast: pd.DataFrame
) -> go.Figure:
    """
    Creates an interactive Plotly figure of the forecast components (trend, seasonality).

    Args:
        model (Prophet): The fitted Prophet model.
        forecast (pd.DataFrame): The forecast DataFrame generated by the model.

    Returns:
        go.Figure: A Plotly figure object showing the forecast components.
    """
    logger.info("Generating forecast components plot.")
    try:
        fig = plot_components_plotly(model, forecast)
        fig.update_layout(
            title="Forecast Components",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        return fig
    except Exception as e:
        logger.error(f"Failed to create forecast components plot: {e}", exc_info=True)
        # Return an empty figure as a fallback
        return go.Figure().update_layout(title="Error: Could not generate components plot")


def get_forecast_summary(forecast: pd.DataFrame, periods: int) -> pd.DataFrame:
    """
    Extracts and formats a summary of the future forecast values.

    Args:
        forecast (pd.DataFrame): The complete forecast DataFrame from Prophet.
        periods (int): The number of future periods that were forecasted.

    Returns:
        pd.DataFrame: A DataFrame containing the date, forecasted value, and
                      upper/lower bounds for the future periods.
    """
    logger.info(f"Extracting forecast summary for the next {periods} periods.")
    summary = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
    summary.rename(columns={
        'ds': 'Date',
        'yhat': 'Forecast',
        'yhat_lower': 'Lower Bound',
        'yhat_upper': 'Upper Bound'
    }, inplace=True)

    # Format for better readability
    for col in ['Forecast', 'Lower Bound', 'Upper Bound']:
        summary[col] = summary[col].round(2)

    summary['Date'] = summary['Date'].dt.date
    summary.set_index('Date', inplace=True)

    return summary