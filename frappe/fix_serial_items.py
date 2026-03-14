"""Fix serialized items qty mismatches"""
import frappe
from frappe.utils import nowdate, nowtime

WAREHOUSE = "Main ICD Store - I"
COMPANY = "ICD"

def fix_serial_items():
    print("=" * 80)
    print("🔧 FIXING SERIALIZED ITEMS QTY MISMATCHES")
    print("=" * 80)

    # Items to fix with their target qty (from Mali's sheet)
    items_to_fix = [
        ('G176J', 73, 75, +2),       # Add 2
        ('378343-001', 1, 7, +6),    # Add 6
        ('F238F', 9, 7, -2),         # Remove 2
        ('X968D', 0, 3, +3),         # Add 3
        ('44T2216', 5, 6, +1),       # Add 1
        ('00E7600', 2, 5, +3),       # Add 3
        ('800-35052-01', 3, 1, -2),  # Remove 2
        ('HY7RM', 11, 10, -1),       # Remove 1
        ('303-115-003D', 6, 5, -1),  # Remove 1
        ('P19510-03-A', 6, 5, -1),   # Remove 1
        ('0HHX14', 4, 3, -1),        # Remove 1
        ('0C5RNH', 10, 12, +2),      # Add 2
        ('39XRY', 2, 1, -1),         # Remove 1
    ]

    additions = [(i, c, t, d) for i, c, t, d in items_to_fix if d > 0]
    removals = [(i, c, t, d) for i, c, t, d in items_to_fix if d < 0]

    results = {'added': [], 'removed': [], 'errors': []}

    # Process ADDITIONS
    if additions:
        print("\n📥 MATERIAL RECEIPT (Adding stock):")
        print("-" * 60)

        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Receipt"
        se.company = COMPANY
        se.posting_date = nowdate()
        se.posting_time = nowtime()
        se.set_posting_time = 1

        for item_code, current, target, diff in additions:
            # Ensure Serial No Series is set
            serial_series = frappe.db.get_value("Item", item_code, "serial_no_series")
            if not serial_series:
                frappe.db.set_value("Item", item_code, "serial_no_series", f"{item_code}.####")
                print(f"  Set serial_no_series for {item_code}")

            val_rate = frappe.db.get_value("Bin",
                {"item_code": item_code, "warehouse": WAREHOUSE},
                "valuation_rate") or 1

            se.append("items", {
                "item_code": item_code,
                "t_warehouse": WAREHOUSE,
                "qty": diff,
                "basic_rate": val_rate
            })
            print(f"  + {item_code}: +{diff} units")

        try:
            se.insert()
            se.submit()
            print(f"\n✅ Stock Entry {se.name} SUBMITTED (additions)")
            results['added'].append(se.name)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            frappe.db.rollback()
            results['errors'].append(str(e))

    # Process REMOVALS
    if removals:
        print("\n📤 MATERIAL ISSUE (Removing stock):")
        print("-" * 60)

        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Issue"
        se.company = COMPANY
        se.posting_date = nowdate()
        se.posting_time = nowtime()
        se.set_posting_time = 1

        for item_code, current, target, diff in removals:
            qty_to_remove = abs(diff)
            val_rate = frappe.db.get_value("Bin",
                {"item_code": item_code, "warehouse": WAREHOUSE},
                "valuation_rate") or 1

            se.append("items", {
                "item_code": item_code,
                "s_warehouse": WAREHOUSE,
                "qty": qty_to_remove,
                "basic_rate": val_rate
            })
            print(f"  - {item_code}: -{qty_to_remove} units")

        try:
            se.insert()
            se.submit()
            print(f"\n✅ Stock Entry {se.name} SUBMITTED (removals)")
            results['removed'].append(se.name)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            frappe.db.rollback()
            results['errors'].append(str(e))

    frappe.db.commit()

    print("\n" + "=" * 80)
    print("✅ SERIALIZED ITEMS FIX COMPLETE")
    print("=" * 80)

    return results
