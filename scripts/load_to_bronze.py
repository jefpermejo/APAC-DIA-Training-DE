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

# Define paths
DUCKDB_PATH = "duckdb/warehouse.duckdb"
PARQUET_PATH = "lake/bronze/parquet"
DELTA_PATH = "lake/bronze/delta"
REJECTS_PATH = "lake/_rejects"


try:
    from deltalake import write_deltalake
except Exception as e:
    write_deltalake = None

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw', type=str, default='data_raw/samples')
    ap.add_argument('--lake', type=str, default='lake')
    ap.add_argument('--manifest', type=str, default=DUCKDB_PATH)
    return ap.parse_args()

def ensure_dirs(lake_root):
    for sub in ['bronze/parquet','bronze/delta']:
        (lake_root/sub).mkdir(parents=True, exist_ok=True)
    (lake_root/'_rejects').mkdir(parents=True, exist_ok=True)

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
def init_bronze(conn): 
    # Check if bronze schema already exists
    existing_schemas = conn.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'bronze'").fetchall()
    
    if existing_schemas:
        print("Bronze schema already exists")
    else:
        conn.execute("CREATE SCHEMA bronze")
        print("Created bronze schema")

def already_processed(conn, p): return conn.execute("SELECT 1 FROM manifest_processed_files WHERE src_path = ?", [str(p)]).fetchone() is not None

def mark_processed(conn, src_path, row_count, reject_count=0, status='success'):
    """Mark file as processed in manifest with full tracking"""
    conn.execute(
        "INSERT OR REPLACE INTO manifest_processed_files VALUES (?, ?, ?, ?, ?)", 
        [str(src_path), dt.datetime.utcnow(), row_count, reject_count, status]
    )

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

def load_customers(raw_root, lake_root, conn):
    src = raw_root/'customers.csv'
    if not src.exists(): return
    if already_processed(conn, src): return
    
    # Read CSV
    table = pacsv.read_csv(src, read_options=pacsv.ReadOptions(encoding='utf-8'))
    
    print(f"Customers - Original rows: {len(table)}")
    print(f"Inferred schema: {table.schema}")
    
    # Schema validation with reject handling
    try:
        # Cast to the expected schema
        validated_table = table.cast(customers_schema, safe=False)
        print("Customers: Schema validation PASSED")
        
        # Add audit columns to validated data
        now = pa.scalar(dt.datetime.utcnow(), type=pa.timestamp('us'))
        src_filename = src.name  # Extract filename from path

        # Generate src_row_hash
        row_numbers = list(range(len(validated_table)))
        row_hashes = [f"{src_filename}_{i}" for i in row_numbers]
        
        # Add all audit columns
        validated_table = validated_table.append_column('ingestion_ts', pa.array([now.as_py()]*len(validated_table), type=pa.timestamp('us')))
        validated_table = validated_table.append_column('src_filename', pa.array([src_filename]*len(validated_table), type=pa.string()))
        validated_table = validated_table.append_column('src_row_hash', pa.array(row_hashes, type=pa.string()))
        
        # Write validated data to bronze layer destinations
        pq_base = lake_root/'bronze'/'parquet'/'customers'
        write_parquet_partitioned(validated_table, pq_base, partitioning=None, table_name='customers')
        
        # Also write to DuckDB
        write_to_duckdb(validated_table, conn, 'customers')
        
        print(f"Loaded {len(validated_table)} valid rows to bronze layer (Parquet + DuckDB)")
        mark_processed(conn, src, len(validated_table), 0, 'success')
        
    except Exception as e:
        # Handle validation errors - write to rejects with reason
        print(f"Products: Schema validation FAILED - {e}")
        
        # Create rejects directory
        rejects_path = lake_root / '_rejects'
        rejects_path.mkdir(parents=True, exist_ok=True)
        
        # Add rejection reason and timestamp
        rejection_reason = f"Schema validation failed: {str(e)}"
        reject_table = table.append_column('rejection_reason', pa.array([rejection_reason] * len(table)))
        reject_table = reject_table.append_column('rejected_at', pa.array([dt.datetime.utcnow()] * len(table)))
        
        # Write rejected data
        reject_file = rejects_path / f"customers_schema_reject_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
        pq.write_table(reject_table, str(reject_file))
        print(f"Rejected data written to: {reject_file}")
        
        # Mark as processed with all rows rejected
        mark_processed(conn, src, 0, len(table), 'all_rejected')

def load_products(raw_root, lake_root, conn):
    src = raw_root/'products.csv'
    if not src.exists(): return
    if already_processed(conn, src): return
    
    # Read CSV and let PyArrow infer types initially
    table = pacsv.read_csv(src, read_options=pacsv.ReadOptions(encoding='utf-8'))
    
    print(f"Products - Original rows: {len(table)}")
    print(f"Inferred schema: {table.schema}")
    
    # Schema validation with reject handling
    try:
        # Cast to the expected schema
        validated_table = table.cast(products_schema, safe=False)
        print("Products: Schema validation PASSED")
        
        # Add audit columns to validated data
        now = pa.scalar(dt.datetime.utcnow(), type=pa.timestamp('us'))
        src_filename = src.name  # Extract filename from path
        
        # Generate src_row_hash
        row_numbers = list(range(len(validated_table)))
        row_hashes = [f"{src_filename}_{i}" for i in row_numbers]
        
        # Add all audit columns
        validated_table = validated_table.append_column('ingestion_ts', pa.array([now.as_py()]*len(validated_table), type=pa.timestamp('us')))
        validated_table = validated_table.append_column('src_filename', pa.array([src_filename]*len(validated_table), type=pa.string()))
        validated_table = validated_table.append_column('src_row_hash', pa.array(row_hashes, type=pa.string()))
        
        # Write validated data to bronze layer destinations
        pq_base = lake_root/'bronze'/'parquet'/'products'
        write_parquet_partitioned(validated_table, pq_base, partitioning=None, table_name='products')
        
        # Also write to DuckDB
        write_to_duckdb(validated_table, conn, 'products')
        
        print(f"Loaded {len(validated_table)} valid rows to bronze layer (Parquet + DuckDB)")
        mark_processed(conn, src, len(validated_table), 0, 'success')
        
    except Exception as e:
        # Handle validation errors - write to rejects with reason
        print(f"Products: Schema validation FAILED - {e}")
        
        # Create rejects directory
        rejects_path = lake_root / '_rejects'
        rejects_path.mkdir(parents=True, exist_ok=True)
        
        # Add rejection reason and timestamp
        rejection_reason = f"Schema validation failed: {str(e)}"
        reject_table = table.append_column('rejection_reason', pa.array([rejection_reason] * len(table)))
        reject_table = reject_table.append_column('rejected_at', pa.array([dt.datetime.utcnow()] * len(table)))
        
        # Write rejected data
        reject_file = rejects_path / f"products_schema_reject_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
        pq.write_table(reject_table, str(reject_file))
        print(f"Rejected data written to: {reject_file}")
        
        # Mark as processed with all rows rejected
        mark_processed(conn, src, 0, len(table), 'all_rejected')

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

    print("Processing bronze layer: customers and products")
    load_customers(raw_root, lake_root, conn)
    load_products(raw_root, lake_root, conn)

    print("Bronze load completed for customers and products.")

if __name__ == '__main__':
    main()
