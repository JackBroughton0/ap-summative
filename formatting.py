import os
import pandas as pd
import numpy as np
import csv
import json
import unicodedata



def custom_decode(file_path):
    """Resolve decoding error by encoding the dataset in utf-8"""
    # Get relevant path variables
    file_ext_index = file_path.rfind('.')
    file_name_index = file_path.rfind('/') + 1
    # Slice the file_path string to extract the file name
    file_name = file_path[file_name_index:file_ext_index]
    # with open(file_path, 'rb') as file:
    #     original_data = file.readlines()
    #     for line in original_data:
    #         print(original_data.index(line))
    #         try:
    #             data = line.decode("utf-8")
    #         except UnicodeDecodeError as e:
    #             # Show positions of errors in relation to text
    #             data = line[:e.start] + line[e.end:]
    #             print(data)
    try:
        # First assume the csv is utf-8 encoded
        df = pd.read_csv(file_path, dtype='str')
    except UnicodeDecodeError:
        try:
            # If not utf-8, assume ISO-8859-1 encoding
            df = pd.read_csv(file_path, dtype='str', encoding='latin-1')
        except Exception as e:
            print(f"Unable to parse {file_name} dataset: {e}")
            raise pd.errors.ParserError("Failed to parse the dataset")
    except Exception as e:
        print(f"An error occurred while reading {file_name}: {e}")
        raise pd.errors.ParserError("Failed to read the dataset")
    return df

def remove_invalid_stations(df):
    """Remove DAB Radio stations that have invalid NGR"""
    # Specify invalid NGRs to drop records
    invalid_ngr = ('NZ02553847', 'SE213515', 'NT05399374', 'NT25265908')
    df_filtered = df[~df['NGR'].isin(invalid_ngr)].reset_index()
    return df_filtered

def wrangle_dab_multiplex(df, dab_multiplexes):
    """Extract DAB multiplexes C18A, C18F and C188 into their own columns.
    Then join each of these categories to the NGR that signifies the DAB
    stations location to the following: Site, Site Height, In-Use Ae Ht, In-Use ERP Total"""
    # Instantiate list of columns to join values
    cols_to_join = ['EID', 'NGR', 'Site', 'Site Height', 'In-Use Ae Ht', 'In-Use ERP Total']
    # df[f'DAB_multiplex'] = np.where(df['EID'].isin(dab_multiplexes), df['EID'], '')
    for multiplex in dab_multiplexes:
        # Create a new column for each DAB multiplex
        df[f'DAB_{multiplex}'] = np.where(
            df['EID'] == multiplex,
            df[cols_to_join].apply(lambda row: ' | '.join(row.astype(str).str.strip()), axis=1),
            ''
        )
    df = df.rename({'In-Use Ae Ht': 'Aerial height(m)',
                     'In-Use ERP Total': 'Power(kW)'}, axis=1)
    return df

def generate_summary_stats(df, dab_multiplexes):
    """Calculate the mean, median, and mode of Power(kW)
    for the C18A, C18F, C188 DAB multiplexes"""
    # Type cast relevant columns to allow descriptive statistics calculations
    df['Site Height'] = df['Site Height'].astype('int')
    df['Power(kW)'] = df['Power(kW)'].str.replace(',', '').astype('float')

    for multiplex in dab_multiplexes:
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

def generate_graph(df, dab_multiplexes):
    """4.	Produce a suitable graph that display the following information from the
three DAB multiplexes that you extracted earlier: C18A, C18F, C188:
Site, Freq, Block, Serv Label1, Serv Label2, Serv Label3, Serv label4, Serv Label10 
You may need to consider how you group this data to make visualisation feasible.
"""

def generate_corr_graph(df, dab_multiplexes):
    """5.	Determine if there is any significant correlation between the
Freq, Block, Serv Label1, Serv Label2, Serv Label3, Serv label4,Serv Label10 
used by the extracted DAB stations.  
You will need to select an appropriate visualisation to demonstrate this."""



def handler(antenna_path, params_path):
    """Main function oversees the data formatting process"""
    #TODO set up git repo to track changes
    # Read in raw data sets, assume UTF-8 encoding
    try:
        df_antenna = pd.read_csv(antenna_path, dtype='str')
    except UnicodeDecodeError:
        print(f'Decoding error when reading Antenna dataset:\n{error}')
        df_antenna = pd.read_csv(antenna_path, dtype='str', encoding='latin-1')
        # df_antenna = custom_decode(antenna_path)
    # Params contains an 'invalid continuation byte'
    # 0xe0 is an invalid continuation byte since it starts with the bit pattern 111 rather than 10
    try:
        df_params = pd.read_csv(params_path, dtype='str')
    except UnicodeDecodeError as error:
        print(f'Decoding error when reading Params dataset:\n{error}')
        # df_params = pd.read_csv(params_path, dtype='str', encoding='latin-1')
        df_params = custom_decode(params_path)
    df_antenna.columns = [col.strip() for col in df_antenna.columns]
    df_params.columns = [col.strip() for col in df_params.columns]

    # Merge the antennas and params dataframes on id
    df = df_antenna.merge(df_params, how='left', on='id', validate='1:1')

    # Only now that data has been merged, check for duplicates
    # Duplicates have undesirable impacts on visualisations
    df = df.drop_duplicates()

    # Format date column to get date without time
    #TODO try except this
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

    # Remove records with NGR: 'NZ02553847', 'SE213515', 'NT05399374', 'NT25265908'
    df = remove_invalid_stations(df)

    # Instantiate tuple of required DAB multiplexes
    dab_multiplexes = ('C18A', 'C18F', 'C188')
    df = wrangle_dab_multiplex(df, dab_multiplexes)

    df = generate_summary_stats(df, dab_multiplexes)
    print('hold')
    generate_graph(df, dab_multiplexes)

    generate_corr_graph(df, dab_multiplexes)



if __name__ == '__main__':
    antenna_path = r'Summative/Data sets/TxAntennaDAB.csv'
    params_path = r'Summative/Data sets/TxParamsDAB.csv'
    handler(antenna_path, params_path)