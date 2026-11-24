# AdventureWorks Lakehouse Data Engineering

An end-to-end data engineering project built around the AdventureWorks sales dataset. The project demonstrates ingestion from GitHub-hosted CSV files into Azure Data Lake Storage, transformation with PySpark, and SQL-based access to curated data.

## Project Overview

This repository contains an Azure data pipeline implementation using a medallion-style data flow:

1. **Source** – AdventureWorks CSV datasets are stored in the repository under `archive/`.
2. **Bronze** – Azure Data Factory (ADF) copy pipelines ingest source files from GitHub over HTTP and land them in the Bronze container in Azure Data Lake Storage Gen2.
3. **Silver** – A PySpark notebook reads the Bronze data, applies data preparation and transformation logic, and writes Parquet outputs to the Silver container.
4. **Gold** – SQL scripts create a `gold` schema and views over the Silver Parquet data using `OPENROWSET`. An additional script demonstrates external data sources, file formats, and an external table.

## Architecture

```text
AdventureWorks CSV files (GitHub / archive)
                 |
                 v
       Azure Data Factory
       HTTP source + Copy
       Static / Dynamic pipelines
                 |
                 v
       Azure Data Lake Storage Gen2
             Bronze layer
                 |
                 v
       PySpark / Spark Notebook
       Cleansing and transformations
                 |
                 v
       Azure Data Lake Storage Gen2
             Silver layer
             Parquet files
                 |
                 v
       Serverless SQL
       Gold schema + views
       External table example
                 |
                 v
       SQL-based analytics
```

## Technologies

- Azure Data Factory – pipeline orchestration and copy activities
- Azure Data Lake Storage Gen2 – Bronze and Silver storage
- Apache Spark / PySpark – data reading, transformation, and Parquet writing
- Azure Synapse serverless SQL – SQL views and external table examples
- GitHub – source data and version control
- CSV and Parquet – source and curated data formats

## Repository Structure

```text
.
├── archive/                 # AdventureWorks source CSV files
├── credential/              # Workspace identity configuration (review before publishing)
├── dataset/                 # ADF dataset definitions and parameterized datasets
├── factory/                 # ADF factory configuration
├── integrationRuntime/      # Integration runtime configuration
├── linkedService/           # HTTP and storage linked-service definitions
├── pipeline/                # Static and dynamic ingestion pipelines
├── sqlscript/               # SQL schema, views, external table, and analytics scripts
├── Silver_layer.ipynb       # PySpark Silver-layer transformations
├── notebooks/                # Reusable data-quality helpers
├── docs/                     # Architecture and engineering notes
└── publish_config.json      # Workspace publishing configuration
```

## Source Datasets

The `archive/` directory contains the AdventureWorks CSV inputs used by the project, including:

- Calendar
- Customers
- Product categories and subcategories
- Products
- Returns
- Sales (2015, 2016, and 2017)
- Territories

## Pipeline and Transformation Details

### 1. Ingestion into Bronze

The repository includes two ADF pipeline definitions:

- **GitToRaw** – a Copy activity that reads a configured CSV source through an HTTP linked service and writes it to the Bronze data lake.
- **DynamicGitToRaw** – uses a Lookup and a ForEach pattern with parameterized source URLs, destination folders, and file names to support metadata-driven ingestion.

The dataset definitions separate source and sink configuration from pipeline logic.

### 2. Silver-layer processing

`Silver_layer.ipynb` uses PySpark to read the Bronze CSV datasets and write Parquet data to Silver. The notebook includes transformations such as:

- Deriving month and year from calendar dates
- Combining customer name fields into a full name
- Preparing product SKU and product name fields
- Converting sales stock dates to timestamps
- Replacing a character in order numbers
- Creating a derived sales quantity calculation
- Writing prepared datasets in Parquet format

### 3. Gold-layer SQL

The SQL scripts demonstrate:

- Creating a `gold` schema
- Creating views for calendar, customers, products, returns, sales, subcategories, and territories using `OPENROWSET`
- Defining a managed-identity database-scoped credential and external data sources
- Defining a Parquet external file format and an example external table

## Setup and Execution

This repository contains exported project definitions and notebook code. To run it, you need access to your own Azure environment and must configure the resources to match your deployment.

1. Create or select an Azure Data Lake Storage Gen2 account.
2. Create the required Bronze and Silver containers.
3. Configure Azure Data Factory with the factory, integration runtime, linked services, datasets, and pipelines in this repository.
4. Update source URLs, storage account names, container paths, and dataset parameters for your environment.
5. Configure authentication using managed identity or another approved identity mechanism. Grant only the required data-plane permissions.
6. Run the ingestion pipeline(s) to populate Bronze.
7. Attach the notebook to an appropriate Spark environment, update its storage paths, and run the Silver transformations.
8. Configure the serverless SQL environment and permissions, then execute the schema, view, and external-table scripts in the required order.

**Important:** The resource names and paths in the exported files are environment-specific examples. They will not work in a different Azure subscription without configuration changes. The notebook currently writes using append mode, so consider clearing or replacing target data, or implementing an idempotent load strategy, before rerunning it to avoid duplicate records.

## Security Notes

- Never commit passwords, access keys, client secrets, tokens, or other credentials to a public repository.
- Use Azure managed identity where possible and keep secrets in a secure secret store.
- Review the repository's SQL scripts and identity/configuration files before sharing or deploying them.
- Replace any credential values that may have been exposed in Git history; deleting a value from the latest file does not remove it from earlier commits.

## Data Quality Checks

A reusable PySpark helper is available at `notebooks/data_quality_checks.py`. It checks required-column presence, null counts for configured columns, and duplicate counts for configured business keys. Import it into the Spark notebook and configure the actual keys from the source model before running checks.

See [Architecture and Engineering Notes](docs/ARCHITECTURE.md) for the data-flow diagram, ingestion patterns, and an incremental-load design recommendation.

Sample Gold-layer SQL queries are available in [sqlscript/Sample Analytics Queries.sql](sqlscript/Sample%20Analytics%20Queries.sql).

## Future Improvements

- Add data-quality checks for nulls, duplicates, schema drift, and row counts.
- Make Silver loads idempotent using overwrite or incremental/merge logic where appropriate.
- Add pipeline failure handling, retries, logging, and monitoring.
- Parameterize environment-specific storage paths and resource names.
- Add a Gold semantic model or Power BI report for business-facing insights.
- Document sample SQL queries and expected outputs.

## Disclaimer

This is a learning and portfolio project built with the AdventureWorks sample dataset. Azure resource names, paths, permissions, and execution steps must be adapted to the target environment.
