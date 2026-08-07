import pandas as pd

def generate_report(df, report_date):
    """Generate structured text report from analysis output."""
    if df is None or len(df) == 0:
        return "ERROR: Cannot generate report for empty or null DataFrame."
        
    revenue = df["revenue"].sum()
    customers = df["customer_id"].nunique()
    avg_order = df["revenue"].mean()

    lines = []
    lines.append("WEEKLY ANALYTICS REPORT")
    lines.append("Date: " + str(report_date))
    lines.append("")
    lines.append("== KPI SUMMARY ==")
    lines.append("Total Revenue: $" + f"{revenue:,.0f}")
    lines.append("Active Customers: " + f"{customers:,}")
    lines.append("Average Order: $" + f"{avg_order:,.0f}")
    lines.append("")
    lines.append("== KEY FINDING ==")
    
    # Safely compute top segment
    if "segment" in df.columns and not df["segment"].dropna().empty:
        top_seg = df.groupby("segment")["revenue"].sum().idxmax()
    else:
        top_seg = "N/A"
    lines.append("Top segment: " + top_seg)
    lines.append("")
    
    lines.append("== RECOMMENDED ACTION ==")
    lines.append("Allocate resources to high-growth segments.")
    return "\n".join(lines)
