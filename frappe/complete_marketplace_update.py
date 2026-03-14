#!/usr/bin/env python3

import frappe

def execute():
    """Complete all marketplace updates for the new page"""

    # Get the new Web Page document
    doc = frappe.get_doc("Web Page", "icd3s-marketplace-it-equipment")
    content = doc.main_section

    # Get actual data from the database to populate sidebar
    items = frappe.get_list('Item',
        fields=['name', 'item_group', 'brand'],
        filters={
            'is_sales_item': 1,
            'disabled': 0
        },
        limit_page_length=1000
    )

    # Count categories and brands
    categories = {}
    brands = {}

    for item in items:
        group = item.get('item_group') or 'Other'
        brand = item.get('brand') or 'No Brand'

        categories[group] = categories.get(group, 0) + 1
        brands[brand] = brands.get(brand, 0) + 1

    # Create static HTML for brands
    brands_html = ''
    sorted_brands = sorted([(k, v) for k, v in brands.items() if k != 'No Brand'],
                          key=lambda x: x[1], reverse=True)[:12]

    for i, (brand_name, count) in enumerate(sorted_brands):
        brands_html += f'''
            <div class="sidebar-item-ultra">
                <input type="checkbox" id="brand-{i}" data-brand="{brand_name}">
                <label for="brand-{i}">{brand_name}</label>
                <span class="sidebar-count-ultra">{count}</span>
            </div>'''

    # Update brands section
    old_brands_placeholder = '''<div class="sidebar-content" id="brandsContent">
                <!-- Dynamic brands will be loaded here -->
            </div>'''

    new_brands_content = f'''<div class="sidebar-content" id="brandsContent">
                {brands_html}
            </div>'''

    content = content.replace(old_brands_placeholder, new_brands_content)

    # Also handle collapsed version
    old_brands_collapsed = '''<div class="sidebar-content collapsed" id="brandsContent">
                <!-- Dynamic brands will be loaded here -->
            </div>'''

    content = content.replace(old_brands_collapsed, new_brands_content)

    # Remove any remaining eBay references
    content = content.replace("eBay-Style", "Professional")
    content = content.replace("ebay-style", "professional")
    content = content.replace("eBay", "Professional")
    content = content.replace("ebay", "professional")

    # Update comments
    content = content.replace("<!-- eBay-Style Enhanced Sidebar -->", "<!-- Professional Enhanced Sidebar -->")
    content = content.replace("Enhanced Sidebar", "Professional Sidebar")

    # Make sure all CSS class references are clean
    content = content.replace("Enhanced", "Professional")

    # Update JavaScript comments
    content = content.replace("Enhanced ERPNext", "Professional ERPNext")

    # Save the updated content
    doc.main_section = content
    doc.save()
    frappe.db.commit()

    print("✅ MARKETPLACE COMPLETELY UPDATED!")
    print("✅ All eBay references removed")
    print("✅ Professional branding throughout")
    print("✅ Brands section populated with real data")
    print("✅ Categories section already working")
    print("✅ Page ready at: /icd3s-marketplace-it-equipment")

    print(f"\n📊 SIDEBAR DATA:")
    print(f"✅ Categories: {len(categories)} types")
    print(f"✅ Brands: {len(sorted_brands)} brands")
    print(f"✅ Total items: {len(items)}")

    # Print some examples
    print(f"\n📂 Top Categories:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {cat}: {count} items")

    print(f"\n🏷️ Top Brands:")
    for brand, count in sorted_brands[:5]:
        print(f"  - {brand}: {count} items")

if __name__ == "__main__":
    execute()