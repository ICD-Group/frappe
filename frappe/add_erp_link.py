#!/usr/bin/env python3

import frappe

def execute():
    """Add simple ERP System link for logged-in users"""

    # Get the Web Page document
    doc = frappe.get_doc("Web Page", "icd-marketplace-ebay-style-it-equipment")
    content = doc.main_section

    # Find the updateUIForLoggedInUser function and make it simple
    ui_update_start = content.find('function updateUIForLoggedInUser() {')
    ui_update_end = content.find('function updateUIForGuest() {')

    if ui_update_start != -1 and ui_update_end != -1:
        new_logged_in_ui = '''function updateUIForLoggedInUser() {
    console.log('Updating UI for logged in user');

    const authSection = document.querySelector('.nav-actions-ultra');
    if (authSection) {
        authSection.innerHTML = `
            <button onclick="shoppingCart.addAllToCart()" class="nav-btn-ultra">
                <i class="fa fa-shopping-cart"></i>
                Cart <span class="cart-count" style="display: none;">0</span>
            </button>
            <a href="https://erp.icloudist.com/app" target="_blank" class="nav-btn-ultra primary">
                <i class="fa fa-external-link-alt"></i>
                ERP System
            </a>
        `;
        console.log('Updated nav to show Cart and ERP System link');
    } else {
        console.log('Nav actions section not found');
    }

    shoppingCart.updateCartDisplay();

    // Also update any login-specific elements
    const loginButtons = document.querySelectorAll('a[href="/login"]');
    loginButtons.forEach(btn => {
        btn.style.display = 'none';
    });
}

'''

        # Replace the function
        content = content[:ui_update_start] + new_logged_in_ui + content[ui_update_end:]

    # Also simplify the cart functionality - just show items count and simple modal
    if 'function showCartModal()' in content:
        cart_modal_start = content.find('function showCartModal() {')
        cart_modal_end = content.find('function showAccountModal() {')

        if cart_modal_start != -1 and cart_modal_end != -1:
            simple_cart_modal = '''function showCartModal() {
    if (!marketplaceData.isUserLoggedIn) {
        showLoginRequired();
        return;
    }

    const cartCount = shoppingCart.getItemCount();
    const cartTotal = shoppingCart.getTotal();

    const modal = createModal('Shopping Cart', `
        <div class="simple-cart">
            <div class="cart-summary">
                <h3>Cart Summary</h3>
                <p><strong>Items:</strong> ${cartCount}</p>
                <p><strong>Total:</strong> SAR ${cartTotal.toLocaleString()}</p>
            </div>
            <div class="cart-actions">
                <a href="https://erp.icloudist.com/app" target="_blank" class="btn-primary">
                    <i class="fa fa-external-link-alt"></i> Go to ERP System
                </a>
                <button onclick="closeModal()" class="btn-secondary">Close</button>
            </div>
        </div>
    `);
    document.body.appendChild(modal);
}

'''
            content = content[:cart_modal_start] + simple_cart_modal + content[cart_modal_end:]

    # Remove the complex account modal and other unnecessary functions
    functions_to_remove = [
        'function showAccountModal()',
        'function generateCartHTML()',
        'function generateAccountHTML()',
        'function loadAccountData()',
        'function loadRecentOrders()',
        'function loadRecentQuotations()'
    ]

    for func_name in functions_to_remove:
        func_start = content.find(func_name)
        if func_start != -1:
            # Find the end of the function
            brace_count = 0
            start_brace_found = False
            func_end = func_start

            for i in range(func_start, len(content)):
                if content[i] == '{':
                    start_brace_found = True
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if start_brace_found and brace_count == 0:
                        func_end = i + 1
                        break

            # Find the next function start
            next_func_start = content.find('function ', func_end)
            if next_func_start != -1:
                func_end = next_func_start

            # Remove the function
            content = content[:func_start] + content[func_end:]

    # Save the updated content
    doc.main_section = content
    doc.save()
    frappe.db.commit()

    print("✅ SIMPLIFIED UI WITH ERP SYSTEM LINK!")
    print("✅ Cart button shows item count")
    print("✅ ERP System button opens https://erp.icloudist.com/app")
    print("✅ Removed complex modals - keeping it simple")
    print("✅ Clean and logical user experience")

if __name__ == "__main__":
    execute()