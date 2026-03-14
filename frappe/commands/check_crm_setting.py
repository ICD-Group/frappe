import frappe

def run():
    """Check CRM Settings auto_creation_of_contact"""
    value = frappe.db.get_single_value("CRM Settings", "auto_creation_of_contact")
    print(f"auto_creation_of_contact = {value}")
    return value
