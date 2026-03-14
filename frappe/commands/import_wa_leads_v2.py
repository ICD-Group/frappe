import frappe
import json

def run():
    """Import WhatsApp leads - Step 3: Create Leads

    GENIUS FIX: Temporarily disable auto_creation_of_contact to avoid Contact creation errors
    """

    # Step 1: Disable auto_creation_of_contact
    print("Step 1: Disabling auto_creation_of_contact...")
    original_value = frappe.db.get_single_value("CRM Settings", "auto_creation_of_contact")
    frappe.db.set_value("CRM Settings", "CRM Settings", "auto_creation_of_contact", 0)
    frappe.db.commit()
    print(f"  Original value: {original_value}, Now: 0")

    try:
        # Step 2: Load leads data
        with open('/tmp/leads_to_create.json', 'r') as f:
            leads = json.load(f)

        print(f"\nStep 2: Creating {len(leads)} Leads...")

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
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else "WA"  # Default "WA" if no last name

            try:
                doc = frappe.get_doc({
                    "doctype": "Lead",
                    "first_name": first_name,
                    "last_name": last_name,
                    "lead_name": lead_name or f"WA-{phone}",
                    "mobile_no": phone,
                    "source": "WhatsApp",
                    "status": "Lead",
                    "sales_partner": sales_partner,
                    "company": "ICD",
                    "territory": "Egypt"
                })
                doc.flags.ignore_permissions = True
                doc.flags.ignore_links = True
                doc.flags.ignore_mandatory = True
                doc.insert()

                created += 1

                if created % 50 == 0:
                    frappe.db.commit()
                    print(f"  Progress: {created} leads created...")

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

    finally:
        # Step 3: Re-enable auto_creation_of_contact
        print(f"\nStep 3: Re-enabling auto_creation_of_contact...")
        frappe.db.set_value("CRM Settings", "CRM Settings", "auto_creation_of_contact", original_value)
        frappe.db.commit()
        print(f"  Restored to: {original_value}")

    return created
