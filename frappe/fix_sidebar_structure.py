#!/usr/bin/env python3

import frappe

def execute():
    """Fix sidebar structure to properly display categories and brands"""

    # Get the Web Page document
    doc = frappe.get_doc("Web Page", "icd-marketplace-ebay-style-it-equipment")
    content = doc.main_section

    # Find and fix the updateCategoriesSection function
    old_categories_function = '''// FIXED: Update categories section
function updateCategoriesSection() {
    const categoriesSection = document.getElementById('categoriesSection');
    if (!categoriesSection) {
        console.log('Categories section not found');
        return;
    }

    // Clear existing items except title
    const existingItems = categoriesSection.querySelectorAll('.sidebar-item-ultra');
    existingItems.forEach(item => item.remove());

    // Add real categories sorted by count
    const sortedCategories = Object.entries(marketplaceData.categories)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15); // Show top 15 categories

    console.log('Adding categories to sidebar:', sortedCategories.length);

    sortedCategories.forEach(([categoryName, count], index) => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'sidebar-item-ultra';
        itemDiv.innerHTML = `
            <input type="checkbox" id="cat-${index}" data-category="${categoryName}">
            <label for="cat-${index}">${categoryName}</label>
            <span class="sidebar-count-ultra">${count}</span>
        `;
        categoriesSection.appendChild(itemDiv);

        // Add event listener
        const checkbox = itemDiv.querySelector('input');
        checkbox.addEventListener('change', loadAllProducts);
    });
}'''

    new_categories_function = '''// FIXED: Update categories section
function updateCategoriesSection() {
    const categoriesContent = document.getElementById('categoriesContent');
    if (!categoriesContent) {
        console.log('Categories content container not found');
        return;
    }

    // Clear existing items
    categoriesContent.innerHTML = '';

    // Add real categories sorted by count
    const sortedCategories = Object.entries(marketplaceData.categories)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15); // Show top 15 categories

    console.log('Adding categories to sidebar:', sortedCategories.length);

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
}'''

    # Replace the function
    content = content.replace(old_categories_function, new_categories_function)

    # Find and fix the updateBrandsSection function
    old_brands_function = '''// FIXED: Update brands section
function updateBrandsSection() {
    const brandsSection = document.getElementById('brandsSection');
    if (!brandsSection) {
        console.log('Brands section not found');
        return;
    }

    // Clear existing items except title
    const existingItems = brandsSection.querySelectorAll('.sidebar-item-ultra');
    existingItems.forEach(item => item.remove());

    // Add real brands sorted by count
    const sortedBrands = Object.entries(marketplaceData.brands)
        .filter(([brandName]) => brandName !== 'No Brand') // Filter out unbranded
        .sort((a, b) => b[1] - a[1])
        .slice(0, 12); // Show top 12 brands

    console.log('Adding brands to sidebar:', sortedBrands.length);

    sortedBrands.forEach(([brandName, count], index) => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'sidebar-item-ultra';
        itemDiv.innerHTML = `
            <input type="checkbox" id="brand-${index}" data-brand="${brandName}">
            <label for="brand-${index}">${brandName}</label>
            <span class="sidebar-count-ultra">${count}</span>
        `;
        brandsSection.appendChild(itemDiv);

        // Add event listener
        const checkbox = itemDiv.querySelector('input');
        checkbox.addEventListener('change', loadAllProducts);
    });
}'''

    new_brands_function = '''// FIXED: Update brands section
function updateBrandsSection() {
    const brandsContent = document.getElementById('brandsContent');
    if (!brandsContent) {
        console.log('Brands content container not found');
        return;
    }

    // Clear existing items
    brandsContent.innerHTML = '';

    // Add real brands sorted by count
    const sortedBrands = Object.entries(marketplaceData.brands)
        .filter(([brandName]) => brandName !== 'No Brand') // Filter out unbranded
        .sort((a, b) => b[1] - a[1])
        .slice(0, 12); // Show top 12 brands

    console.log('Adding brands to sidebar:', sortedBrands.length);

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
}'''

    # Replace the function
    content = content.replace(old_brands_function, new_brands_function)

    # Add toggle section function if missing
    if 'function toggleSection(' not in content:
        toggle_function = '''
// Toggle sidebar sections
function toggleSection(sectionName) {
    const content = document.getElementById(sectionName + 'Content');
    const btn = document.getElementById(sectionName + 'ExpandBtn');

    if (content && btn) {
        content.classList.toggle('collapsed');
        btn.classList.toggle('expanded');

        const icon = btn.querySelector('i');
        if (icon) {
            icon.classList.toggle('fa-chevron-down');
            icon.classList.toggle('fa-chevron-up');
        }
    }
}
'''

        # Insert before the last script tag
        script_end = content.rfind('</script>')
        if script_end != -1:
            content = content[:script_end] + toggle_function + content[script_end:]

    # Fix the products display container
    if 'id="productsContainer"' not in content:
        # Find the products grid and add the container
        old_products_grid = '<div class="products-grid" id="productsGrid">'
        new_products_grid = '''<div id="productsContainer">
            <div class="products-grid" id="productsGrid">'''

        content = content.replace(old_products_grid, new_products_grid)

        # Also close the container
        content = content.replace('</div>\n    </div>\n</div>', '</div>\n        </div>\n    </div>\n</div>')

    # Fix the displayProducts function to use the right container
    old_display = '''function displayProducts(products) {
    const productsContainer = document.getElementById('productsContainer');
    if (!productsContainer) {
        console.log('Products container not found');
        return;
    }'''

    new_display = '''function displayProducts(products) {
    const productsGrid = document.getElementById('productsGrid');
    if (!productsGrid) {
        console.log('Products grid not found');
        return;
    }'''

    content = content.replace(old_display, new_display)
    content = content.replace('productsContainer.innerHTML = ', 'productsGrid.innerHTML = ')

    # Save the updated content
    doc.main_section = content
    doc.save()
    frappe.db.commit()

    print("✅ SIDEBAR STRUCTURE FIXED!")
    print("✅ Categories now append to categoriesContent")
    print("✅ Brands now append to brandsContent")
    print("✅ Toggle functionality added")
    print("✅ Products display container fixed")
    print("✅ Proper DOM targeting implemented")

if __name__ == "__main__":
    execute()