from datetime import datetime
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.cm import ScalarMappable
from wordcloud import WordCloud


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


def get_tags_per_movieId(movieId: int, tags_df: pd.DataFrame) -> list:
    """
    Use to get all tags per movieId
    Args:
        movieId
        tags_df: dataframe from tags dataset
    Returns:
        list of tags per movieId.
    """
    return list(tags_df[tags_df.movieId == movieId]["tag"])


def aggregate_data(df: pd.DataFrame, movies_df) -> pd.DataFrame:
    """
    Use to aggregate total_views (count_views), average_ratings (rating_means), and get all tags collected per movieId
    Arg:
        df: dataframe with preferred time interval already defined
        movies_df: dataframe from the movies dataset
    Returns:
        a copy datframe of movies_df
    """

    movies_df_copy = movies_df.copy()

    count_views = pd.DataFrame(df.groupby("movieId")["movieId"].count()).rename(
        columns={"movieId": "total_views"}
    )

    rating_means = pd.DataFrame(df.groupby("movieId")["rating"].mean()).rename(
        columns={"rating": "average_rating"}
    )

    movies_df_copy = pd.merge(movies_df, count_views, on="movieId")

    movies_df_copy = pd.merge(movies_df_copy, rating_means, on="movieId")

    # get all tags per movieId
    movies_df_copy["tags"] = movies_df_copy["movieId"].apply(
        lambda x: get_tags_per_movieId(x)
    )

    return movies_df_copy


def generate_plots(movies_df: pd.DataFrame, genre: str, decade: int, top: int = 20):
    """
    Use to generate insights based on movies_df. By default, the insights will
    be generated based on the top 20 movies.
    """

    # sample data
    movies_df = movies_df.sort_values(by="total_views", ascending=False).head(top)

    # define colors for shading based on ratings
    cmap = plt.cm.get_cmap("viridis", 10)  # Choose a colormap with 10 shades
    ratings = movies_df["average_rating"]  # Ratings data from your dataframe
    normalized_ratings = (ratings - 1) / 4  # Normalize ratings to range [0,1]
    colors = cmap.reversed()(normalized_ratings)  # Reverse the colormap

    # create a figure with three subplots
    fig, axs = plt.subplots(3, 1, figsize=(10, 15))

    # reduce alpha value to increase contrast of bars
    colors = [(c[0], c[1], c[2], 0.7) for c in colors]  # Set alpha value to 0.7

    # plot the horizontal bar chart on the first subplot
    barh = axs[0].barh(movies_df["title"], movies_df["total_views"], color=colors)
    axs[0].set_xlabel("Total views")
    axs[0].set_title(
        f"Total Views by Top {genre} {top} movies produced in the {decade}s and Average Ratings",
        fontweight="bold",
    )

    # create a custom legend for the first subplot
    legend_labels = [
        plt.Line2D([0], [0], color=cmap.reversed()(0.2), lw=6),
        plt.Line2D([0], [0], color=cmap.reversed()(0.5), lw=6),
        plt.Line2D([0], [0], color=cmap.reversed()(0.8), lw=6),
    ]
    legend_texts = ["Low Rating (<3)", "Medium Rating (3)", "High Rating (>3)"]
    axs[0].legend(legend_labels, legend_texts, loc="upper right")

    # add rating labels inside the bars in the first subplot
    for i, bar in enumerate(barh):
        rating = movies_df.iloc[i]["average_rating"]
        axs[0].text(
            bar.get_width() - 0.2,
            bar.get_y() + bar.get_height() / 2,
            f"{rating:.1f}",
            color="white",
            ha="right",
            va="center",
        )

    # plot the scatter plot on the second subplot
    axs[1].scatter(
        movies_df.sort_values(by="total_views", ascending=False)["average_rating"],
        movies_df.sort_values(by="total_views", ascending=False)["total_views"],
        color="green",
    )
    axs[1].set_xlabel("Average Rating")
    axs[1].set_ylabel("Total Views")
    axs[1].set_title(
        f"Correlation between Total Views and Average Rating of the Top {top} movies produced in the {decade}s",
        fontweight="bold",
    )

    # generate the word cloud from the "tags" column on the third subplot
    wordcloud = WordCloud(width=800, height=400).generate(
        " ".join(movies_df["tags"].explode().dropna())
    )

    # plot the word cloud on the third subplot
    axs[2].imshow(wordcloud, interpolation="bilinear")
    axs[2].axis("off")
    axs[2].set_title(f"Tags generated by the users for these movies", fontweight="bold")

 
    plt.tight_layout()


    plt.show


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
