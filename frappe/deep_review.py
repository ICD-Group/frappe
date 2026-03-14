"""
DEEP REVIEW - 60 Year ERPNext Expert Audit
December 26, 2025
"""
import frappe

def deep_review():
    print("=" * 90)
    print("🔬 DEEP REVIEW - DR. ERPNEXT 60-YEAR EXPERT AUDIT")
    print("=" * 90)

    issues = []
    warnings = []
    recommendations = []

    # ========================================================================
    # 1. SHELF FIELD MANDATORY STATUS
    # ========================================================================
    print("\n" + "=" * 90)
    print("1️⃣  SHELF FIELD CONFIGURATION REVIEW")
    print("=" * 90)

    shelf_fields = frappe.db.sql("""
        SELECT name, dt, fieldname, reqd, hidden
        FROM `tabCustom Field`
        WHERE fieldname = 'shelf'
        ORDER BY dt
    """, as_dict=True)

    print("\n📋 Current Shelf Field Status:")
    print(f"{'DocType':<40} {'Required':>10} {'Hidden':>10}")
    print("-" * 60)

    critical_doctypes = [
        'Stock Entry Detail',
        'Stock Reconciliation Item',
        'Delivery Note Item',
        'Purchase Receipt Item',
        'Sales Invoice Item',
        'Serial No'
    ]

    for field in shelf_fields:
        reqd_status = "✅ YES" if field.reqd else "❌ NO"
        hidden_status = "Hidden" if field.hidden else "Visible"
        print(f"{field.dt:<40} {reqd_status:>10} {hidden_status:>10}")

        if field.dt in ['Stock Entry Detail', 'Stock Reconciliation Item'] and not field.reqd:
            issues.append(f"CRITICAL: {field.dt} shelf is NOT mandatory - users can skip location!")

    # ========================================================================
    # 2. INVENTORY DIMENSION CONFIGURATION
    # ========================================================================
    print("\n" + "=" * 90)
    print("2️⃣  INVENTORY DIMENSION CONFIGURATION")
    print("=" * 90)

    inv_dims = frappe.db.sql("""
        SELECT name, dimension_name, reference_document, reqd, document_type
        FROM `tabInventory Dimension`
    """, as_dict=True)

    for dim in inv_dims:
        print(f"\nDimension: {dim.dimension_name}")
        print(f"  Reference: {dim.reference_document}")
        print(f"  Required: {'Yes' if dim.reqd else 'No'}")
        print(f"  Document Type: {dim.document_type or 'All'}")

    # ========================================================================
    # 3. STOCK SETTINGS REVIEW
    # ========================================================================
    print("\n" + "=" * 90)
    print("3️⃣  STOCK SETTINGS REVIEW")
    print("=" * 90)

    stock_settings = frappe.get_single("Stock Settings")

    critical_settings = [
        ('allow_negative_stock', 'Allow Negative Stock', False),
        ('auto_insert_price_list_rate_if_missing', 'Auto Insert Price List Rate', None),
        ('allow_existing_serial_no_with_different_item', 'Allow Serial Reuse', False),
        ('automatically_set_serial_nos_based_on_fifo', 'Auto FIFO Serial', None),
    ]

    for field, label, recommended in critical_settings:
        value = getattr(stock_settings, field, None)
        status = "⚠️" if recommended is not None and value != recommended else "ℹ️"
        print(f"  {status} {label}: {value}")

        if field == 'allow_existing_serial_no_with_different_item' and value:
            warnings.append("Serial reuse between items is ENABLED - may cause tracking confusion")

    # ========================================================================
    # 4. SERIAL NUMBER INTEGRITY CHECK
    # ========================================================================
    print("\n" + "=" * 90)
    print("4️⃣  SERIAL NUMBER INTEGRITY CHECK")
    print("=" * 90)

    # Check for serials with wrong item assignment
    serial_issues = frappe.db.sql("""
        SELECT sn.name, sn.item_code, sn.status, sn.warehouse,
               sle.item_code as sle_item
        FROM `tabSerial No` sn
        LEFT JOIN `tabStock Ledger Entry` sle ON sle.serial_no LIKE CONCAT('%', sn.name, '%')
            AND sle.is_cancelled = 0
        WHERE sn.status = 'Active'
        AND sn.item_code != COALESCE(sle.item_code, sn.item_code)
        LIMIT 10
    """, as_dict=True)

    if serial_issues:
        print("⚠️ Serials with potential item mismatch:")
        for s in serial_issues:
            print(f"  {s.name}: SN says {s.item_code}, SLE says {s.sle_item}")
            warnings.append(f"Serial {s.name} may have item mismatch")
    else:
        print("✅ No serial number integrity issues found")

    # Check for duplicate active serials
    dup_serials = frappe.db.sql("""
        SELECT name, COUNT(*) as cnt
        FROM `tabSerial No`
        WHERE status = 'Active'
        GROUP BY name
        HAVING cnt > 1
    """, as_dict=True)

    if dup_serials:
        for d in dup_serials:
            issues.append(f"Duplicate active serial: {d.name}")
    else:
        print("✅ No duplicate active serials")

    # ========================================================================
    # 5. BIN VS STOCK LEDGER CONSISTENCY
    # ========================================================================
    print("\n" + "=" * 90)
    print("5️⃣  BIN VS STOCK LEDGER CONSISTENCY CHECK")
    print("=" * 90)

    # Check for bin/SLE mismatches
    bin_mismatches = frappe.db.sql("""
        SELECT 
            b.item_code,
            b.warehouse,
            b.actual_qty as bin_qty,
            (SELECT qty_after_transaction 
             FROM `tabStock Ledger Entry` sle 
             WHERE sle.item_code = b.item_code 
             AND sle.warehouse = b.warehouse 
             AND sle.is_cancelled = 0
             ORDER BY posting_date DESC, posting_time DESC, creation DESC 
             LIMIT 1) as sle_qty
        FROM `tabBin` b
        WHERE b.warehouse = 'Main ICD Store - I'
        HAVING bin_qty != COALESCE(sle_qty, 0) AND ABS(bin_qty - COALESCE(sle_qty, 0)) > 0.01
        LIMIT 20
    """, as_dict=True)

    if bin_mismatches:
        print("⚠️ Bin vs SLE mismatches found:")
        for m in bin_mismatches:
            print(f"  {m.item_code}: Bin={m.bin_qty}, SLE={m.sle_qty}")
            issues.append(f"Bin mismatch: {m.item_code}")
    else:
        print("✅ All bins match Stock Ledger entries")

    # ========================================================================
    # 6. NEGATIVE STOCK CHECK
    # ========================================================================
    print("\n" + "=" * 90)
    print("6️⃣  NEGATIVE STOCK CHECK")
    print("=" * 90)

    negative_bins = frappe.db.sql("""
        SELECT item_code, actual_qty
        FROM `tabBin`
        WHERE warehouse = 'Main ICD Store - I'
        AND actual_qty < 0
    """, as_dict=True)

    if negative_bins:
        print("❌ NEGATIVE STOCK FOUND:")
        for nb in negative_bins:
            print(f"  {nb.item_code}: {nb.actual_qty}")
            issues.append(f"Negative stock: {nb.item_code} = {nb.actual_qty}")
    else:
        print("✅ No negative stock")

    # ========================================================================
    # 7. SUMMARY & RECOMMENDATIONS
    # ========================================================================
    print("\n" + "=" * 90)
    print("📊 DEEP REVIEW SUMMARY")
    print("=" * 90)

    print(f"\n❌ CRITICAL ISSUES: {len(issues)}")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")

    print(f"\n⚠️ WARNINGS: {len(warnings)}")
    for i, warning in enumerate(warnings, 1):
        print(f"   {i}. {warning}")

    # Recommendations
    recommendations = [
        "RESTORE shelf mandatory on Stock Entry Detail and Stock Reconciliation Item",
        "Review 'allow_existing_serial_no_with_different_item' setting - consider disabling after audit",
        "Run Stock Reposting Tool if any bin mismatches persist",
        "Implement Shelf validation in custom scripts for critical transactions",
    ]

    print(f"\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")

    return {
        'issues': len(issues),
        'warnings': len(warnings),
        'recommendations': recommendations
    }
