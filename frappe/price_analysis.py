"""Deep Price Analysis for All Stock Items"""
import frappe
from frappe.utils import now_datetime
import json

WAREHOUSE = "Main ICD Store - I"

def analyze():
    print("=" * 120)
    print("🔬 DEEP PRICE ANALYSIS - ALL STOCK ITEMS")
    print("=" * 120)
    
    results = {
        "timestamp": str(now_datetime()),
        "items_with_price": [],
        "items_without_price": [],
        "prices_from_quotations": [],
        "prices_from_sales_orders": [],
        "summary": {}
    }
    
    # =====================================================================
    # 1. GET ALL ITEMS IN STOCK
    # =====================================================================
    print("\n" + "=" * 120)
    print("1️⃣  CHECKING STANDARD SELLING PRICE FOR ALL 101 ITEMS")
    print("=" * 120)
    
    items = frappe.db.sql("""
        SELECT 
            b.item_code,
            i.item_name,
            b.actual_qty,
            i.standard_rate,
            i.valuation_rate,
            (SELECT price_list_rate FROM `tabItem Price` ip 
             WHERE ip.item_code = b.item_code 
             AND ip.selling = 1 
             AND ip.price_list = 'Standard Selling'
             LIMIT 1) as selling_price
        FROM `tabBin` b
        JOIN `tabItem` i ON i.name = b.item_code
        WHERE b.warehouse = %s AND b.actual_qty > 0
        ORDER BY b.item_code
    """, WAREHOUSE, as_dict=True)
    
    print(f"\n   Total items in stock: {len(items)}")
    
    with_price = []
    without_price = []
    
    for item in items:
        price = item.selling_price or item.standard_rate or 0
        if price and price > 0:
            with_price.append({
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": int(item.actual_qty),
                "standard_rate": float(item.standard_rate or 0),
                "selling_price": float(item.selling_price or 0),
                "price_source": "Item Price" if item.selling_price else "Standard Rate"
            })
        else:
            without_price.append({
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": int(item.actual_qty)
            })
    
    results["items_with_price"] = with_price
    results["items_without_price"] = without_price
    
    print(f"\n   ✅ Items WITH standard price: {len(with_price)}")
    print(f"   ❌ Items WITHOUT standard price: {len(without_price)}")
    
    # =====================================================================
    # 2. ITEMS WITHOUT PRICE - DETAILED LIST
    # =====================================================================
    print("\n" + "=" * 120)
    print("2️⃣  ITEMS WITHOUT STANDARD PRICE")
    print("=" * 120)
    
    if without_price:
        print(f"\n   {'#':<4} {'Item Code':<20} {'Item Name':<60} {'Qty':>6}")
        print("-" * 100)
        for idx, item in enumerate(without_price, 1):
            print(f"   {idx:<4} {item['item_code']:<20} {item['item_name'][:58]:<60} {item['qty']:>6}")
    else:
        print("\n   ✅ All items have standard price!")
    
    # =====================================================================
    # 3. FIND PRICES FROM 2025 QUOTATIONS
    # =====================================================================
    print("\n" + "=" * 120)
    print("3️⃣  SEARCHING PRICES IN 2025 QUOTATIONS")
    print("=" * 120)
    
    for item in without_price:
        # Get latest quotation price for this item in 2025
        qtn_prices = frappe.db.sql("""
            SELECT 
                qi.parent as quotation,
                q.party_name as customer,
                qi.rate,
                qi.qty,
                q.transaction_date,
                q.status
            FROM `tabQuotation Item` qi
            JOIN `tabQuotation` q ON q.name = qi.parent
            WHERE qi.item_code = %s
            AND q.transaction_date >= '2025-01-01'
            AND q.docstatus < 2
            ORDER BY q.transaction_date DESC
            LIMIT 5
        """, item["item_code"], as_dict=True)
        
        if qtn_prices:
            item["quotation_prices"] = []
            print(f"\n   📄 {item['item_code']}: Found in {len(qtn_prices)} quotation(s)")
            for qp in qtn_prices:
                print(f"      - {qp.quotation}: ${qp.rate:.2f} x {int(qp.qty)} ({qp.customer[:30]}) [{qp.status}]")
                item["quotation_prices"].append({
                    "quotation": qp.quotation,
                    "customer": qp.customer,
                    "rate": float(qp.rate),
                    "qty": int(qp.qty),
                    "date": str(qp.transaction_date),
                    "status": qp.status
                })
            results["prices_from_quotations"].append(item)
    
    # =====================================================================
    # 4. FIND PRICES FROM 2025 SALES ORDERS
    # =====================================================================
    print("\n" + "=" * 120)
    print("4️⃣  SEARCHING PRICES IN 2025 SALES ORDERS")
    print("=" * 120)
    
    for item in without_price:
        # Get sales order prices for this item in 2025
        so_prices = frappe.db.sql("""
            SELECT 
                soi.parent as sales_order,
                so.customer,
                soi.rate,
                soi.qty,
                so.transaction_date,
                so.status
            FROM `tabSales Order Item` soi
            JOIN `tabSales Order` so ON so.name = soi.parent
            WHERE soi.item_code = %s
            AND so.transaction_date >= '2025-01-01'
            AND so.docstatus < 2
            ORDER BY so.transaction_date DESC
            LIMIT 5
        """, item["item_code"], as_dict=True)
        
        if so_prices:
            item["so_prices"] = []
            print(f"\n   📋 {item['item_code']}: Found in {len(so_prices)} sales order(s)")
            for sp in so_prices:
                print(f"      - {sp.sales_order}: ${sp.rate:.2f} x {int(sp.qty)} ({sp.customer[:30]}) [{sp.status}]")
                item["so_prices"].append({
                    "sales_order": sp.sales_order,
                    "customer": sp.customer,
                    "rate": float(sp.rate),
                    "qty": int(sp.qty),
                    "date": str(sp.transaction_date),
                    "status": sp.status
                })
            results["prices_from_sales_orders"].append(item)
    
    # =====================================================================
    # 5. ITEMS STILL WITHOUT ANY PRICE REFERENCE
    # =====================================================================
    print("\n" + "=" * 120)
    print("5️⃣  ITEMS WITH NO PRICE ANYWHERE (Need Manual Pricing)")
    print("=" * 120)
    
    no_price_anywhere = []
    for item in without_price:
        if not item.get("quotation_prices") and not item.get("so_prices"):
            no_price_anywhere.append(item)
    
    if no_price_anywhere:
        print(f"\n   ⚠️ {len(no_price_anywhere)} items have NO price in system:")
        print(f"\n   {'#':<4} {'Item Code':<20} {'Item Name':<60} {'Qty':>6}")
        print("-" * 100)
        for idx, item in enumerate(no_price_anywhere, 1):
            print(f"   {idx:<4} {item['item_code']:<20} {item['item_name'][:58]:<60} {item['qty']:>6}")
    else:
        print("\n   ✅ All items without standard price have prices in quotations/SO!")
    
    results["no_price_anywhere"] = no_price_anywhere
    
    # =====================================================================
    # 6. PRICE SUMMARY TABLE
    # =====================================================================
    print("\n" + "=" * 120)
    print("6️⃣  PRICE SUMMARY FOR ITEMS WITH STANDARD PRICE")
    print("=" * 120)
    
    print(f"\n   {'#':<4} {'Item Code':<18} {'Item Name':<45} {'Qty':>5} {'Price':>12} {'Source':<15}")
    print("-" * 110)
    
    for idx, item in enumerate(with_price[:30], 1):  # Show first 30
        price = item['selling_price'] or item['standard_rate']
        print(f"   {idx:<4} {item['item_code']:<18} {item['item_name'][:43]:<45} {item['qty']:>5} ${price:>10.2f} {item['price_source']:<15}")
    
    if len(with_price) > 30:
        print(f"\n   ... and {len(with_price) - 30} more items with prices")
    
    # =====================================================================
    # SUMMARY
    # =====================================================================
    results["summary"] = {
        "total_items": len(items),
        "with_standard_price": len(with_price),
        "without_standard_price": len(without_price),
        "found_in_quotations": len([i for i in without_price if i.get("quotation_prices")]),
        "found_in_sales_orders": len([i for i in without_price if i.get("so_prices")]),
        "no_price_anywhere": len(no_price_anywhere)
    }
    
    print("\n" + "=" * 120)
    print("📊 SUMMARY")
    print("=" * 120)
    print(f"""
   Total items in stock:           {len(items)}
   ✅ With standard price:          {len(with_price)}
   ❌ Without standard price:       {len(without_price)}
   
   Of items without standard price:
      📄 Found in 2025 Quotations:  {results['summary']['found_in_quotations']}
      📋 Found in 2025 Sales Orders: {results['summary']['found_in_sales_orders']}
      ⚠️  NO price anywhere:         {len(no_price_anywhere)}
    """)
    
    # Save results
    with open("/tmp/price_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("   Results saved to /tmp/price_analysis_results.json")
    
    return results

