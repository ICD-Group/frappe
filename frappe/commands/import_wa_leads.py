import frappe
import json

def run():
    """Import WhatsApp leads - Step 3: Create Leads"""
    with open('/tmp/leads_to_create.json', 'r') as f:
        leads = json.load(f)
    
    created = 0
    skipped = 0
    failed = []
    
    for lead in leads:
        phone = lead['phone']
        lead_name = lead['lead_name']
        sales_partner = lead['sales_partner']
        
        # Check if lead already exists with this phone
        existing = frappe.db.exists("Lead", {"mobile_no": phone})
        if existing:
            skipped += 1
            continue
        
        # Parse name for first/last name
        name_parts = lead_name.split() if lead_name else [f"WA-{phone}"]
        first_name = name_parts[0] if name_parts else f"WA-{phone}"
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        try:
            doc = frappe.get_doc({
                "doctype": "Lead",
                "first_name": first_name,
                "last_name": last_name,
                "lead_name": lead_name,
                "mobile_no": phone,
                "source": "WhatsApp",
                "status": "Lead",
                "sales_partner": sales_partner,
                "company": "ICD",
                "territory": "Egypt"
            })
            doc.flags.ignore_permissions = True
            doc.flags.ignore_links = True
            doc.insert()
            
            created += 1
            
            if created % 50 == 0:
                frappe.db.commit()
                print(f"Progress: {created} leads created...")
                
        except Exception as e:
            failed.append({"name": lead_name, "phone": phone, "error": str(e)[:100]})
    
    frappe.db.commit()
    
    print(f"\n{'='*50}")
    print(f"LEADS IMPORT COMPLETE")
    print(f"{'='*50}")
    print(f"Created: {created}")
    print(f"Skipped (exist): {skipped}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("\nFailed items:")
        for f in failed[:10]:
            print(f"  - {f['name']} ({f['phone']}): {f['error']}")
    
    return created
