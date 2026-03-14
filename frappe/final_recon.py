"""Final Stock Reconciliation to fix remaining mismatches"""
import frappe
from frappe.utils import nowdate, nowtime
import pandas as pd

def run_final_recon():
    WAREHOUSE = "Main ICD Store - I"
    COMPANY = "ICD"
    EXPENSE_ACCOUNT = "5119 - Stock Adjustment - I"
    COST_CENTER = "General Management - I"

    # Read Mali's sheet
    df = pd.read_excel('/tmp/ICD_Stock_Report.xlsx', sheet_name='Query Report')

    print("=" * 80)
    print("🔧 FINAL STOCK RECONCILIATION - FIXING MISMATCHES")
    print("=" * 80)

    items_to_fix = []

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
            {"item_code": item_code, "warehouse": WAREHOUSE},
            "actual_qty") or 0
        erp_qty = int(erp_qty)

        # If mismatch, add to fix list
        if erp_qty != target_qty:
            # Check if serialized
            has_serial = frappe.db.get_value("Item", item_code, "has_serial_no")

            items_to_fix.append({
                'item_code': item_code,
                'current': erp_qty,
                'target': target_qty,
                'diff': target_qty - erp_qty,
                'has_serial': has_serial
            })
            print(f"  {item_code}: {erp_qty} → {target_qty} ({target_qty - erp_qty:+d}) Serial={has_serial}")

    if not items_to_fix:
        print("\n✅ No items need fixing!")
        return

    print(f"\n📦 Creating Stock Reconciliation for {len(items_to_fix)} items...")

    # Separate serialized and non-serialized
    non_serial_items = [i for i in items_to_fix if not i['has_serial']]
    serial_items = [i for i in items_to_fix if i['has_serial']]

    # Non-serialized items - use Stock Reconciliation
    if non_serial_items:
        sr = frappe.new_doc("Stock Reconciliation")
        sr.company = COMPANY
        sr.purpose = "Stock Reconciliation"
        sr.expense_account = EXPENSE_ACCOUNT
        sr.cost_center = COST_CENTER

        for item in non_serial_items:
            val_rate = frappe.db.get_value("Bin",
                {"item_code": item['item_code'], "warehouse": WAREHOUSE},
                "valuation_rate") or 1

            sr.append("items", {
                "item_code": item['item_code'],
                "warehouse": WAREHOUSE,
                "qty": item['target'],
                "valuation_rate": val_rate
            })

        try:
            sr.insert()
            sr.submit()
            print(f"\n✅ Stock Reconciliation {sr.name} SUBMITTED ({len(non_serial_items)} non-serial items)")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            frappe.db.rollback()

    # Serialized items - need different approach
    if serial_items:
        print(f"\n⚠️ SERIALIZED ITEMS ({len(serial_items)}) - Need manual adjustment:")
        for item in serial_items:
            if item['diff'] > 0:
                print(f"  {item['item_code']}: Need to ADD {item['diff']} units (with serials)")
            else:
                print(f"  {item['item_code']}: Need to REMOVE {abs(item['diff'])} units")

    frappe.db.commit()

    print("\n" + "=" * 80)
    print("✅ FINAL RECONCILIATION COMPLETE")
    print("=" * 80)
