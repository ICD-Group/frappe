import frappe
import json

def run():
    """Import WhatsApp customers - Step 1: Create Customers only"""
    with open('/tmp/customers_to_create.json', 'r') as f:
        customers = json.load(f)
    
    created = 0
    skipped = 0
    failed = []
    created_data = []
    
    for c in customers:
        name = c['customer_name']
        
        if frappe.db.exists("Customer", {"customer_name": name}):
            skipped += 1
            # Still save for contact creation
            cust_name = frappe.db.get_value("Customer", {"customer_name": name}, "name")
            created_data.append({
                "customer_id": cust_name,
                "customer_name": name,
                "phone": c['phone'],
                "contact_name": c['contact_name'],
                "sales_partner": c['sales_partner']
            })
            continue
        
        try:
            doc = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": name,
                "customer_type": "Company",
                "customer_group": "Commercial",
                "territory": "Egypt",
                "sales_partner": c['sales_partner'],
                "default_sales_partner": c['sales_partner'],
                # DON'T set mobile_no here to avoid auto-contact creation
                "tax_id": "1234567",
                "default_currency": "USD",
                "default_price_list": "Standard Selling USD",
                "workflow_state": "Draft"
            })
            doc.flags.ignore_permissions = True
            doc.flags.ignore_links = True
            doc.insert()
            
            created_data.append({
                "customer_id": doc.name,
                "customer_name": name,
                "phone": c['phone'],
                "contact_name": c['contact_name'],
                "sales_partner": c['sales_partner']
            })
            created += 1
            
            if created % 20 == 0:
                frappe.db.commit()
                print(f"Progress: {created} customers created...")
                
        except Exception as e:
            failed.append({"name": name, "error": str(e)[:100]})
    
    frappe.db.commit()
    
    print(f"\n{'='*50}")
    print(f"CUSTOMERS IMPORT COMPLETE")
    print(f"{'='*50}")
    print(f"Created: {created}")
    print(f"Skipped (exist): {skipped}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("\nFailed items:")
        for f in failed[:10]:
            print(f"  - {f['name']}: {f['error']}")
    
    # Save for contact creation
    with open('/tmp/customers_for_contacts.json', 'w') as f:
        json.dump(created_data, f)
    
    print(f"\nSaved {len(created_data)} customers for contact creation")
    return created
