#!/usr/bin/env python3

import frappe

def execute():
    """Simple direct approach to show categories in sidebar"""

    # Get the Web Page document
    doc = frappe.get_doc("Web Page", "icd-marketplace-ebay-style-it-equipment")
    content = doc.main_section

    # Get actual data from the database to populate sidebar directly
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

    # Create static HTML for categories based on real data
    categories_html = ''
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:15]

    for i, (cat_name, count) in enumerate(sorted_categories):
        categories_html += f'''
            <div class="sidebar-item-ultra">
                <input type="checkbox" id="cat-{i}" data-category="{cat_name}">
                <label for="cat-{i}">{cat_name}</label>
                <span class="sidebar-count-ultra">{count}</span>
            </div>'''

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

    # Replace the dynamic content placeholders with static HTML
    old_categories_content = '''            <div class="sidebar-content" id="categoriesContent">
                <!-- Dynamic categories will be loaded here -->
            </div>'''

    new_categories_content = f'''            <div class="sidebar-content" id="categoriesContent">
                {categories_html}
            </div>'''

    content = content.replace(old_categories_content, new_categories_content)

    old_brands_content = '''            <div class="sidebar-content collapsed" id="brandsContent">
                <!-- Dynamic brands will be loaded here -->
            </div>'''

    new_brands_content = f'''            <div class="sidebar-content" id="brandsContent">
                {brands_html}
            </div>'''

    content = content.replace(old_brands_content, new_brands_content)

    # Add simple JavaScript for filtering
    simple_js = '''
// Simple filtering functionality
function filterByCategory(categoryName, isChecked) {
    console.log('Filtering by category:', categoryName, isChecked);
    loadAllProducts();
}

function filterByBrand(brandName, isChecked) {
    console.log('Filtering by brand:', brandName, isChecked);
    loadAllProducts();
}

// Add event listeners to checkboxes
document.addEventListener('DOMContentLoaded', function() {
    // Category checkboxes
    document.querySelectorAll('[data-category]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            filterByCategory(this.dataset.category, this.checked);
        });
    });

    // Brand checkboxes
    document.querySelectorAll('[data-brand]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            filterByBrand(this.dataset.brand, this.checked);
        });
    });

    console.log('✅ Sidebar filters initialized with static data');
    console.log('✅ Categories loaded:', document.querySelectorAll('[data-category]').length);
    console.log('✅ Brands loaded:', document.querySelectorAll('[data-brand]').length);
});
'''

    # Add the simple JS before the last script tag
    script_end = content.rfind('</script>')
    if script_end != -1:
        content = content[:script_end] + simple_js + content[script_end:]

    # Save the updated content
    doc.main_section = content
    doc.save()
    frappe.db.commit()

    print("✅ STATIC SIDEBAR CREATED!")
    print(f"✅ Added {len(sorted_categories)} categories directly to HTML")
    print(f"✅ Added {len(sorted_brands)} brands directly to HTML")
    print("✅ Simple event listeners for filtering")
    print("✅ No more API calls needed for sidebar")

    # Print some of the data for verification
    print("\n📂 Categories loaded:")
    for cat, count in sorted_categories[:5]:
        print(f"  - {cat}: {count} items")

    print("\n🏷️ Brands loaded:")
    for brand, count in sorted_brands[:5]:
        print(f"  - {brand}: {count} items")

if __name__ == "__main__":
    execute()