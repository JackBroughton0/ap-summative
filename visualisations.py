import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import mongodb_interaction


def format_dataframe(df, vis_input):
    """Format the dataframe so that only the data records
    with the requested DAB multiplexes are processed further"""
    # Get the requested DAB Multiplexes
    multiplexes = []
    for mp in ['C18A', 'C18F', 'C188']:
        if vis_input[mp]:
            multiplexes.append(mp)
    # Subset dataframe to only process required multiplexes
    df_list = []
    for mp in multiplexes:
        df_sub = df.loc[df[mp] == mp].copy()
        df_list.append(df_sub)
    df = pd.concat(df_list)
    return df, multiplexes


def produce_stats(df_mp):
    """Calculate the mean, median, and mode of Power(kW)
    for the specified DAB multiplex"""
    summary_stats = {}
    # Initialise 'Site Height' as an empty dictionary
    summary_stats['Site Height'] = {}
    # Initialise 'Date' as an empty dictionary
    summary_stats['Date'] = {}
    # Instantiate dataframe masks as requested by the client
    site_height_mask = (df_mp['Site Height'] > 75)
    date_mask = (df_mp['Date'].dt.year >= 2001)

    # Get mean, median, and mode where site height is greater than 75
    summary_stats['Site Height']['mean'] = df_mp.loc[site_height_mask]['Power(kW)'].mean()
    summary_stats['Site Height']['median'] = df_mp.loc[site_height_mask]['Power(kW)'].median()
    summary_stats['Site Height']['mode'] = df_mp.loc[site_height_mask]['Power(kW)'].mode()[0]

    # Get mean, median, and mode where the year is greater than or equal to 2001
    summary_stats['Date']['mean'] = df_mp.loc[date_mask]['Power(kW)'].mean()
    summary_stats['Date']['median'] = df_mp.loc[date_mask]['Power(kW)'].median()
    summary_stats['Date']['mode'] = df_mp.loc[date_mask]['Power(kW)'].mode()[0]
    return summary_stats

def summary_stats(df, multiplexes, figure_size):
    """Produce plot showing the mean, median, and mode of
    Power(kW) for the C18A, C18F, C188 DAB multiplexes where
    the year is more than 2001 and site height is greater than 75m"""
    # Create empty dict to store stats for all specified DAB multiplexes
    multiplex_stats = {}
    for multiplex in multiplexes:
        df_mp = df[df[multiplex]==multiplex].copy()
        multiplex_stats[multiplex] = produce_stats(df_mp)
    categories = ['mean', 'median', 'mode']
    data = {category: [multiplex_stats[m]['Site Height'][category] for m in multiplexes] for category in categories}

    # Create a figure with two subplots
    fig, axes = plt.subplots(1, 2, figsize=figure_size)
    for idx, variable in enumerate(['Date', 'Site Height']):
        data = {category: [multiplex_stats[m][variable][category] for m in multiplexes] for category in categories}
        ax = axes[idx]

        # Create a bar plot for each variable
        bar_width = 0.2
        x = np.arange(len(multiplexes))
        colors = ['b', 'g', 'r']
        for i, category in enumerate(categories):
            ax.bar(x + i * bar_width, data[category], bar_width, label=category, color=colors[i])

        ax.set_xlabel('DAB Multiplex')
        ax.set_ylabel('Power(kW)')
        ax.set_title(f"DAB Multiplex Power where {variable} > {'the year 2000' if variable=='Date' else '75m'}")
        ax.set_xticks(x + bar_width)
        ax.set_xticklabels(multiplexes)
        ax.legend()

    plt.tight_layout()  # Ensure subplots don't overlap
    return fig


def graph(df, multiplexes, figure_size):
    """4.	Produce a suitable graph that display the following information from the
three DAB multiplexes that you extracted earlier: C18A, C18F, C188:
Site, Freq, Block, Serv Label1, Serv Label2, Serv Label3, Serv label4, Serv Label10 
You may need to consider how you group this data to make visualisation feasible.
"""
    # Create single DAB Multiplex column to facilitate groupby
    df['DAB_Multiplex'] = ''
    # Group data by multiplex and get counts for each multiplex
    C18A_counts = df.groupby('C18A').size()
    C18F_counts = df.groupby('C18F').size()
    C188_counts = df.groupby('C188').size()

    # Plot the grouped bar chart
    fig, ax = plt.subplots()
    multiplex_counts.plot(kind='bar', ax=ax)
    ax.set_xlabel('Multiplex')
    ax.set_ylabel('Count')
    ax.set_title('DAB Multiplex Distribution')
    plt.xticks(rotation=0)  # Rotate x-axis labels if needed

    # Return the figure and axis objects
    return fig, ax


def corr_graph(df, multiplexes, figure_size):
    """5.	Determine if there is any significant correlation between the
Freq, Block, Serv Label1, Serv Label2, Serv Label3, Serv label4,Serv Label10 
used by the extracted DAB stations.  
You will need to select an appropriate visualisation to demonstrate this."""
    print('hold')
    
    #return fig


def handler(vis_input):
    # Get the data from MongoDB
    df = mongodb_interaction.retrieve_from_mongo()
    # Get standard figure size
    figure_size = (10, 5)
    df, multiplexes = format_dataframe(df, vis_input)
    # Determine the correct visualisation
    if vis_input['visualisation'] == "Summary Statistics":
        # Subset the dataframe, take only required columns
        df = df[[*multiplexes, 'Date', 'Site Height', 'Power(kW)']]
        visualisation = summary_stats(df, multiplexes, figure_size)
    elif vis_input['visualisation'] == "Bar Graphs":
        # Subset the dataframe, take only required columns
        df = df[[*multiplexes, *vis_input['columns']]]
        visualisation = graph(df, multiplexes, figure_size)
    elif vis_input['visualisation'] == "Correlation":
        # Do not accept Site as a variable for this graph
        if 'Site' in vis_input['columns']:
            vis_input['columns'].remove('Site')
        # Subset the dataframe, take only required columns
        df = df[[*multiplexes, *vis_input['columns']]]
        visualisation = corr_graph(df, multiplexes, figure_size)
    # Case where an unexpected visualisation has been requested
    else:
        return None
    return visualisation

