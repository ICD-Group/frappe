"""Verify stock balance against Mali's sheet"""
import frappe
import pandas as pd

def verify_stock():
    # Read Mali's sheet
    df = pd.read_excel('/tmp/ICD_Stock_Report.xlsx', sheet_name='Query Report')

    print("=" * 90)
    print("📊 STOCK BALANCE VERIFICATION - Mali vs ERPNext")
    print("=" * 90)
    print(f"{'Item':<20} {'Mali Target':>12} {'ERPNext':>12} {'Match':>8}")
    print("-" * 90)

    matches = 0
    mismatches = []

    for _, row in df.iterrows():
        item_code = str(row['Item']).strip()

        # Skip 0PD89Y
        if item_code == '0PD89Y':
            continue

        # Map 2KH133-136 to 39XRY
        if item_code == '2KH133-136':
            item_code = '39XRY'

        # Get target qty from Mali
        if pd.notna(row['New quantity']):
            target_qty = int(float(row['New quantity']))
        else:
            target_qty = int(row['Balance Qty']) if pd.notna(row['Balance Qty']) else 0

        # Get current ERPNext qty
        erp_qty = frappe.db.get_value("Bin",
            {"item_code": item_code, "warehouse": "Main ICD Store - I"},
            "actual_qty") or 0
        erp_qty = int(erp_qty)

        # Compare
        if erp_qty == target_qty:
            matches += 1
        else:
            mismatches.append((item_code, target_qty, erp_qty))

    # Print mismatches
    for item_code, target, actual in mismatches:
        print(f"{item_code:<20} {target:>12} {actual:>12} {'❌':>8}")

    print("-" * 90)
    print(f"\n✅ MATCHES: {matches}")
    print(f"❌ MISMATCHES: {len(mismatches)}")

    if len(mismatches) == 0:
        print("\n🎉 ALL ITEMS MATCH MALI'S TARGET QUANTITIES!")
    else:
        print(f"\n⚠️ {len(mismatches)} items need attention")

    return {"matches": matches, "mismatches": len(mismatches)}
