# Personal Progress Tracker

## Deliverables
- `/scripts/generate_data.py`: Data generation implementation
- `/scripts/load_to_bronze.py` or `/scripts/bronze_dlt_pipeline.py`: Bronze ingestion
- `/dbt/`: Complete dbt project with models, tests, snapshots
- `data_raw/samples/`: Sample data for review
- `lake/bronze/parquet/samples/`: Sample Bronze outputs
- `duckdb/warehouse.duckdb`: DuckDB database (if < 50MB)
- `analytics/report.pbix`: Power BI dashboard
- `docs/post_mortem.md`: Reflection document

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
- [x] Commit changes for each table in `/scripts/generate_data.py`
- [x] Validate outputs and partitioning logic

#### Next Steps
- [ ] Generate events data
- [ ] Validate all synthetic datasets for schema compliance and anomaly logic
- [ ] Organize sample outputs in `data_raw/samples/` and commit
- [ ] Finalize documentation and update progress tracker

### Exercise 3: Bronze Ingestion
- [ ] Not started

### Exercise 4: Silver Layer
- [ ] Not started

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


**Notes:**
- Update this tracker regularly to keep track on progress/blockers.
- Add details or blockers as needed.