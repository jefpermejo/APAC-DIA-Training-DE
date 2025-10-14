# Ingest raw files into Bronze (Parquet + Delta), with schema validation, partitioning,
# rejects, and manifest tracking in DuckDB.
# Usage: python scripts/load_to_bronze.py --raw data_raw --lake lake --manifest duckdb/warehouse.duckdb
import argparse, pathlib, os, hashlib, json, datetime as dt
import duckdb
import pyarrow as pa
import pyarrow.csv as pacsv
import pyarrow.dataset as pads
import pyarrow.parquet as pq
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from schemas import *
from deltalake import write_deltalake
import pandas as pd
import pyarrow.json as pajson

# Define paths
DUCKDB_PATH = "duckdb/warehouse.duckdb"
PARQUET_PATH = "lake/bronze/parquet"
DELTA_PATH = "lake/bronze/delta"
REJECTS_PATH = "lake/_rejects"

# Define all tables to ingest
tables = [
    {"name": "customers", "filename": "customers.csv", "format": "csv", "schema": customers_schema, "write_delta": True, "partitioned": False},
    {"name": "products", "filename": "products.csv", "format": "csv", "schema": products_schema, "write_delta": True, "partitioned": False},
    {"name": "stores", "filename": "stores.csv", "format": "csv", "schema": stores_schema, "write_delta": True, "partitioned": False},
    {"name": "suppliers", "filename": "suppliers.csv", "format": "csv", "schema": suppliers_schema, "write_delta": True, "partitioned": False},
    {"name": "orders_header", "filename": "orders", "format": "csv", "schema": orders_header_schema, "write_delta": True, "partitioned": True, "file_pattern": "part-*.csv"},
    {"name": "orders_lines", "filename": "orders", "format": "csv", "schema": orders_lines_schema, "write_delta": True, "partitioned": True, "file_pattern": "order_lines.csv"},
    {"name": "sensors", "filename": "sensors", "format": "csv", "schema": sensors_schema, "write_delta": True, "partitioned": True, "file_pattern": "sensors.csv"},
    {"name": "exchange_rates", "filename": "exchange_rates.xlsx", "format": "xlsx", "schema": exchange_rates_schema, "write_delta": True, "partitioned": False},
    {"name": "shipments", "filename": "shipments.parquet", "schema": shipments_schema, "format": "parquet", "write_delta": True, "partitioned": False, "file_pattern": "*.parquet"},
    {"name": "events", "filename": "events", "format": "json", "schema": events_schema, "write_delta": True, "partitioned": True, "file_pattern": "*.jsonl"}
    ]

# Parse arguments
def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw', type=str, default='data_raw/samples')
    ap.add_argument('--lake', type=str, default='lake')
    ap.add_argument('--manifest', type=str, default=DUCKDB_PATH)
    return ap.parse_args()

#Ensure directories exist
def ensure_dirs(lake_root):
    for sub in ['bronze/parquet','bronze/delta']:
        (lake_root/sub).mkdir(parents=True, exist_ok=True)
    (lake_root/'_rejects').mkdir(parents=True, exist_ok=True)

