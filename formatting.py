import pandas as pd
import numpy as np


def custom_decode(file_path):
    """Resolve decoding error by encoding the dataset in utf-8"""
    # Get relevant path variables
    file_ext_index = file_path.rfind('.')
    file_name_index = file_path.rfind('/') + 1
    # Slice the file_path string to extract the file name
    file_name = file_path[file_name_index:file_ext_index]
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
        df_antenna = custom_decode(antenna_path)
    try:
        df_params = pd.read_csv(params_path, dtype='str')
    except UnicodeDecodeError as error:
        print(f'Decoding error when reading Params dataset:\n{error}')
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
            # Allow ISO 8601 date and time format
            df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S')
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
        df[col] = df[col].str.replace(r'\s+', ' ', regex=True).str.strip()
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
    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        entry = {
            '_id': row['id'],
            'Date': row['Date'],
            'C18A': row['C18A'],
            'C18F': row['C18F'],
            'C188': row['C188'],
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
        # Replace empty strings with None in the dictionary
        entry = {key: value if value not in ['', np.nan]
                  else None for key, value in entry.items()}
        data.append(entry)
    return data


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
    return upload_data

