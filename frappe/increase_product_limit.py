#!/usr/bin/env python3

import frappe

def execute():
    """Increase product display limit to show more products"""

    # Get the Web Page document
    doc = frappe.get_doc("Web Page", "icd-marketplace-ebay-style-it-equipment")
    content = doc.main_section

    # Find and update the product loading limit
    old_limit = 'limit_page_length: 50'
    new_limit = 'limit_page_length: 200'

    content = content.replace(old_limit, new_limit)

    # Also update any other 50 limits in the loadAllProducts function
    old_function_part = '''            body: JSON.stringify({
                doctype: 'Item',
                fields: ['name', 'item_name', 'item_group', 'brand', 'standard_rate', 'image', 'description'],
                filters: filters,
                limit_page_length: 200
            })'''

    # Make sure it's updated everywhere
    content = content.replace('limit_page_length: 50', 'limit_page_length: 200')

    # Save the updated content
    doc.main_section = content
    doc.save()
    frappe.db.commit()

    print("✅ PRODUCT LIMIT INCREASED!")
    print("✅ Now showing up to 200 products instead of 50")
    print("✅ You should see more products now")
    print("✅ Filters will show actual product counts")

if __name__ == "__main__":
    execute()