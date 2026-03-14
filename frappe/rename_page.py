#!/usr/bin/env python3

import frappe

def execute():
    """Rename the web page to remove eBay reference"""

    # Get the current Web Page document
    old_doc = frappe.get_doc("Web Page", "icd-marketplace-ebay-style-it-equipment")

    # Create a new web page with proper name
    new_doc = frappe.new_doc("Web Page")
    new_doc.title = "ICD3S Mission-Critical IT Infrastructure Marketplace"
    new_doc.page_name = "icd3s-marketplace-it-equipment"
    new_doc.published = 1
    new_doc.main_section = old_doc.main_section
    new_doc.meta_title = "ICD3S Mission-Critical IT Equipment | Enterprise Hardware Solutions"
    new_doc.meta_description = "ICD3S Mission-Critical IT Infrastructure - Professional IT Equipment Marketplace for Enterprise Solutions"

    # Remove any eBay references from the content
    content = new_doc.main_section
    content = content.replace("eBay-Style", "Professional")
    content = content.replace("ebay-style", "professional")
    content = content.replace("eBay", "Professional")
    content = content.replace("ebay", "professional")

    new_doc.main_section = content

    # Save the new document
    new_doc.insert()
    frappe.db.commit()

    # Delete the old document
    old_doc.delete()
    frappe.db.commit()

    print("✅ PAGE RENAMED SUCCESSFULLY!")
    print("✅ Old name: icd-marketplace-ebay-style-it-equipment")
    print("✅ New name: icd3s-marketplace-it-equipment")
    print("✅ Title: ICD3S Mission-Critical IT Infrastructure Marketplace")
    print("✅ Removed all eBay references from content")
    print("✅ Page is published and ready")

if __name__ == "__main__":
    execute()