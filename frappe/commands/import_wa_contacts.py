import frappe
import json

def run():
    """Import WhatsApp contacts - Step 2: Create Contacts linked to Customers"""
    with open('/tmp/customers_for_contacts.json', 'r') as f:
        customers = json.load(f)
    
    created = 0
    skipped = 0
    failed = []
    
    for c in customers:
        customer_id = c['customer_id']
        customer_name = c['customer_name']
        phone = c['phone']
        contact_name = c['contact_name']
        sales_partner = c['sales_partner']
        
        # Check if contact already exists for this customer
        existing = frappe.db.exists("Dynamic Link", {
            "link_doctype": "Customer",
            "link_name": customer_id,
            "parenttype": "Contact"
        })
        
        if existing:
            skipped += 1
            continue
        
        # Parse contact name for first/last name
        name_parts = contact_name.split() if contact_name else [customer_name]
        first_name = name_parts[0] if name_parts else customer_name
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else "WA"
        
        # Create placeholder email
        email = f"tbd-{phone}@update.required"
        
        try:
            doc = frappe.get_doc({
                "doctype": "Contact",
                "first_name": first_name,
                "last_name": last_name,
                "mobile_no": phone,
                "sales_partner": sales_partner,
                "email_ids": [{"email_id": email, "is_primary": 1}],
                "phone_nos": [{"phone": phone, "is_primary_mobile_no": 1}],
                "links": [{"link_doctype": "Customer", "link_name": customer_id}],
                "is_primary_contact": 1
            })
            doc.flags.ignore_permissions = True
            doc.flags.ignore_links = True
            doc.insert()
            
            # Update customer with primary contact
            frappe.db.set_value("Customer", customer_id, "customer_primary_contact", doc.name)
            
            created += 1
            
            if created % 20 == 0:
                frappe.db.commit()
                print(f"Progress: {created} contacts created...")
                
        except Exception as e:
            failed.append({"name": contact_name, "customer": customer_name, "error": str(e)[:100]})
    
    frappe.db.commit()
    
    print(f"\n{'='*50}")
    print(f"CONTACTS IMPORT COMPLETE")
    print(f"{'='*50}")
    print(f"Created: {created}")
    print(f"Skipped (exist): {skipped}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("\nFailed items:")
        for f in failed[:10]:
            print(f"  - {f['name']} ({f['customer']}): {f['error']}")
    
    return created
