
import pandas as pd


# --------------------------------------------------
# Tool 1: Get dataset overview
# --------------------------------------------------

def get_dataset_overview(df):

    return {
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "columns": list(df.columns),
        "data_types": {
            str(column): str(dtype)
            for column, dtype in df.dtypes.items()
        },
        "missing_values": {
            str(column): int(count)
            for column, count in df.isna().sum().items()
        }
    }


# --------------------------------------------------
# Tool 2: Get information about a specific column
# --------------------------------------------------

def get_column_summary(df, column):

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    series = df[column]

    result = {
        "column": column,
        "data_type": str(series.dtype),
        "non_empty_values": int(series.count()),
        "missing_values": int(series.isna().sum()),
        "unique_values": int(series.nunique())
    }

    numeric = pd.to_numeric(series, errors="coerce").dropna()

    if len(numeric) > 0:

        result["numeric_summary"] = {
            "minimum": float(numeric.min()),
            "maximum": float(numeric.max()),
            "average": float(numeric.mean()),
            "median": float(numeric.median())
        }

    else:

        result["sample_values"] = [
            str(value)
            for value in series.dropna().unique()[:10]
        ]

    return result


# --------------------------------------------------
# Tool 3: Analyze a numeric column
# --------------------------------------------------

def analyze_numeric_column(df, column, operation):

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    numeric = pd.to_numeric(
        df[column],
        errors="coerce"
    ).dropna()

    if numeric.empty:
        raise ValueError(
            f"Column '{column}' does not contain usable numeric values."
        )

    operations = {
        "sum": numeric.sum,
        "average": numeric.mean,
        "minimum": numeric.min,
        "maximum": numeric.max,
        "median": numeric.median,
        "count": numeric.count,
        "standard_deviation": numeric.std
    }

    if operation not in operations:
        raise ValueError(f"Unsupported operation: {operation}")

    value = operations[operation]()

    return {
        "column": column,
        "operation": operation,
        "result": float(value)
    }


# --------------------------------------------------
# Tool 4: Group data and calculate an aggregate
# --------------------------------------------------

def group_by_analysis(
    df,
    group_column,
    value_column,
    operation
):

    if group_column not in df.columns:
        raise ValueError(
            f"Column '{group_column}' does not exist."
        )

    if value_column not in df.columns:
        raise ValueError(
            f"Column '{value_column}' does not exist."
        )

    grouped = df.groupby(
        group_column,
        dropna=False
    )[value_column]

    operations = {
        "sum": grouped.sum,
        "average": grouped.mean,
        "minimum": grouped.min,
        "maximum": grouped.max,
        "count": grouped.count
    }

    if operation not in operations:
        raise ValueError(f"Unsupported operation: {operation}")

    result = operations[operation]()

    return {
        "group_column": group_column,
        "value_column": value_column,
        "operation": operation,
        "results": {
            str(key): (
                float(value)
                if pd.notna(value)
                else None
            )
            for key, value in result.items()
        }
    }


# --------------------------------------------------
# Tool 5: Find the most frequent values in a column
# --------------------------------------------------

def get_top_values(df, column, limit=10):

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100.")

    result = df[column].value_counts(
        dropna=False
    ).head(limit)

    return {
        "column": column,
        "top_values": {
            str(key): int(value)
            for key, value in result.items()
        }
    }
