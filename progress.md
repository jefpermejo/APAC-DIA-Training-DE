# Personal Progress Tracker

## Deliverables
- [x] `/scripts/generate_data.py`: Data generation implementation ✅ Complete
- [ ] `/scripts/load_to_bronze.py` or `/scripts/bronze_dlt_pipeline.py`
- [ ] `/dbt/`: Complete dbt project with models, tests, snapshots
- [ ] `data_raw/samples/`: Sample data for review
- [ ] `lake/bronze/parquet/samples/`: Sample Bronze outputs
- [ ] `duckdb/warehouse.duckdb`: DuckDB database (if < 50MB)
- [ ] `analytics/report.pbix`: Power BI dashboard
- [ ] `docs/post_mortem.md`: Reflection document

## Setup & Prerequisites
- [x] Install Python 3.10+
- [x] Install Power BI Desktop

## Repository Setup
- [x] Fork the repository
- [x] Configure Git for regular commits
- [ ] Modify .gitignore for assessment submission (to do before final submission)

## Documentation & Planning
- [x] Read `/docs/00_overview.md`
- [x] Review all schema docs (`/docs/01_raw_schemas.md`, `/schemas/schemas.py`)
- [ ] Ongoing: Document notes

## Exercises Progress

### Exercise 1: Schema Review
- [x] Completed schema analysis and documentation review

### Exercise 2: Data Generation

#### Checklist
- [x] Review objective and requirements
- [x] Implement CLI arguments (`--seed`, `--out`, `--scale`) in `/scripts/generate_data.py`
- [x] Generate customers dataset (schema, anomalies, UTC datetimes)
- [x] Generate products dataset (schema, anomalies, UTC datetimes)
- [x] Commit customer and product synthetic data separately for traceability
- [x] Generate suppliers dataset (schema, anomalies, UTC datetimes)
- [x] Generate stores dataset (schema, anomalies, UTC datetimes)
- [x] Generate orders header fact table
- [x] Generate order lines fact table
- [x] Generate events data with anomalies and validation
- [x] Generate sensors data for IoT analytics
- [x] Generate shipments data for supply chain tracking
- [x] Generate exchange rates data for currency conversion
- [x] Generate returns data with Delta Lake format and schema evolution
- [x] Implement comprehensive referential integrity across all datasets
- [x] Add controlled anomalies and edge cases for validation testing
- [x] Commit changes for each table in `/scripts/generate_data.py`
- [x] Validate outputs and partitioning logic
- [x] Organize sample outputs in `data_raw/samples/` and commit
- [x] Implement Delta Lake schema evolution (v1 → v2 with UPSERT operations)

#### Completed Features
- [x] CLI interface with seed, output path, and scale parameters
- [x] Multi-format data generation (CSV, JSON, Delta Lake)
- [x] Comprehensive data validation and quality controls
- [x] Referential integrity across all fact and dimension tables
- [x] Schema evolution demonstration with Delta Lake
- [x] Enterprise-grade synthetic data with realistic distributions

### Exercise 3: Bronze Ingestion
- [x] Done review
- [ ] Ongoing bronze layer ingestion

### Exercise 4: Silver Layer
- [ ] Ongoing review

### Exercise 5: Gold Layer
- [ ] Not started

### Exercise 6: Power BI Dashboard
- [ ] Not started

### Exercise 7: Operations & Documentation
- [ ] Not started

---
## Daily Log

- **Oct 1, 2025:**
	- Completed environment setup and schema review for Exercise 1.
	- Blocker: Admin access required to install Power BI and add variables to PATH.
	- Resolution: Raised concern with IT and received a temporary password via Trusted Advisor. Issue resolved.
	- Future Action: If this happens again, submit a ticket to IT for admin access.
    - Next Step: Proceed with Exercise 2

- **Oct 2, 2025:**
    - Started objective and requirement review for Exercise 2.
    - Implemented and committed customer and product synthetic data generation logic.
    - Updated all datetime fields to be timezone-aware (UTC) for consistency.
    - Made separate commits for each dataset for better traceability.
    - Next Step: Continue generating and committing remaining datasets, ensure partitioning and anomaly logic for all sources.

- **Oct 3, 2025:**
    - Completed synthetic data generation for dimension tables: stores and suppliers (customers and products were completed yesterday).
    - Completed fact tables: orders header and order lines.
    - Committed changes for each table in generate_data.py.
    - Next: Begin generating events data.

- **Oct 7, 2025:**
    - **COMPLETED Exercise 2**: Finished all remaining datasets (events, sensors, shipments, exchange_rates, returns)
    - Implemented Delta Lake schema evolution and comprehensive referential integrity
    - Next Step: Begin Exercise 3 (Bronze Ingestion)

- **Oct 8, 2025:**
    - **Exercise 3 Progress**: Bronze layer ingestion implementation
    - Implemented bronze layer with traditional Python script approach:
      - Dual output: DuckDB bronze schema + Parquet files (Delta to follow)
      - Audit trail: ingestion_ts (src_filename, src_row_hash - ongoing)
      - Manifest tracking for idempotent processing
    - Successfully ingested customers (800 rows) and products (250 rows) with full schema validation
    - Commits: Bronze layer implementation with audit columns
    - Next Step: Continue expanding the bronze layer to ingest the remaining data

- **Oct 9, 2025:**
    - Added error handling in bronze ingestion
    - Validated schema and ingested data successfully for customer and product
    - Code block to write to rejects folder for invalid data
    - Next: Ingest remaining datasets into bronze layer and review all requirements

- **Oct 10, 2025:**
    - Fixed suppliers CSV quoting bug in data generation.
    - Written output to Delta format for bronze layer.
    - Ingested other CSV files into the bronze layer (+suppliers and stores(non-partitioned)).
    - Committed and pushed changes to GitHub.
    - Next step: Continue ingesting the remaining data formats and review the dbt implementation to plan the Silver layer.

- **Oct 13, 2025:**
    - Committed and pushed:
        - Add partitioned: False to non-partitioned tables in load_to_bronze.py
        - Added orders_header, orders_lines and sensors data (remaining partitioned files) to bronze ingestion
        - Find all CSV files recursively under the partitioned folder
    - Ongoing: Reviewing dbt to prepare for Exercise 4 (Silver ingestion).
    - Next steps:
        - Continue bronze ingestion for other file types: JSON, Delta, XLSX, Parquet
        - Start Silver layer development for the ingested csv files (Exercise 4)
        
**Oct 14, 2025:**
    - Committed and pushed:
        - Added support for additional file formats in bronze ingestion: enabled XLSX reader and ingestion logic.
        - Added support for shipments data ingestion: enabled Parquet file handling in bronze layer.
        - (WIP) Add initial JSON ingestion script for Bronze layer (handling malformed data next).
    - Ongoing: Studying dbt to start Silver layer implementation tomorrow for available ingested data in bronze layer.

**Oct 15, 2025:**
    - Focused on Silver layer development in dbt (Exercise 4).
    - Built and refined staging models for customers, suppliers, stores, and products:
        - Applied data cleaning, type casting, and trimming to ensure consistency and quality (trimming, casting, standardization).
    - Validated all staging models with dbt tests and updated constraints as required.
    - Improved Bronze ingestion pipeline (Exercise 3):
        - Added initial Delta ingestion logic to the Bronze layer (WIP). 
    - Pushed all changes to the assessment-solution branch for review.
    
**Notes:**
- Update this tracker regularly to keep track on progress/blockers.
- Add details or blockers as needed