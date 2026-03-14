"""
FIX ALL ISSUES - Restore Proper Configuration
60-Year ERPNext Expert Fix
"""
import frappe

def fix_all_issues():
    print("=" * 90)
    print("🔧 FIXING ALL ISSUES - RESTORING PROPER CONFIGURATION")
    print("=" * 90)

    # ========================================================================
    # 1. RESTORE MANDATORY SHELF ON STOCK ENTRY DETAIL
    # ========================================================================
    print("\n1️⃣  Restoring mandatory shelf on Stock Entry Detail...")

    frappe.db.set_value("Custom Field", "Stock Entry Detail-shelf", "reqd", 1)
    print("   ✅ Stock Entry Detail-shelf: reqd = 1 (MANDATORY)")

    # ========================================================================
    # 2. RESTORE MANDATORY SHELF ON STOCK RECONCILIATION ITEM
    # ========================================================================
    print("\n2️⃣  Restoring mandatory shelf on Stock Reconciliation Item...")

    frappe.db.set_value("Custom Field", "Stock Reconciliation Item-shelf", "reqd", 1)
    print("   ✅ Stock Reconciliation Item-shelf: reqd = 1 (MANDATORY)")

    # ========================================================================
    # 3. DISABLE SERIAL REUSE SETTING
    # ========================================================================
    print("\n3️⃣  Disabling serial reuse between items...")

    frappe.db.set_value("Stock Settings", None,
        "allow_existing_serial_no_with_different_item", 0)
    print("   ✅ allow_existing_serial_no_with_different_item = 0 (DISABLED)")

    # ========================================================================
    # 4. VERIFY INVENTORY DIMENSION
    # ========================================================================
    print("\n4️⃣  Checking Inventory Dimension 'Shelf' configuration...")

    shelf_dim = frappe.db.get_value("Inventory Dimension",
        {"dimension_name": "Shelf"},
        ["name", "reqd"], as_dict=True)

    if shelf_dim:
        print(f"   Shelf dimension exists: {shelf_dim.name}")
        print(f"   Current reqd: {shelf_dim.reqd}")
        # Note: Inventory Dimension reqd affects ALL doctypes - keep as is
        # Individual Custom Field reqd handles specific doctypes
    else:
        print("   ⚠️ Shelf dimension not found")

    # Commit all changes
    frappe.db.commit()

    # ========================================================================
    # 5. CLEAR CACHE
    # ========================================================================
    print("\n5️⃣  Clearing cache...")
    frappe.clear_cache()
    print("   ✅ Cache cleared")

    # ========================================================================
    # 6. VERIFY CHANGES
    # ========================================================================
    print("\n" + "=" * 90)
    print("📋 VERIFICATION - CURRENT STATUS:")
    print("=" * 90)

    # Check shelf fields
    for dt in ['Stock Entry Detail', 'Stock Reconciliation Item']:
        field_name = f"{dt}-shelf"
        reqd = frappe.db.get_value("Custom Field", field_name, "reqd")
        status = "✅ MANDATORY" if reqd else "❌ NOT MANDATORY"
        print(f"   {dt}: {status}")

    # Check stock settings
    serial_reuse = frappe.db.get_single_value("Stock Settings",
        "allow_existing_serial_no_with_different_item")
    status = "❌ ENABLED (risk)" if serial_reuse else "✅ DISABLED (safe)"
    print(f"   Serial Reuse Between Items: {status}")

    print("\n" + "=" * 90)
    print("✅ ALL ISSUES FIXED!")
    print("=" * 90)

    return {"status": "fixed"}