#Initialize manifest
def init_manifest(conn):
    # Create table only if it doesn't exist (preserves existing data)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS manifest_processed_files (
            src_path TEXT PRIMARY KEY,
            processed_at TIMESTAMP,
            row_count BIGINT,
            reject_count BIGINT,
            status TEXT
        )
    ''')

#Initialize bronze schema
def init_bronze(conn): 
    # Check if bronze schema already exists
    existing_schemas = conn.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'bronze'").fetchall()
    
    if existing_schemas:
        print("Bronze schema already exists")
    else:
        conn.execute("CREATE SCHEMA bronze")
        print("Created bronze schema")

# Check if file already processed
def already_processed(conn, p): return conn.execute("SELECT 1 FROM manifest_processed_files WHERE src_path = ?", [str(p)]).fetchone() is not None

# Mark file as processed
def mark_processed(conn, src_path, row_count, reject_count=0, status='success'):
    """Mark file as processed in manifest with full tracking"""
    conn.execute(
        "INSERT OR REPLACE INTO manifest_processed_files VALUES (?, ?, ?, ?, ?)", 
        [str(src_path), dt.datetime.utcnow(), row_count, reject_count, status]
    )

# Read table by format
def read_table_by_format(file_path, format):
    if format == "csv":
        return pacsv.read_csv(file_path, read_options=pacsv.ReadOptions(encoding='utf-8'))
    elif format == "xlsx":
        df = pd.read_excel(file_path)
        return pa.Table.from_pandas(df)
    elif format == "parquet":
        return pq.read_table(file_path)
    elif format == "json":
        return pajson.read_json(file_path)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
# Write to Delta Lake with partitioning
def write_delta_partitioned(table, base_path, partitioning=None, table_name=None):

    base_path.mkdir(parents=True, exist_ok=True)
    print(f"[DEBUG] Attempting to write to Delta Lake: path={base_path}, rows={len(table)}, partition_by={partitioning}")
    try:
        write_deltalake(str(base_path), table, partition_by=partitioning, mode='append')
        print(f"[DEBUG] Written {len(table)} rows to Delta Lake at: {base_path}")
    except Exception as e:
        print(f"[ERROR] Failed to write to Delta Lake: {e}")

# Write to Parquet with partitioning
def write_parquet_partitioned(table, base_path, partitioning=None, table_name=None):
    """Write table to parquet with custom filename"""
    base_path.mkdir(parents=True, exist_ok=True)
    
    if table_name:
        # Use custom table name for filename
        file_path = base_path / f"{table_name}.parquet"
        pq.write_table(table, str(file_path))
    else:
        # Fall back to dataset writing (creates part-0.parquet)
        pads.write_dataset(table, base_dir=str(base_path), format='parquet', 
                          partitioning=partitioning, existing_data_behavior='overwrite_or_ignore')

#Write to DuckDB
def write_to_duckdb(table, conn, table_name):
    """Write PyArrow table to DuckDB bronze schema"""
    try:
        # Register the PyArrow table and create DuckDB table from it
        conn.register('temp_table', table)
        conn.execute(f"CREATE OR REPLACE TABLE bronze.{table_name} AS SELECT * FROM temp_table")
        conn.unregister('temp_table')
        print(f"Written {len(table)} rows to DuckDB table: bronze.{table_name}")
        
    except Exception as e:
        print(f"Failed to write to DuckDB: {e}")
        raise


# Ingest for any csv table with schema validation, audit columns, rejects, and manifest tracking
def load_table(raw_root, lake_root, conn, table_def):
    # Support partitioned tables (CSV files in subfolders)
    format = table_def.get('format', 'csv')
    if table_def.get('partitioned', False):
        # Find all files recursively under the partitioned folder, filtered by pattern
        src_dir = raw_root / table_def['filename']
        pattern = table_def.get('file_pattern', '*.csv')
        files = list(src_dir.rglob(pattern))
        if not files:
            print(f"[INFO] No files matching {pattern} found in {src_dir}, skipping.")
            return
        # Read and concatenate all files
        tables = [read_table_by_format(f, format) for f in files]
        table = pa.concat_tables(tables)
        src_display = f"{src_dir} ({len(files)} files, pattern: {pattern})"
    else:
        src = raw_root / table_def['filename']
        if not src.exists():
            print(f"[INFO] {src} does not exist, skipping.")
            return
        if already_processed(conn, src):
            print(f"[INFO] {src} already processed, skipping.")
            return
        table = read_table_by_format(src, format)
        src_display = str(src)

    print(f"{table_def['name'].capitalize()} - Original rows: {len(table)}")
    print(f"Inferred schema: {table.schema}")

    # Schema validation with reject handling
    try:
        # Cast to the expected schema
        validated_table = table.cast(table_def['schema'], safe=False)
        print(f"{table_def['name'].capitalize()}: Schema validation PASSED")

        # Add audit columns to validated data
        now = pa.scalar(dt.datetime.utcnow(), type=pa.timestamp('us'))
        # For partitioned, using a generic src_filename for now
        if table_def.get('partitioned', False):
            src_filename = table_def['filename']
        else:
            src_filename = src.name

        # Generate src_row_hash
        row_numbers = list(range(len(validated_table)))
        row_hashes = [f"{src_filename}_{i}" for i in row_numbers]

        # Add all audit columns
        validated_table = validated_table.append_column('ingestion_ts', pa.array([now.as_py()]*len(validated_table), type=pa.timestamp('us')))
        validated_table = validated_table.append_column('src_filename', pa.array([src_filename]*len(validated_table), type=pa.string()))
        validated_table = validated_table.append_column('src_row_hash', pa.array(row_hashes, type=pa.string()))

        # Write validated data to bronze layer destinations - Parquet
        pq_base = lake_root/'bronze'/'parquet'/table_def['name']
        write_parquet_partitioned(validated_table, pq_base, partitioning=None, table_name=table_def['name'])

        # Write validated data to bronze layer destinations - Delta
        if table_def.get('write_delta', True):
            delta_base = lake_root/'bronze'/'delta'/table_def['name']
            write_delta_partitioned(validated_table, delta_base, partitioning=None, table_name=table_def['name'])

        # Also write to DuckDB
        write_to_duckdb(validated_table, conn, table_def['name'])

        print(f"Loaded {len(validated_table)} valid rows to bronze layer (Parquet + DuckDB)")
        # For partitioned, mark the directory as processed; for non-partitioned, mark the file
        if table_def.get('partitioned', False):
            mark_processed(conn, src_display, len(validated_table), 0, 'success')
        else:
            mark_processed(conn, src, len(validated_table), 0, 'success')

    except Exception as e:
        # Handle validation errors - write to rejects with reason
        print(f"{table_def['name'].capitalize()}: Schema validation FAILED - {e}")

        # Create rejects directory
        rejects_path = lake_root / '_rejects'
        rejects_path.mkdir(parents=True, exist_ok=True)

        # Add rejection reason and timestamp
        rejection_reason = f"Schema validation failed: {str(e)}"
        reject_table = table.append_column('rejection_reason', pa.array([rejection_reason] * len(table)))
        reject_table = reject_table.append_column('rejected_at', pa.array([dt.datetime.utcnow()] * len(table)))

        # Write rejected data
        reject_file = rejects_path / f"{table_def['name']}_schema_reject_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
        pq.write_table(reject_table, str(reject_file))
        print(f"Rejected data written to: {reject_file}")

        # Mark as processed with all rows rejected
        mark_processed(conn, src, 0, len(table), 'all_rejected')

# Main function
def main():
    args = parse_args()
    raw_root = pathlib.Path(args.raw)
    lake_root = pathlib.Path(args.lake)
    ensure_dirs(lake_root)
    pathlib.Path(args.manifest).parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(args.manifest)
    conn.execute("INSTALL delta; LOAD delta;")
    init_manifest(conn)
    init_bronze(conn)

    print("Processing bronze layer tables:")
    for table_def in tables:
        load_table(raw_root, lake_root, conn, table_def)

    print("Bronze load completed for all tables.")

if __name__ == '__main__':
    main()
