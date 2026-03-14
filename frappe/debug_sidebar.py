#!/usr/bin/env python3

import frappe

def execute():
    """Debug and fix sidebar categories not showing"""

    # Get the Web Page document
    doc = frappe.get_doc("Web Page", "icd-marketplace-ebay-style-it-equipment")
    content = doc.main_section

    # Add better debugging and ensure the sidebar loads properly
    debug_js = '''
// Enhanced debugging and fixed sidebar loading
console.log('Starting marketplace debugging...');

// FIXED: Load categories and brands from actual items
async function loadCategoriesAndBrands() {
    try {
        console.log('Loading categories and brands...');

        const response = await fetch('/api/method/frappe.client.get_list', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': frappe.csrf_token || ''
            },
            body: JSON.stringify({
                doctype: 'Item',
                fields: ['name', 'item_group', 'brand'],
                filters: {
                    'is_sales_item': 1,
                    'disabled': 0
                },
                limit_page_length: 9999
            })
        });

        const result = await response.json();
        console.log('API response:', result);

        const items = result.message || [];
        console.log('Items loaded:', items.length);

        marketplaceData.categories = {};
        marketplaceData.brands = {};
        marketplaceData.total = items.length;

        items.forEach(item => {
            const group = item.item_group || 'Other';
            const brand = item.brand || 'No Brand';

            marketplaceData.categories[group] = (marketplaceData.categories[group] || 0) + 1;
            marketplaceData.brands[brand] = (marketplaceData.brands[brand] || 0) + 1;
        });

        console.log('Categories found:', Object.keys(marketplaceData.categories));
        console.log('Categories data:', marketplaceData.categories);
        console.log('Brands found:', Object.keys(marketplaceData.brands));

    } catch (error) {
        console.error('Error loading categories and brands:', error);
    }
}

// FIXED: Update categories section with better error handling
function updateCategoriesSection() {
    console.log('Updating categories section...');

    const categoriesContent = document.getElementById('categoriesContent');
    console.log('Categories content element:', categoriesContent);

    if (!categoriesContent) {
        console.error('Categories content container not found!');
        // Try alternative selector
        const altContainer = document.querySelector('.sidebar-content');
        if (altContainer) {
            console.log('Found alternative container');
            altContainer.id = 'categoriesContent';
        }
        return;
    }

    // Clear existing items
    categoriesContent.innerHTML = '';

    // Check if we have categories data
    if (!marketplaceData.categories || Object.keys(marketplaceData.categories).length === 0) {
        console.log('No categories data available');
        categoriesContent.innerHTML = '<p style="color: #666; font-size: 11px; padding: 8px;">Loading categories...</p>';
        return;
    }

    // Add real categories sorted by count
    const sortedCategories = Object.entries(marketplaceData.categories)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 20); // Show top 20 categories

    console.log('Displaying categories:', sortedCategories);

    if (sortedCategories.length === 0) {
        categoriesContent.innerHTML = '<p style="color: #666; font-size: 11px; padding: 8px;">No categories found</p>';
        return;
    }

    sortedCategories.forEach(([categoryName, count], index) => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'sidebar-item-ultra';
        itemDiv.innerHTML = `
            <input type="checkbox" id="cat-${index}" data-category="${categoryName}">
            <label for="cat-${index}">${categoryName}</label>
            <span class="sidebar-count-ultra">${count}</span>
        `;
        categoriesContent.appendChild(itemDiv);

        // Add event listener
        const checkbox = itemDiv.querySelector('input');
        checkbox.addEventListener('change', loadAllProducts);
    });

    console.log('Categories section updated successfully');
}

// FIXED: Update brands section with better error handling
function updateBrandsSection() {
    console.log('Updating brands section...');

    const brandsContent = document.getElementById('brandsContent');
    console.log('Brands content element:', brandsContent);

    if (!brandsContent) {
        console.error('Brands content container not found!');
        return;
    }

    // Clear existing items
    brandsContent.innerHTML = '';

    // Check if we have brands data
    if (!marketplaceData.brands || Object.keys(marketplaceData.brands).length === 0) {
        console.log('No brands data available');
        brandsContent.innerHTML = '<p style="color: #666; font-size: 11px; padding: 8px;">Loading brands...</p>';
        return;
    }

    // Add real brands sorted by count
    const sortedBrands = Object.entries(marketplaceData.brands)
        .filter(([brandName]) => brandName !== 'No Brand') // Filter out unbranded
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15); // Show top 15 brands

    console.log('Displaying brands:', sortedBrands);

    if (sortedBrands.length === 0) {
        brandsContent.innerHTML = '<p style="color: #666; font-size: 11px; padding: 8px;">No brands found</p>';
        return;
    }

    sortedBrands.forEach(([brandName, count], index) => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'sidebar-item-ultra';
        itemDiv.innerHTML = `
            <input type="checkbox" id="brand-${index}" data-brand="${brandName}">
            <label for="brand-${index}">${brandName}</label>
            <span class="sidebar-count-ultra">${count}</span>
        `;
        brandsContent.appendChild(itemDiv);

        // Add event listener
        const checkbox = itemDiv.querySelector('input');
        checkbox.addEventListener('change', loadAllProducts);
    });

    console.log('Brands section updated successfully');
}

// Force update sidebar after a delay
setTimeout(() => {
    console.log('Force updating sidebar...');
    if (marketplaceData.categories && Object.keys(marketplaceData.categories).length > 0) {
        updateCategoriesSection();
        updateBrandsSection();
    } else {
        console.log('No data yet, trying to reload...');
        loadCategoriesAndBrands().then(() => {
            updateSidebarWithRealData();
        });
    }
}, 2000);

// Also add a manual refresh function for testing
window.refreshSidebar = function() {
    console.log('Manual sidebar refresh triggered');
    loadCategoriesAndBrands().then(() => {
        updateSidebarWithRealData();
    });
};
'''

    # Find where to insert the debug code
    script_end = content.rfind('</script>')
    if script_end != -1:
        content = content[:script_end] + debug_js + content[script_end:]

    # Make sure categories and brands sections are expanded by default
    content = content.replace('class="sidebar-content collapsed"', 'class="sidebar-content"')

    # Save the updated content
    doc.main_section = content
    doc.save()
    frappe.db.commit()

    print("✅ SIDEBAR DEBUGGING ADDED!")
    print("✅ Enhanced error handling and logging")
    print("✅ Force refresh after 2 seconds")
    print("✅ Manual refresh function: refreshSidebar()")
    print("✅ Sections expanded by default")
    print("✅ Better fallback handling")

if __name__ == "__main__":
    execute()