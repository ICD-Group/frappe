#!/usr/bin/env python3

import frappe

def execute():
    """Fix the brands section that wasn't updated"""

    # Get the Web Page document
    doc = frappe.get_doc("Web Page", "icd-marketplace-ebay-style-it-equipment")
    content = doc.main_section

    # Get actual brand data from the database
    items = frappe.get_list('Item',
        fields=['name', 'brand'],
        filters={
            'is_sales_item': 1,
            'disabled': 0
        },
        limit_page_length=1000
    )

    # Count brands
    brands = {}
    for item in items:
        brand = item.get('brand') or 'No Brand'
        brands[brand] = brands.get(brand, 0) + 1

    # Create static HTML for brands based on real data
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

    # Find and replace the brands content
    old_brands_placeholder = '''<div class="sidebar-content" id="brandsContent">
                <!-- Dynamic brands will be loaded here -->
            </div>'''

    new_brands_content = f'''<div class="sidebar-content" id="brandsContent">
                {brands_html}
            </div>'''

    content = content.replace(old_brands_placeholder, new_brands_content)

    # Also check for the collapsed version
    old_brands_collapsed = '''<div class="sidebar-content collapsed" id="brandsContent">
                <!-- Dynamic brands will be loaded here -->
            </div>'''

    new_brands_collapsed = f'''<div class="sidebar-content" id="brandsContent">
                {brands_html}
            </div>'''

    content = content.replace(old_brands_collapsed, new_brands_collapsed)

    # Save the updated content
    doc.main_section = content
    doc.save()
    frappe.db.commit()

    print("✅ BRANDS SECTION FIXED!")
    print(f"✅ Added {len(sorted_brands)} brands to sidebar")
    print("✅ Brands section now has static data")

    # Print the brands for verification
    print("\n🏷️ Brands added:")
    for brand, count in sorted_brands:
        print(f"  - {brand}: {count} items")

if __name__ == "__main__":
    execute()