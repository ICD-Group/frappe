#!/usr/bin/env python3

import frappe

def execute():
    """Check if sidebar data exists in the web page"""

    doc = frappe.get_doc("Web Page", "icd-marketplace-ebay-style-it-equipment")
    content = doc.main_section

    # Check what's in the sidebar
    has_dell = "Dell 10K SAS HDD" in content
    has_hpe = "HPE" in content
    has_categories_content = "categoriesContent" in content
    has_brands_content = "brandsContent" in content

    print("\n✅ CHECKING SIDEBAR STATUS:")
    print(f"Has 'Dell 10K SAS HDD' in sidebar: {has_dell}")
    print(f"Has 'HPE' brand in sidebar: {has_hpe}")
    print(f"Has categoriesContent div: {has_categories_content}")
    print(f"Has brandsContent div: {has_brands_content}")

    # Find what's actually in the categories section
    start = content.find('<div class="sidebar-content" id="categoriesContent">')
    if start != -1:
        end = content.find('</div>', start)
        categories_section = content[start:end+6]
        print("\n📂 Categories Section Content:")
        if len(categories_section) < 300:
            print(categories_section)
        else:
            print(categories_section[:300] + "...")
    else:
        print("\n❌ Categories content div not found!")

    # Find what's actually in the brands section
    start = content.find('<div class="sidebar-content" id="brandsContent">')
    if start == -1:
        start = content.find('<div class="sidebar-content collapsed" id="brandsContent">')

    if start != -1:
        end = content.find('</div>', start)
        brands_section = content[start:end+6]
        print("\n🏷️ Brands Section Content:")
        if len(brands_section) < 300:
            print(brands_section)
        else:
            print(brands_section[:300] + "...")
    else:
        print("\n❌ Brands content div not found!")

if __name__ == "__main__":
    execute()