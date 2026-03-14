"""Fix X968D - remove 3 extra units"""
import frappe
from frappe.utils import nowdate, nowtime

def fix_x968d():
    WAREHOUSE = "Main ICD Store - I"
    COMPANY = "ICD"

    print("🔧 Fixing X968D - removing 3 extra units...")

    val_rate = frappe.db.get_value("Bin",
        {"item_code": "X968D", "warehouse": WAREHOUSE},
        "valuation_rate") or 1

    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = "Material Issue"
    se.company = COMPANY
    se.posting_date = nowdate()
    se.posting_time = nowtime()
    se.set_posting_time = 1

    se.append("items", {
        "item_code": "X968D",
        "s_warehouse": WAREHOUSE,
        "qty": 3,
        "basic_rate": val_rate
    })

    try:
        se.insert()
        se.submit()
        print(f"✅ Stock Entry {se.name} SUBMITTED - Removed 3 units from X968D")

        # Verify
        new_qty = frappe.db.get_value("Bin",
            {"item_code": "X968D", "warehouse": WAREHOUSE}, "actual_qty")
        print(f"✅ X968D new qty: {new_qty}")
    except Exception as e:
        print(f"❌ Error: {e}")
        frappe.db.rollback()
