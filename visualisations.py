import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


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
    df = pd.concat(df_list).reset_index(drop=True)
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


def get_mp_column(df, multiplexes):
    """Create one column to flag all DAB Multiplexes.
    Drop original DAB Multiplex columns"""
    df['DAB_Multiplex'] = ''
    for mp in multiplexes:
        df.loc[df[mp]==mp, 'DAB_Multiplex'] = mp
        # Drop the original DAB Multiplex flag
        df.drop(mp, axis=1, inplace=True)
    return df


def other_bar_graphs(df, multiplexes, figure_size):
    """Produce plot showing counts of requested variables'
    values for the requested DAB Multiplexes"""
    # Create single DAB Multiplex column to facilitate groupby
    df = get_mp_column(df.copy(), multiplexes)
    # Pivot "Service Labels" into binary columns
    df = pd.get_dummies(df, columns=['Serv Label1', 'Serv Label2',
                                           'Serv Label3', 'Serv Label4',
                                           'Serv Label10'], dtype=int,
                                            prefix='', prefix_sep='')

    # Create subplots with 2 rows and 2 columns
    fig, axes = plt.subplots(2, 2, figsize=figure_size)

    # Plot the counts of each service label grouped by Freq
    df.groupby('Freq').sum().iloc[:, 1:].plot(kind='bar', ax=axes[0, 0])
    axes[0, 0].set_title('Counts of Service Labels by Freq')
    axes[0, 0].set_ylabel('Count')

    # Plot the counts of each service level grouped by DAB_Multiplex
    df.groupby('DAB_Multiplex').sum().iloc[:, 1:].plot(kind='bar', ax=axes[0, 1])
    axes[0, 1].set_title('Counts of Service Labels by DAB_Multiplex')
    axes[0, 1].set_ylabel('Count')
    axes[0, 1].get_legend().remove()

    # Plot the number of unique sites grouped by DAB_Multiplex
    df.groupby('DAB_Multiplex')['Site'].nunique().plot(kind='bar', ax=axes[1, 0])
    axes[1, 0].set_title('Counts of Unique Sites by DAB_Multiplex')
    axes[1, 0].set_ylabel('Count')

    # Remove the fourth subplot
    fig.delaxes(axes[1, 1])

    # Get the legend labels which are used by both subplots
    handles, labels = axes[0, 0].get_legend_handles_labels()
    axes[0, 0].get_legend().remove()
    # Create a single legend in the bottom right
    fig.legend(handles=handles, labels=labels, title='Service Labels Key',
                ncol=2, bbox_to_anchor=(0.97, 0.42))

    plt.tight_layout()

    return fig


def corr_graph(df, multiplexes, figure_size):
    """Produce plot to determine if there is any significant correlation
    between the requested variables for the requested DAB Multiplexes"""
    # Create single DAB Multiplex column to facilitate groupby
    df = get_mp_column(df.copy(), multiplexes)
    # Function to calculate Cramér's V
    def cramers_v(x, y):
        confusion_matrix = pd.crosstab(x, y)
        chi2 = 0
        n = confusion_matrix.values.sum()
        rows, cols = confusion_matrix.shape

        for i in range(rows):
            for j in range(cols):
                expected = (confusion_matrix.iloc[i].sum() * confusion_matrix.iloc[:, j].sum()) / n
                chi2 += (confusion_matrix.iloc[i, j] - expected) ** 2 / expected

        cramers_v = np.sqrt(chi2 / (n * (min(rows, cols) - 1)))
        # Case where Cramer's V has detected no association
        if np.isnan(cramers_v):
            return 0.0
        return cramers_v

    # Calculate Cramér's V matrix for all pairs of columns
    cramer_matrix = pd.DataFrame(index=df.columns, columns=df.columns)

    for col1 in df.columns:
        for col2 in df.columns:
            # Case where cramers v would detect a perfect association
            if df[col1].nunique() == 1 and df[col2].nunique() == 1:
                cramer_matrix.loc[col1, col2] = 1.0
            else:
                cramer_matrix.loc[col1, col2] = cramers_v(df[col1], df[col2])

    # Create a heatmap of Cramér's V values
    plt.figure(figsize=figure_size)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.yticks(fontsize=8)
    plt.subplots_adjust(bottom=0.15)
    sns.heatmap(cramer_matrix.astype(float), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Cramér's V Heatmap")
    # Convert the heatmap to a figure
    fig = plt.gcf()
    return fig


def handler(df, vis_input):
    # Get standard figure size
    figure_size = (10, 5)
    df, multiplexes = format_dataframe(df, vis_input)
    # Do not attempt to generate visualisations where no data is present
    if df.empty:
        return None
    # Determine the correct visualisation
    if vis_input['visualisation'] == "Summary Statistics":
        # Subset the dataframe, take only required columns
        df = df[[*multiplexes, 'Date', 'Site Height', 'Power(kW)']]
        visualisation = summary_stats(df, multiplexes, figure_size)
    elif vis_input['visualisation'] == "Other Bar Graphs":
        # Subset the dataframe, take only required columns
        df = df[['Site', *multiplexes, 'Freq', 'Block', 'Serv Label1',
                 'Serv Label2', 'Serv Label3', 'Serv Label4','Serv Label10']]
        visualisation = other_bar_graphs(df, multiplexes, figure_size)
    elif vis_input['visualisation'] == "Correlation":
        # Subset the dataframe, take only required columns
        df = df[[*multiplexes, *vis_input['columns']]]
        visualisation = corr_graph(df, multiplexes, figure_size)
    # Case where an unexpected visualisation has been requested
    else:
        raise KeyError("Unexpected visualisaition requested")
    return visualisation

