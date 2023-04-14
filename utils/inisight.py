import pandas as pd
from utils import filter_production_date, aggregate_data, generate_plots

def find_closest_match_ut(genre, prod_year, dataset):
    """
    Compare a proposed new movie against similar movies in the dataset and
    visualize how the similar movies behaved.

    Args:
        genre (str): Genre of the proposed new movie.
        prod_year (int): Production year of the proposed new movie.
        dataset (pd.DataFrame): Dataset of movies to compare against.

    Returns:
        filter_df (pd.DataFrame): Filtered dataframe per genre and decade.
        aggregate_df (pd.DataFrame): Aggregated data for visualization.
    """

    # Define decade in which the proposed movie has been produced
    decade = prod_year // 10 * 10

    # filter df per start and end decade (+9 yrs)
    filter_df = filter_production_date(dataset, decade, decade + 9)
    filter_df = filter_df.explode("genres")
    filter_df = filter_df[filter_df["genres"].str.contains(genre)]

    aggregate_df = aggregate_data(filter_df)

    generate_plots(aggregate_df, genre, decade)

    return filter_df, aggregate_df