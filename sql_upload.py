import pandas as pd
from sqlalchemy import create_engine
import os


def handler():
    """Upload original datasets to MySQL"""
    # Read in raw data sets
    try:
        df1 = pd.read_csv(r'Summative/Data sets/TxAntennaDAB.csv', dtype='str')
    except UnicodeDecodeError:
        print('Decoding error when reading Antenna dataset')
    # Params contains an 'invalid continuation byte'
    # 0xe0 is an invalid continuation byte since it starts with the bit pattern 111 rather than 10
    try:
        df2 = pd.read_csv(r'Summative/Data sets/TxParamsDAB.csv', dtype='str', encoding='latin-1')
    except UnicodeDecodeError:
        print('Decoding error when reading Params dataset')
    # Clean column names by removing whitespace
    df1.columns = [col.strip() for col in df1.columns]
    df2.columns = [col.strip() for col in df2.columns]
    # MySQL database connection details
    db_username = 'root'
    db_password = 'Theashes2022'
    db_host = '127.0.0.1'
    db_name = 'radio_stations'
    schema_name = 'radio_stations'
    # Create a connection string with the specified schema
    connection_string = f'mysql+pymysql://{db_username}:{db_password}@{db_host}/{db_name}?charset=utf8mb4&local_infile=1'
    # Create an SQLAlchemy engine
    engine = create_engine(connection_string)
    # Name of the new table
    table_params = 'params'
    # Upload the DataFrame to the new table within the specified schema
    df2.to_sql(table_params, con=engine, schema=schema_name, if_exists='replace', index=False)
    # Name of the new table
    table_antennas = 'antennas'
    # Upload the DataFrame to the new table within the specified schema
    df1.to_sql(table_antennas, con=engine, schema=schema_name, if_exists='replace', index=False)


if __name__ == '__main__':
    handler()