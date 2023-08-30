import os
import pandas as pd
import numpy as np
import csv
import json
import unicodedata
import pymongo



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

def wrangle_dab_multiplex(df):
    """Extract DAB multiplexes C18A, C18F and C188 into their own columns.
    Then join each of these categories to the NGR that signifies the DAB
    stations location to the following: Site, Site Height, In-Use Ae Ht, In-Use ERP Total"""
    # # Instantiate list of columns to join values
    # cols_to_join = ['EID', 'NGR', 'Site', 'Site Height', 'In-Use Ae Ht', 'In-Use ERP Total']
    # # df[f'DAB_multiplex'] = np.where(df['EID'].isin(dab_multiplexes), df['EID'], '')
    # for multiplex in dab_multiplexes:
    #     # Create a new column for each DAB multiplex
    #     df[f'DAB_{multiplex}'] = np.where(
    #         df['EID'] == multiplex,
    #         df[cols_to_join].apply(lambda row: ' | '.join(row.astype(str).str.strip()), axis=1),
    #         ''
    #     )
    # df = df.rename({'In-Use Ae Ht': 'Aerial height(m)',
    #                  'In-Use ERP Total': 'Power(kW)'}, axis=1)
    # return df
    # Instantiate tuple of required DAB multiplexes
    dab_multiplexes = ('C18A', 'C18F', 'C188')
    # Create a binary column indicating the presence of each multiplex
    for multiplex in dab_multiplexes:
        df[multiplex] = df["EID"].apply(lambda x: int(x == multiplex))
    print('hold')
    # Only need NGR, Site Height, In-Use Ae Ht, In-Use ERP Total from antenna data set
    # # Instantiate list of columns to keep
    # columns_to_keep = ['NGR', 'Site', 'Site Height', 'In-Use Ae Ht', 'In-Use ERP Total']
    # # Filter the DataFrame to only include relevant columns and rows
    # df_filtered = df[df['EID'].isin(dab_multiplexes)][columns_to_keep + ['EID']]
    # # Pivot the DataFrame
    # df_pivot = df_filtered.pivot(index='NGR', columns='EID', values=columns_to_keep)
    # # Rename columns
    # df_pivot.columns = [f'{col[1]}_{col[0]}' for col in df_pivot.columns]
    # # Reset index and drop NGR column
    # df_pivot.reset_index(drop=True, inplace=True)
    return df

def clean_data(df):
    """Standardise values and remove anomalies"""
    # Strip extra whitespace from column names
    df.columns = [col.strip() for col in df.columns]
    # Remove '- DAB' from the end of Site values
    df['Site'] = df['Site'].str.replace('- DAB', '')
    # Remove commas from Power column
    df['In-Use ERP Total'] = df['In-Use ERP Total'].str.replace(',', '')
    for col in df.columns:
        # Remove extra whitespace from values
        df[col] = df[col].str.replace(r'\s+', ' ').str.strip()
        # Convert all values to upper case
        df[col] = df[col].str.upper()
        # Format date column to get date without time
    # Parse dates
    try:
        # Try the expected British format
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    except ValueError:
        try:
            # Allow dashes
            df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
        except ValueError as e:
            print(f'Unsupported date format: {e}')
    return df

def format_json(df):
    """Convert data into a dictionary ready to accurately
    upload to the radio_data MongoDB database"""
    upload_dict = {}
    for dab_multiplex in ('C18A', 'C18F', 'C188'):
        df_multiplex = df[[col for col in df.columns if col.startswith(dab_multiplex)]]
        df_multiplex = df_multiplex.dropna(how='all')
        print('hold')        
    return upload_dict

def upload_to_mongo(df, client, formatted=False):
    """Upload the formatted data to MongoDB for later retrieval"""
    if formatted:
        # data has been read in by
        df = pd.read_json()
    else:
        upload_dict = format_json(df)
    # Create a database
    db = client["radio_data"]
    #TODO STORE ONLY REQUIRED RECORDS REQUIRED FOR VISUALISATIONS IN MONGODB for processing speed

    # Create collections to store the formatted data
    collection_clean = db["clean_merged_data"]
    collection_required = db["visualisation_input"]

def retrieve_from_mongo(client):
    """Retrieve the cleaned and formatted data from MongoDB.
    This will be the input data for data visualisations"""
    # df = 
    # return df

def generate_summary_stats(df):
    """Calculate the mean, median, and mode of Power(kW)
    for the C18A, C18F, C188 DAB multiplexes"""
    # Type cast relevant columns to allow descriptive statistics calculations
    df['Site Height'] = df['Site Height'].astype('int')
    df['Power(kW)'] = df['Power(kW)'].str.replace(',', '').astype('float')

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



def handler(antenna_path, params_path):
    """Main function oversees the data formatting process"""
    # Read in raw data sets, assume UTF-8 encoding
    antenna_cols =['id', 'NGR', 'Site Height',
                   'In-Use Ae Ht', 'In-Use ERP Total']
    try:
        df_antenna = pd.read_csv(antenna_path, usecols=antenna_cols,
                                 dtype='str')
    except UnicodeDecodeError:
        print(f'Decoding error when reading Antenna dataset:\n{error}')
        df_antenna = pd.read_csv(antenna_path, usecols=antenna_cols,
                                 dtype='str', encoding='latin-1')
        # df_antenna = custom_decode(antenna_path)
    # Params contains an 'invalid continuation byte'
    # 0xe0 is an invalid continuation byte since it starts with the bit pattern 111 rather than 10
    try:
        df_params = pd.read_csv(params_path, dtype='str')
    except UnicodeDecodeError as error:
        print(f'Decoding error when reading Params dataset:\n{error}')
        # df_params = pd.read_csv(params_path, dtype='str', encoding='latin-1')
        df_params = custom_decode(params_path)

    # Merge the antennas and params dataframes on id
    df = df_antenna.merge(df_params, how='left', on='id', validate='1:1')

    # Only now that data has been merged, check for duplicates
    # Duplicates have undesirable impacts on visualisations
    df = df.drop_duplicates()

    # Standardise values and general cleaning
    df = clean_data(df)

    # Remove records with NGR: 'NZ02553847', 'SE213515', 'NT05399374', 'NT25265908'
    df = remove_invalid_stations(df)

    df = wrangle_dab_multiplex(df)

    # Establish a connection to the MongoDB server
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    upload_to_mongo(df, client)
    # df = retrieve_from_mongo(client)

    df = generate_summary_stats(df)
    print('hold')
    generate_graph(df)

    generate_corr_graph(df)



if __name__ == '__main__':
    antenna_path = r'C:\Users\jbrou\Advanced Programming\OL6 AP 2223 Data sets\Data sets/TxAntennaDAB.csv'
    params_path = r'C:\Users\jbrou\Advanced Programming\OL6 AP 2223 Data sets\Data sets/TxParamsDAB.csv'
    handler(antenna_path, params_path)