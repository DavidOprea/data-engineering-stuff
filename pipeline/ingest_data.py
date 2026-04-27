#!/usr/bin/env python
# coding: utf-8

import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', type=int, default=5432, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--year', type=int, default=2021, help='Year of data to ingest')
@click.option('--month', type=int, default=1, help='Month of data to ingest')
@click.option('--chunksize', type=int, default=100000, help='Chunk size for reading CSV')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')
@click.option('--url', default='https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet', help='URL of the Parquet file to ingest')
@click.option('--file_type', default='parquet', help='Type of the file to ingest (csv or parquet)')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, chunksize, target_table, url, file_type):

    engine = create_engine(f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    if file_type == 'parquet':
        df= pd.read_parquet(
            url
        )

        df.to_sql(name=target_table, con=engine, if_exists='replace')
    elif file_type == 'csv':
        df_iter = pd.read_csv(
            url,
            iterator=True,
            chunksize=chunksize
        )

        first = True
        for df_chunk in tqdm(df_iter):
            if first:
                df_chunk.head(0).to_sql(
                    name=target_table,
                    con=engine,
                    if_exists='replace'
                )
                first = False
            df_chunk.to_sql(name=target_table, con=engine, if_exists='append')

if __name__ == '__main__':
    run()