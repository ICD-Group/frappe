#!/usr/bin/env python3

import frappe

def execute():
    """Fix logout URL to use proper ERPNext logout"""

    # Get the Web Page document
    doc = frappe.get_doc("Web Page", "icd-marketplace-ebay-style-it-equipment")
    content = doc.main_section

    # Update the logout URL in the logged in UI function
    old_logout = 'href="/logout"'
    new_logout = 'href="https://erp.icloudist.com/?cmd=web_logout"'

    content = content.replace(old_logout, new_logout)

    # Also make sure it redirects properly after logout
    ui_update_start = content.find('function updateUIForLoggedInUser() {')
    ui_update_end = content.find('function updateUIForGuest() {')

    if ui_update_start != -1 and ui_update_end != -1:
        new_logged_in_ui = '''function updateUIForLoggedInUser() {
    console.log('Updating UI for logged in user');

    const authSection = document.querySelector('.nav-actions-ultra');
    if (authSection) {
        authSection.innerHTML = `
            <button onclick="showCartSummary()" class="nav-btn-ultra">
                <i class="fa fa-shopping-cart"></i>
                Cart <span class="cart-count" style="display: none;">0</span>
            </button>
            <a href="https://erp.icloudist.com/app" target="_blank" class="nav-btn-ultra">
                <i class="fa fa-external-link-alt"></i>
                ERP System
            </a>
            <a href="https://erp.icloudist.com/?cmd=web_logout" class="nav-btn-ultra primary">
                <i class="fa fa-sign-out-alt"></i>
                Sign Out
            </a>
        `;
        console.log('Updated nav to show Cart, ERP System, and Sign Out with proper logout URL');
    } else {
        console.log('Nav actions section not found');
    }

    shoppingCart.updateCartDisplay();

    // Hide login/signup elements when logged in
    const loginButtons = document.querySelectorAll('a[href="/login"], a[href*="signup"]');
    loginButtons.forEach(btn => {
        btn.style.display = 'none';
    });
}

'''

        # Replace the function
        content = content[:ui_update_start] + new_logged_in_ui + content[ui_update_end:]

    # Save the updated content
    doc.main_section = content
    doc.save()
    frappe.db.commit()

    print("✅ LOGOUT URL FIXED!")
    print("✅ Sign Out now uses: https://erp.icloudist.com/?cmd=web_logout")
    print("✅ Proper ERPNext logout functionality")
    print("✅ Clean logout process")

if __name__ == "__main__":
    execute()