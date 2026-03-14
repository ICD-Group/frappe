#!/usr/bin/env python3

import frappe

def execute():
    """Fix Sign Out button to show when logged in"""

    # Get the Web Page document
    doc = frappe.get_doc("Web Page", "icd-marketplace-ebay-style-it-equipment")
    content = doc.main_section

    # Update the logged in UI to include Sign Out
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
            <a href="/logout" class="nav-btn-ultra primary">
                <i class="fa fa-sign-out-alt"></i>
                Sign Out
            </a>
        `;
        console.log('Updated nav to show Cart, ERP System, and Sign Out');
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

    # Update the guest UI to show Sign Up and Login
    guest_ui_start = content.find('function updateUIForGuest() {')
    guest_ui_end = content.find('// FIXED: Initialize marketplace with proper data loading')

    if guest_ui_start != -1 and guest_ui_end != -1:
        new_guest_ui = '''function updateUIForGuest() {
    console.log('Updating UI for guest user');

    const authSection = document.querySelector('.nav-actions-ultra');
    if (authSection) {
        authSection.innerHTML = `
            <a href="/login" class="nav-btn-ultra">
                <i class="fa fa-sign-in-alt"></i>
                Login
            </a>
            <a href="mailto:sales@icd3s.com" class="nav-btn-ultra primary">
                <i class="fa fa-envelope"></i>
                Get Quote
            </a>
        `;
        console.log('Updated nav to show Login and Get Quote buttons');
    } else {
        console.log('Nav actions section not found');
    }

    // Show login/signup elements for guests
    const hiddenElements = document.querySelectorAll('a[href="/login"], a[href*="signup"]');
    hiddenElements.forEach(el => {
        el.style.display = '';
    });
}

'''

        # Replace the guest UI function
        content = content[:guest_ui_start] + new_guest_ui + content[guest_ui_end:]

    # Rename the cart modal function to be simpler
    if 'function showCartModal()' in content:
        content = content.replace('function showCartModal()', 'function showCartSummary()')
        content = content.replace('onclick="showCartModal()"', 'onclick="showCartSummary()"')

    # Save the updated content
    doc.main_section = content
    doc.save()
    frappe.db.commit()

    print("✅ SIGN OUT FUNCTIONALITY FIXED!")
    print("✅ When logged in: Cart | ERP System | Sign Out")
    print("✅ When logged out: Login | Get Quote")
    print("✅ Proper logout link to /logout")
    print("✅ Clean and logical navigation")

if __name__ == "__main__":
    execute()