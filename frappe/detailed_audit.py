"""Detailed Stock Audit v2 - ALL removed items + ALL serials"""
import frappe
from frappe.utils import now_datetime
import json

WAREHOUSE = "Main ICD Store - I"

def audit():
    results = {
        "timestamp": str(now_datetime()),
        "all_items_with_serials": [],
        "removed_items": [],
        "removed_today": [],
        "changes_today": [],
        "summary": {}
    }
    
    print("=" * 100)
    print("🔬 DETAILED STOCK AUDIT v2 - FULL SERIAL LIST")
    print("=" * 100)
    
    today = str(now_datetime().date())
    
    # =====================================================================
    # 1. ALL ITEMS IN STOCK WITH THEIR SERIALS
    # =====================================================================
    print("\n" + "=" * 100)
    print("1️⃣  ALL ITEMS IN STOCK WITH SERIAL NUMBERS")
    print("=" * 100)
    
    items_in_stock = frappe.db.sql("""
        SELECT 
            b.item_code,
            i.item_name,
            b.actual_qty,
            i.has_serial_no
        FROM `tabBin` b
        JOIN `tabItem` i ON i.name = b.item_code
        WHERE b.warehouse = %s AND b.actual_qty > 0
        ORDER BY b.item_code
    """, WAREHOUSE, as_dict=True)
    
    print(f"\n   Total items with positive stock: {len(items_in_stock)}")
    
    for item in items_in_stock:
        item_data = {
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": int(item.actual_qty),
            "has_serial_no": item.has_serial_no,
            "serials": []
        }
        
        if item.has_serial_no:
            serials = frappe.db.sql("""
                SELECT name FROM `tabSerial No`
                WHERE item_code = %s AND status = 'Active'
                ORDER BY name
            """, item.item_code, as_dict=True)
            item_data["serials"] = [s.name for s in serials]
            item_data["serial_count"] = len(serials)
        
        results["all_items_with_serials"].append(item_data)
    
    # =====================================================================
    # 2. ALL REMOVED ITEMS
    # =====================================================================
    print("\n" + "=" * 100)
    print("2️⃣  ALL REMOVED ITEMS (Had stock before, now ZERO)")
    print("=" * 100)
    
    removed = frappe.db.sql("""
        SELECT DISTINCT 
            sle.item_code,
            i.item_name,
            i.has_serial_no,
            COALESCE(b.actual_qty, 0) as current_qty
        FROM `tabStock Ledger Entry` sle
        JOIN `tabItem` i ON i.name = sle.item_code
        LEFT JOIN `tabBin` b ON b.item_code = sle.item_code AND b.warehouse = %s
        WHERE sle.warehouse = %s
        AND sle.is_cancelled = 0
        AND (b.actual_qty IS NULL OR b.actual_qty <= 0)
        ORDER BY sle.item_code
    """, (WAREHOUSE, WAREHOUSE), as_dict=True)
    
    print(f"\n   Total removed items (ever): {len(removed)}")
    
    for r in removed:
        last_txn = frappe.db.sql("""
            SELECT voucher_no, voucher_type, posting_date
            FROM `tabStock Ledger Entry`
            WHERE item_code = %s AND warehouse = %s AND is_cancelled = 0
            ORDER BY posting_date DESC, posting_time DESC
            LIMIT 1
        """, (r.item_code, WAREHOUSE), as_dict=True)
        
        old_serials = []
        if r.has_serial_no:
            old_serials = frappe.db.sql("""
                SELECT name, status FROM `tabSerial No`
                WHERE item_code = %s ORDER BY status, name
            """, r.item_code, as_dict=True)
        
        removed_item = {
            "item_code": r.item_code,
            "item_name": r.item_name,
            "current_qty": int(r.current_qty),
            "has_serial_no": r.has_serial_no,
            "last_voucher": last_txn[0].voucher_no if last_txn else "N/A",
            "last_voucher_type": last_txn[0].voucher_type if last_txn else "N/A",
            "last_date": str(last_txn[0].posting_date) if last_txn else "N/A",
            "old_serials": [{"name": s.name, "status": s.status} for s in old_serials]
        }
        
        results["removed_items"].append(removed_item)
        
        # Check if removed today
        if last_txn and str(last_txn[0].posting_date) == today:
            results["removed_today"].append(removed_item)
    
    # =====================================================================
    # 3. ITEMS REMOVED TODAY
    # =====================================================================
    print("\n" + "=" * 100)
    print("3️⃣  ITEMS REMOVED TODAY (Set to ZERO on " + today + ")")
    print("=" * 100)
    
    if results["removed_today"]:
        print(f"\n   ⚠️ Items removed TODAY: {len(results['removed_today'])}")
        for r in results["removed_today"]:
            print(f"\n   {r['item_code']}: {r['item_name'][:60]}")
            print(f"      Via: {r['last_voucher']} ({r['last_voucher_type']})")
            if r["old_serials"]:
                print(f"      Serials: {len(r['old_serials'])}")
                for s in r["old_serials"]:
                    print(f"         - {s['name']} ({s['status']})")
    else:
        print("\n   ✅ No items removed today")
    
    # =====================================================================
    # 4. CHANGES TODAY
    # =====================================================================
    print("\n" + "=" * 100)
    print("4️⃣  ALL STOCK MOVEMENTS TODAY")
    print("=" * 100)
    
    # Stock Entries
    stock_entries = frappe.db.sql("""
        SELECT name, stock_entry_type, posting_date FROM `tabStock Entry`
        WHERE posting_date = %s AND docstatus = 1 ORDER BY creation
    """, today, as_dict=True)
    
    print(f"\n   Stock Entries: {len(stock_entries)}")
    for se in stock_entries:
        # Get items for this SE
        se_items = frappe.db.sql("""
            SELECT item_code FROM `tabStock Entry Detail`
            WHERE parent = %s AND (t_warehouse = %s OR s_warehouse = %s)
        """, (se.name, WAREHOUSE, WAREHOUSE), as_dict=True)
        item_codes = [i.item_code for i in se_items]
        
        print(f"      {se.name}: {se.stock_entry_type}")
        print(f"         Items: {', '.join(item_codes)}")
        
        results["changes_today"].append({
            "doctype": "Stock Entry",
            "name": se.name,
            "type": se.stock_entry_type,
            "item_list": item_codes
        })
    
    # Stock Reconciliations
    stock_recons = frappe.db.sql("""
        SELECT name, purpose, posting_date FROM `tabStock Reconciliation`
        WHERE posting_date = %s AND docstatus = 1 ORDER BY creation
    """, today, as_dict=True)
    
    print(f"\n   Stock Reconciliations: {len(stock_recons)}")
    for sr in stock_recons:
        sr_items = frappe.db.sql("""
            SELECT item_code FROM `tabStock Reconciliation Item`
            WHERE parent = %s AND warehouse = %s
        """, (sr.name, WAREHOUSE), as_dict=True)
        item_codes = [i.item_code for i in sr_items]
        
        print(f"      {sr.name}: {sr.purpose}")
        print(f"         Items: {', '.join(item_codes)}")
        
        results["changes_today"].append({
            "doctype": "Stock Reconciliation",
            "name": sr.name,
            "type": sr.purpose,
            "item_list": item_codes
        })
    
    # =====================================================================
    # SUMMARY
    # =====================================================================
    results["summary"] = {
        "total_items_in_stock": len(items_in_stock),
        "total_removed_items_ever": len(removed),
        "removed_today_count": len(results["removed_today"]),
        "stock_entries_today": len(stock_entries),
        "stock_recons_today": len(stock_recons)
    }
    
    print("\n" + "=" * 100)
    print("📊 SUMMARY")
    print("=" * 100)
    print(f"""
   Items in stock: {len(items_in_stock)}
   Total removed items (all time): {len(removed)}
   Items removed TODAY: {len(results['removed_today'])}
   Stock Entries today: {len(stock_entries)}
   Stock Reconciliations today: {len(stock_recons)}
    """)
    
    # Save
    with open("/tmp/detailed_audit_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("   ✅ Results saved to /tmp/detailed_audit_results.json")
    
    return results

