import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def generate_summary_stats(df):
    """Calculate the mean, median, and mode of Power(kW)
    for the C18A, C18F, C188 DAB multiplexes"""
    # Type cast relevant columns to allow descriptive statistics calculations
    df['Site Height'] = df['Site Height'].astype(int)
    df['Power(kW)'] = df['Power(kW)'].str.replace(',', '').astype(float)

    for multiplex in df['EID'].unique():
        site_height_mask = (df['EID']==multiplex) & (df['Site Height'] > 75)
        date_mask = (df['EID']==multiplex) & (df['Date'].dt.year >= 2001)

        # Get mean, median, and mode where site height is greater than 75
        site_ht_power_mean = df.loc[site_height_mask]['Power(kW)'].mean()
        site_ht_power_median = df.loc[site_height_mask]['Power(kW)'].median()
        site_ht_power_mode = df.loc[site_height_mask]['Power(kW)'].mode()[0]

        # Get mean, median, and mode where the year is greater than or equal to 2001
        date_power_mean = df.loc[date_mask]['Power(kW)'].mean()
        date_power_median = df.loc[date_mask]['Power(kW)'].median()
        date_power_mode = df.loc[date_mask]['Power(kW)'].mode()[0]

        # Display the results
        print(f"Mean Power(kW) where site height is greater than 75: {site_ht_power_mean}")
        print(f"Median Power(kW) where site height is greater than 75: {site_ht_power_median}")
        print(f"Mode Power(kW) where site height is greater than 75: {site_ht_power_mode}")
        print(f"Mean Power(kW) where the year is greater than or equal to 2001: {date_power_mean}")
        print(f"Median Power(kW) where the year is greater than or equal to 2001: {date_power_median}")
        print(f"Mode Power(kW) where the year is greater than or equal to 2001: {date_power_mode}")
        print('hold')
    return df


def generate_graph(df):
    """4.	Produce a suitable graph that display the following information from the
three DAB multiplexes that you extracted earlier: C18A, C18F, C188:
Site, Freq, Block, Serv Label1, Serv Label2, Serv Label3, Serv label4, Serv Label10 
You may need to consider how you group this data to make visualisation feasible.
"""


def generate_corr_graph(df):
    """5.	Determine if there is any significant correlation between the
Freq, Block, Serv Label1, Serv Label2, Serv Label3, Serv label4,Serv Label10 
used by the extracted DAB stations.  
You will need to select an appropriate visualisation to demonstrate this."""



if __name__ == '__main__':
    df = generate_summary_stats(df)
    generate_graph(df)
    generate_corr_graph(df)