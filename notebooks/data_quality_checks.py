"""
Reusable PySpark data-quality checks for the AdventureWorks Silver layer.

Configure the expected primary keys and required columns for each dataset
before calling run_table_checks(). The helper does not assume business keys
that are not defined in the source project.
"""

from typing import Dict, Iterable, List, Optional
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def run_table_checks(
    df: DataFrame,
    table_name: str,
    primary_key_columns: Optional[List[str]] = None,
    required_columns: Optional[List[str]] = None,
) -> Dict[str, object]:
    """Run basic completeness, uniqueness, and schema checks on a DataFrame."""
    primary_key_columns = primary_key_columns or []
    required_columns = required_columns or []

    missing_required = [c for c in required_columns if c not in df.columns]
    missing_keys = [c for c in primary_key_columns if c not in df.columns]

    if missing_required or missing_keys:
        return {
            "table": table_name,
            "status": "FAILED",
            "row_count": df.count(),
            "null_counts": {},
            "duplicate_key_count": None,
            "missing_required_columns": missing_required,
            "missing_key_columns": missing_keys,
        }

    row_count = df.count()
    columns_to_check = sorted(set(required_columns + primary_key_columns))
    null_exprs = [
        F.sum(F.when(F.col(c).isNull(), 1).otherwise(0)).alias(c)
        for c in columns_to_check
    ]
    null_row = df.agg(*null_exprs).first() if null_exprs else None
    null_counts = (
        {c: int(null_row[c] or 0) for c in columns_to_check}
        if null_row else {}
    )

    duplicate_key_count = None
    if primary_key_columns:
        duplicate_key_count = (
            df.groupBy(*primary_key_columns)
              .count()
              .filter(F.col("count") > 1)
              .count()
        )

    has_nulls = any(value > 0 for value in null_counts.values())
    has_duplicates = duplicate_key_count is not None and duplicate_key_count > 0
    status = "PASSED" if not has_nulls and not has_duplicates else "FAILED"

    return {
        "table": table_name,
        "status": status,
        "row_count": row_count,
        "null_counts": null_counts,
        "duplicate_key_count": duplicate_key_count,
        "missing_required_columns": [],
        "missing_key_columns": [],
    }


def print_quality_report(results: Iterable[Dict[str, object]]) -> None:
    """Print a readable report; results can also be written to a Delta audit table."""
    for result in results:
        print(
            f"{result['table']}: {result['status']} | "
            f"rows={result['row_count']} | "
            f"duplicate_keys={result['duplicate_key_count']} | "
            f"nulls={result['null_counts']} | "
            f"missing_required={result['missing_required_columns']} | "
            f"missing_keys={result['missing_key_columns']}"
        )


# Example usage in your Spark notebook after loading a Silver DataFrame:
#
# checks = [
#     run_table_checks(
#         df_sales,
#         table_name="AdventureWorks_Sales",
#         primary_key_columns=["REPLACE_WITH_CONFIRMED_SALES_KEY"],
#         required_columns=["OrderDate", "OrderNumber", "OrderQuantity"],
#     )
# ]
# print_quality_report(checks)
#
# Do not leave placeholder key names in a production run. Confirm the actual
# business key from the source data model before enabling uniqueness checks.
