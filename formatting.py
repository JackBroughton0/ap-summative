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


def get_raw_data(antenna_path, params_path):
    """Get the raw data"""
    # Instantiate list of required columns from antenna data
    antenna_cols = ['id', 'NGR', 'Site Height',
                    'In-Use Ae Ht', 'In-Use ERP Total']
    # Read in raw data sets, assume UTF-8 encoding
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
    return df


def format_dates(df):
    """Format the date column by parsing to datetime"""
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


def type_cast(df):
    """Cast the data types of the columns required
    for output to generate visualisations"""
    # Parse dates
    df = format_dates(df)
    # Convert to integer columns
    df['id'] = df['id'].astype(int)
    df['Site Height'] = df['Site Height'].astype(int)
    df['In-Use Ae Ht'] = df['In-Use Ae Ht'].astype(int)
    # Convert to float columns
    df['In-Use ERP Total'] = df['In-Use ERP Total'].astype(float)
    df['Freq'] = df['Freq'].astype(float)
    return df


def clean_data(df):
    """Standardise values and remove anomalies"""
    # Duplicates have undesirable impacts on visualisations
    df = df.drop_duplicates()
    # Strip extra whitespace from column names
    df.columns = [col.strip() for col in df.columns]
    df = df.rename({'Freq.': 'Freq'}, axis=1)
    # Remove commas from Power values
    df['In-Use ERP Total'] = df['In-Use ERP Total'].str.replace(',', '')
    for col in df.columns:
        # Remove extra whitespace from values
        df[col] = df[col].str.replace(r'\s+', ' ').str.strip()
        # Convert all values to upper case
        df[col] = df[col].str.upper()
    # Remove spaces from NGR values
    df['NGR'] = df['NGR'].str.replace(' ', '')
    # Cast the data types of the required columns
    df = type_cast(df)
    return df


def remove_invalid_stations(df):
    """Remove DAB Radio stations that have invalid NGR"""
    # Specify invalid NGRs to drop records
    invalid_ngr = ('NZ02553847', 'SE213515', 'NT05399374', 'NT25265908')
    df_filtered = df[~df['NGR'].isin(invalid_ngr)].reset_index()
    return df_filtered


def wrangle_dab_multiplex(df):
    """Extract DAB multiplex blocks C18A, C18F and C188 into
      their own columns and drop records that don't have
      these EID values"""
    # Instantiate list of required DAB multiplexes
    dab_multiplexes = ['C18A', 'C18F', 'C188']
    # Create a column indicating the presence of each multiplex
    for multiplex in dab_multiplexes:
        df[multiplex] = df["EID"].apply(lambda x: multiplex if x == multiplex else '')
    # Remove records not in the list of EIDs required for output
    df_out = df[df[dab_multiplexes].any(axis=1)]
    return df_out


def get_output_columns(df):
    """Remove columns that are not required for output"""
    # Rename columns according to client brief
    df = df.rename({'In-Use Ae Ht': 'Aerial height(m)',
                    'In-Use ERP Total': 'Power(kW)'}, axis=1)
    # Instantiate list of columns required for output
    keep_cols = ['id', 'NGR', 'C18A', 'C18F', 'C188', 'Site', 'Site Height',
                 'Aerial height(m)', 'Power(kW)', 'Date', 'Freq',
                 'Block', 'Serv Label1', 'Serv Label2', 'Serv Label3',
                 'Serv Label4', 'Serv Label10']
    # Get subset of dataframe with required columns
    df_out = df[keep_cols]
    return df_out


def format_json(df):
    """Convert data into a dictionary ready to accurately
    upload to the radio_data MongoDB database"""
    # Create a list to store the data
    data = []
    dab_multiplexes = ['C18A', 'C18F', 'C188']
    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        entry = {
            '_id': row['id'],
            'Date': row['Date'],
            'DAB_Multiplex': None,
            'Site Info': {'NGR': row['NGR'],
                          'Site': row['Site'],
                          'Site Height': row['Site Height']},
            'Aerial height(m)': row['Aerial height(m)'],
            'Power(kW)': row['Power(kW)'],
            'Freq': row['Freq'],
            'Block': row['Block'],
            'Service Labels': {'Serv Label1': row['Serv Label1'],
                                'Serv Label2': row['Serv Label2'],
                                'Serv Label3': row['Serv Label3'],
                                'Serv Label4': row['Serv Label4'],
                                'Serv Label10': row['Serv Label10']}
        }
        # Determine the DAB multiplex and update the entry
        for multiplex in dab_multiplexes:
            if row[multiplex]:
                entry['DAB_Multiplex'] = multiplex
                break
        data.append(entry)
    return data


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


def handler(antenna_path, params_path):
    """Main function oversees the data formatting process"""
    # Read in raw csvs and merge data sets on id
    df = get_raw_data(antenna_path, params_path)
    # Standardise values and general cleaning
    df = clean_data(df)
    # Remove records with NGR: 'NZ02553847', 'SE213515', 'NT05399374', 'NT25265908'
    df = remove_invalid_stations(df)
    # Extract records with DAB multiplexes: 'C18A', 'C18F' and 'C188'
    df = wrangle_dab_multiplex(df)
    # Get subset of dataframe with required columns
    df_out = get_output_columns(df)
    # Convert the dataframe to json
    upload_data = format_json(df_out)
    df = generate_summary_stats(df)
    generate_graph(df)
    generate_corr_graph(df)


if __name__ == '__main__':
    antenna_path = r'C:\Users\jbrou\Advanced Programming\OL6 AP 2223 Data sets\Data sets/TxAntennaDAB.csv'
    params_path = r'C:\Users\jbrou\Advanced Programming\OL6 AP 2223 Data sets\Data sets/TxParamsDAB.csv'
    handler(antenna_path, params_path)