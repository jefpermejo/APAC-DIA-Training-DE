
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
- [x] Ongoing: Objective and requirements review
- [x] Updated `/scripts/generate_data.py`:
    - Implemented CLI arguments (--seed, --out, --scale)
    - Generated customers and products datasets with correct schema and controlled anomalies
    - Ensured all datetime fields are timezone-aware and UTC across datasets
    - Committed customer and product synthetic data separately for traceability
    - Planning to continue with remaining datasets and partitioning

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

**Oct 2, 2025:**
    - Started objective and requirement review for Exercise 2.
    - Implemented and committed customer and product synthetic data generation logic.
    - Updated all datetime fields to be timezone-aware (UTC) for consistency.
    - Made separate commits for each dataset for better traceability.
    - Next Step: Continue generating and committing remaining datasets, ensure partitioning and anomaly logic for all sources.

**Notes:**
- Update this tracker regularly to keep track on progress/blockers.
- Add details or blockers as needed.

