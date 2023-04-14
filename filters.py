from datetime import datetime
import pandas as pd


def filter_time_interval(
    df: pd.DataFrame, start_date: datetime, end_date: datetime
) -> pd.DataFrame:
    """
    Use to filter the dataset based on time interval. The time interval has
    been inferred from the time a movie has been rated, assuming that the
    userId rated the movie right after watching it.
    Args:
        df: pandas df with datetime_rating (assumed to be approximately
        the moment the movie has been watched), start_date, end_date.
    Returns:
        pandas df filtered for a defined time interval.
    """
    return df.loc[
        (df.datetime_rating >= start_date) & (df.datetime_rating <= end_date)
    ].sort_values(by="datetime_rating", ascending=False)


def filter_production_date(
    df: pd.DataFrame, prod_start: int, prod_end: int
) -> pd.DataFrame:
    """
    Use to filter the dataset based on production movie years.
    Args:
        df: pandas df with movie titles and production movie year,
        prod_start: start prodcution movie year,
        prod_end: end production movie year.
    Returns:
        pandas df filter by production movie year interval.
    """
    return df.loc[(df.movie_year >= prod_start) & (df.movie_year <= prod_end)]
