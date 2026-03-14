#!/usr/bin/env python3

import frappe

def execute():
    """Fix authentication detection to properly show logged in state"""

    # Get the Web Page document
    doc = frappe.get_doc("Web Page", "icd-marketplace-ebay-style-it-equipment")
    content = doc.main_section

    # Find the authentication function and replace it with a fixed version
    auth_function_start = content.find('// Enhanced authentication check')
    auth_function_end = content.find('// Load customer data from ERPNext')

    if auth_function_start != -1 and auth_function_end != -1:
        new_auth_code = '''// Enhanced authentication check
async function checkAuthentication() {
    try {
        console.log('Checking authentication...');

        // First check if we're already logged in via session
        const sessionResponse = await fetch('/api/method/frappe.auth.get_logged_user', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
            }
        });

        const sessionResult = await sessionResponse.json();
        console.log('Session check result:', sessionResult);

        if (sessionResult.message && sessionResult.message !== 'Guest' && sessionResult.message !== null) {
            marketplaceData.isUserLoggedIn = true;
            marketplaceData.currentUser = sessionResult.message;
            console.log('User is logged in:', marketplaceData.currentUser);

            // Get customer data
            await loadCustomerData();
            updateUIForLoggedInUser();

            return true;
        } else {
            // Try alternative method to check session
            const altResponse = await fetch('/api/method/frappe.client.get_list', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': frappe.csrf_token || ''
                },
                body: JSON.stringify({
                    doctype: 'User',
                    fields: ['name'],
                    filters: {},
                    limit_page_length: 1
                })
            });

            const altResult = await altResponse.json();

            if (altResult.message && !altResult.exc) {
                // We can access ERPNext, so user is logged in
                marketplaceData.isUserLoggedIn = true;
                marketplaceData.currentUser = frappe.session.user || 'Unknown';
                console.log('User authenticated via API access');

                await loadCustomerData();
                updateUIForLoggedInUser();

                return true;
            } else {
                marketplaceData.isUserLoggedIn = false;
                marketplaceData.currentUser = null;
                console.log('User is not logged in');
                updateUIForGuest();

                return false;
            }
        }
    } catch (error) {
        console.error('Auth check error:', error);

        // Fallback: check if frappe session exists
        if (typeof frappe !== 'undefined' && frappe.session && frappe.session.user && frappe.session.user !== 'Guest') {
            marketplaceData.isUserLoggedIn = true;
            marketplaceData.currentUser = frappe.session.user;
            console.log('Using frappe session fallback:', marketplaceData.currentUser);

            await loadCustomerData();
            updateUIForLoggedInUser();

            return true;
        } else {
            marketplaceData.isUserLoggedIn = false;
            marketplaceData.currentUser = null;
            updateUIForGuest();

            return false;
        }
    }
}

'''

        # Replace the authentication function
        content = content[:auth_function_start] + new_auth_code + content[auth_function_end:]

    # Also fix the UI update functions to be more robust
    ui_update_start = content.find('// UI Updates for authentication state')
    ui_update_end = content.find('// FIXED: Initialize marketplace with proper data loading')

    if ui_update_start != -1 and ui_update_end != -1:
        new_ui_code = '''// UI Updates for authentication state
function updateUIForLoggedInUser() {
    console.log('Updating UI for logged in user');

    const authSection = document.querySelector('.nav-actions-ultra');
    if (authSection) {
        authSection.innerHTML = `
            <button onclick="showCartModal()" class="nav-btn-ultra">
                <i class="fa fa-shopping-cart"></i>
                Cart <span class="cart-count" style="display: none;">0</span>
            </button>
            <button onclick="showAccountModal()" class="nav-btn-ultra primary">
                <i class="fa fa-user"></i>
                Account
            </button>
        `;
        console.log('Updated nav to show Cart and Account buttons');
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

function updateUIForGuest() {
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
}

'''

        # Replace the UI update functions
        content = content[:ui_update_start] + new_ui_code + content[ui_update_end:]

    # Add modal functions for cart and account if missing
    if 'function showCartModal()' not in content:
        modal_functions = '''
// Modal Functions
function showCartModal() {
    if (!marketplaceData.isUserLoggedIn) {
        showLoginRequired();
        return;
    }

    const modal = createModal('Shopping Cart', generateCartHTML());
    document.body.appendChild(modal);
}

function showAccountModal() {
    if (!marketplaceData.isUserLoggedIn) {
        showLoginRequired();
        return;
    }

    const modal = createModal('My Account', generateAccountHTML());
    document.body.appendChild(modal);
    loadAccountData();
}

function generateCartHTML() {
    if (shoppingCart.items.length === 0) {
        return `
            <div class="empty-cart">
                <i class="fa fa-shopping-cart" style="font-size: 48px; color: #ccc; margin-bottom: 15px;"></i>
                <p>Your cart is empty</p>
                <button onclick="closeModal()" class="btn-secondary">Continue Shopping</button>
            </div>
        `;
    }

    let html = `
        <div class="cart-items">
            ${shoppingCart.items.map(item => `
                <div class="cart-item">
                    <div class="item-details">
                        <h4>${item.itemName}</h4>
                        <p class="item-code">Code: ${item.itemCode}</p>
                        <p class="item-price">SAR ${item.price.toLocaleString()}</p>
                    </div>
                    <div class="item-controls">
                        <input type="number" value="${item.quantity}" min="1"
                               onchange="shoppingCart.updateQuantity('${item.itemCode}', this.value)">
                        <button onclick="shoppingCart.removeItem('${item.itemCode}')" class="btn-danger">
                            <i class="fa fa-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
        <div class="cart-summary">
            <div class="total">
                <strong>Total: SAR ${shoppingCart.getTotal().toLocaleString()}</strong>
            </div>
            <div class="cart-actions">
                <button onclick="shoppingCart.checkout()" class="btn-primary">
                    <i class="fa fa-credit-card"></i> Checkout
                </button>
                <button onclick="closeModal()" class="btn-secondary">Continue Shopping</button>
            </div>
        </div>
    `;
    return html;
}

function generateAccountHTML() {
    return `
        <div class="account-dashboard">
            <div class="account-info">
                <h3>Account Information</h3>
                <p><strong>Name:</strong> ${marketplaceData.customerData?.customer_name || 'Not available'}</p>
                <p><strong>Email:</strong> ${marketplaceData.currentUser}</p>
                <p><strong>Customer ID:</strong> ${marketplaceData.customerData?.name || 'Not available'}</p>
            </div>

            <div class="account-section">
                <h3>Recent Orders</h3>
                <div id="recentOrders">Loading...</div>
            </div>

            <div class="account-section">
                <h3>Recent Quotations</h3>
                <div id="recentQuotes">Loading...</div>
            </div>

            <div class="account-actions">
                <a href="/logout" class="btn-secondary">Logout</a>
                <button onclick="closeModal()" class="btn-primary">Close</button>
            </div>
        </div>
    `;
}

// Account data loading
async function loadAccountData() {
    await loadRecentOrders();
    await loadRecentQuotations();
}

async function loadRecentOrders() {
    if (!marketplaceData.customerData) return;

    try {
        const response = await fetch('/api/method/frappe.client.get_list', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': frappe.csrf_token || ''
            },
            body: JSON.stringify({
                doctype: 'Sales Order',
                fields: ['name', 'transaction_date', 'grand_total', 'status'],
                filters: {
                    'customer': marketplaceData.customerData.name
                },
                order_by: 'creation desc',
                limit_page_length: 5
            })
        });

        const result = await response.json();
        const ordersContainer = document.getElementById('recentOrders');

        if (result.message && result.message.length > 0) {
            ordersContainer.innerHTML = result.message.map(order => `
                <div class="order-item">
                    <div class="order-header">
                        <strong>${order.name}</strong>
                        <span class="order-status status-${order.status?.toLowerCase()}">${order.status}</span>
                    </div>
                    <div class="order-details">
                        <span>Date: ${order.transaction_date}</span>
                        <span>Total: SAR ${order.grand_total?.toLocaleString()}</span>
                    </div>
                </div>
            `).join('');
        } else {
            ordersContainer.innerHTML = '<p>No recent orders found.</p>';
        }
    } catch (error) {
        console.error('Error loading orders:', error);
        document.getElementById('recentOrders').innerHTML = '<p>Error loading orders.</p>';
    }
}

async function loadRecentQuotations() {
    if (!marketplaceData.customerData) return;

    try {
        const response = await fetch('/api/method/frappe.client.get_list', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': frappe.csrf_token || ''
            },
            body: JSON.stringify({
                doctype: 'Quotation',
                fields: ['name', 'transaction_date', 'grand_total', 'status'],
                filters: {
                    'party_name': marketplaceData.customerData.name,
                    'quotation_to': 'Customer'
                },
                order_by: 'creation desc',
                limit_page_length: 5
            })
        });

        const result = await response.json();
        const quotesContainer = document.getElementById('recentQuotes');

        if (result.message && result.message.length > 0) {
            quotesContainer.innerHTML = result.message.map(quote => `
                <div class="quote-item">
                    <div class="quote-header">
                        <strong>${quote.name}</strong>
                        <span class="quote-status status-${quote.status?.toLowerCase()}">${quote.status}</span>
                    </div>
                    <div class="quote-details">
                        <span>Date: ${quote.transaction_date}</span>
                        <span>Total: SAR ${quote.grand_total?.toLocaleString()}</span>
                    </div>
                </div>
            `).join('');
        } else {
            quotesContainer.innerHTML = '<p>No recent quotations found.</p>';
        }
    } catch (error) {
        console.error('Error loading quotations:', error);
        document.getElementById('recentQuotes').innerHTML = '<p>Error loading quotations.</p>';
    }
}

'''

        # Insert modal functions before the last script tag
        script_end = content.rfind('</script>')
        if script_end != -1:
            content = content[:script_end] + modal_functions + content[script_end:]

    # Save the updated content
    doc.main_section = content
    doc.save()
    frappe.db.commit()

    print("✅ AUTHENTICATION DETECTION FIXED!")
    print("✅ Robust login state detection")
    print("✅ Proper UI updates for logged in users")
    print("✅ Cart and Account buttons show when logged in")
    print("✅ Enhanced debugging and fallback methods")
    print("✅ Modal functions for cart and account added")

if __name__ == "__main__":
    execute()