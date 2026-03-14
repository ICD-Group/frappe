import frappe

def run():
    """Delete 79 wrong Customers and their linked Contacts"""

    # List of 79 wrong customer names
    wrong_customers = [
        '"A"', 'A7zema', 'Abd Alrahman Shafey.', 'Ahmed', 'Ahmed Ali',
        'Ahmed Fekry', 'Ahmed Mousa EGY', 'Ahmed Tahon', 'Ahmed Thabet Product Manager BC',
        'Ahmedabdelshafy', 'Ali Ebrahim', 'Amr', 'Amr Mohamed', 'arabbusiness84',
        'Ashraf', 'Aya Khaled Direct', 'Diaa Abdelaziz', 'Dina Dfd', 'Emad Soliman',
        'esamh228', 'Eslam mandrawy', 'Esraa', 'fatmaedries58', 'gabrmohammed433',
        'Hager', 'HATEM KASSEM', 'Haytham Ðash', 'Hend Ataya', 'Hussein',
        'Hussein Shehab', 'Ibrahim Nour', 'kaboza', 'kareem nady', 'Mahmoud Elhosieny',
        'Maisara Magdy', 'mansuorseneg', 'Marina Magdy', 'Masrawy', 'medoayad78',
        'mina melad', 'Moghazy Dream', 'Moh Hamdy', 'Mohamed Aboulfarag', 'Mohamed Eid Dell',
        'Mohamed El akhras', 'Mohamed Gad Elmawla', 'Mohamed Hammam', 'Mohamed mostafa',
        'Mohamed Salih', 'mohamedosamaguda', 'montassermomen36', 'Mostafa', 'Mostafa Essam',
        'Mostafa Omar', 'Moustafa Mahmoud', 'mramadan skytech', 'Muhammad Zain',
        'Nabil Tharwat', 'nada', 'Omar Mekky', 'popelnet gad', 'Rehab Gamal',
        'Ruby Reda', 'Salma Khaled Nabawy', 'Sayed Sabry', 'Shaban.4.tech', 'Sharif',
        'Tony', 'wifitotallynetworking', 'Yehia Badr', 'yossef medhat hassen', 'Z3dni',
        'الحمد لله', 'الله كريم', 'بطارية و شاحن', 'حسام حبيشى hossam hebishy',
        'عماد سلامه', 'لاب توب', 'محمد حسين عبدالرحمن'
    ]

    print(f"Starting deletion of {len(wrong_customers)} wrong Customers and Contacts...")
    print("="*60)

    contacts_deleted = 0
    customers_deleted = 0
    failed = []

    for customer_name in wrong_customers:
        try:
            # Step 1: Find and delete linked Contact
            # Contacts are linked via Dynamic Link table
            contact_links = frappe.db.sql("""
                SELECT dl.parent
                FROM `tabDynamic Link` dl
                WHERE dl.link_doctype = 'Customer'
                AND dl.link_name = %s
                AND dl.parenttype = 'Contact'
            """, (customer_name,), as_dict=True)

            for link in contact_links:
                contact_name = link.parent
                try:
                    # Delete Dynamic Link first
                    frappe.db.sql("""
                        DELETE FROM `tabDynamic Link`
                        WHERE parent = %s AND parenttype = 'Contact'
                    """, (contact_name,))

                    # Delete Contact
                    frappe.delete_doc("Contact", contact_name, force=True, ignore_permissions=True)
                    contacts_deleted += 1
                except Exception as e:
                    pass  # Contact might already be deleted

            # Step 2: Delete Customer
            if frappe.db.exists("Customer", customer_name):
                frappe.delete_doc("Customer", customer_name, force=True, ignore_permissions=True)
                customers_deleted += 1

                if customers_deleted % 20 == 0:
                    frappe.db.commit()
                    print(f"  Progress: {customers_deleted} customers deleted...")

        except Exception as e:
            failed.append({"name": customer_name, "error": str(e)[:100]})

    frappe.db.commit()

    print(f"\n{'='*60}")
    print(f"DELETION COMPLETE")
    print(f"{'='*60}")
    print(f"Contacts deleted: {contacts_deleted}")
    print(f"Customers deleted: {customers_deleted}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\nFailed items:")
        for f in failed[:10]:
            print(f"  - {f['name']}: {f['error']}")

    return customers_deleted
