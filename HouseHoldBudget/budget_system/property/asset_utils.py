import pandas as pd
from typing import Dict, Union
from .asset import PropertyRegistry
import matplotlib.pyplot as plt


def summarize_total_value(registry: PropertyRegistry) -> Dict[str, Union[float, pd.DataFrame]]:
    """Compute total asset value and a summary table by type and owner."""
    df = registry.to_dataframe()

    if df.empty or "Value" not in df.columns:
        return {"Total Value": 0.0, "Summary Table": pd.DataFrame()}

    # make sure Value is numeric
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    total_value = float(df["Value"].sum(skipna=True))

    # group by Type and Owner
    summary = (
        df.groupby(["Type", "Owner"], dropna=False)["Value"]
        .agg(["sum", "mean", "count"])
        .reset_index()
    )
    summary.rename(
        columns={
            "sum": "Total Value",
            "mean": "Average Value",
            "count": "Count",
        },
        inplace=True,
    )

    # format currency columns for display
    summary["Total Value"] = summary["Total Value"].map(
        lambda x: f"${x:,.2f}" if pd.notna(x) else ""
    )
    summary["Average Value"] = summary["Average Value"].map(
        lambda x: f"${x:,.2f}" if pd.notna(x) else ""
    )

    return {
        "Total Value": total_value,
        "Summary Table": summary,
    }


def search_assets(registry: PropertyRegistry, keyword: str) -> pd.DataFrame:
    """Search assets by keyword in ID, name, type, or owner."""
    keyword_lower = keyword.strip().lower()
    rows = []

    for asset in registry:
        if (
            keyword_lower in asset.asset_id.lower()
            or keyword_lower in asset.name.lower()
            or keyword_lower in asset.asset_type.lower()
            or keyword_lower in str(asset.owner).lower()
        ):
            rows.append(asset.to_dict())

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # numeric + formatted display value
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df["Value_Display"] = df["Value"].map(
        lambda x: f"${x:,.2f}" if pd.notna(x) else ""
    )

    # keep key columns only if they exist
    cols = [
        "Asset ID",
        "Name",
        "Type",
        "Owner",
        "Value",
        "Value_Display",
        "Date Acquired",
        "Last Updated",
    ]
    df = df[[c for c in cols if c in df.columns]]

    return df


def get_visualization_data(registry: PropertyRegistry, group_by: str = "Type") -> pd.DataFrame:
    """
    Prepare aggregated data for charts (grouped by type or owner),
    and show a figure with table (left) + pie chart (right).
    """
    if group_by not in ("Type", "Owner"):
        raise ValueError("group_by must be 'Type' or 'Owner'.")

    df = registry.to_dataframe()
    if df.empty or "Value" not in df.columns:
        print("No asset data to visualize.")
        return pd.DataFrame(columns=["Label", "Value", "Percentage"])

    # make sure Value is numeric
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    grouped = (
        df.groupby(group_by, dropna=False)["Value"]
        .sum()
        .reset_index()
    )

    # rename columns for output
    grouped.rename(columns={group_by: "Label", "Value": "Value"}, inplace=True)

    total = grouped["Value"].sum()
    if total and not pd.isna(total):
        grouped["Percentage"] = (grouped["Value"] / total * 100.0).round(2)
    else:
        grouped["Percentage"] = 0.0

    result = grouped[["Label", "Value", "Percentage"]]

    # ---------- plotting: left table + right pie ----------
    if result.empty:
        print("No aggregated data to visualize.")
        return result

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # left: table
    axes[0].axis("off")
    table = axes[0].table(
        cellText=result.values,
        colLabels=result.columns,
        loc="center"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.auto_set_column_width(col=list(range(len(result.columns))))
    axes[0].set_title(f"Assets by {group_by}", pad=10)

    # right: pie chart
    labels = result["Label"].astype(str)
    values = result["Value"]

    axes[1].pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90
    )
    axes[1].set_title("Value Share")

    plt.tight_layout()
    plt.show()

    return result