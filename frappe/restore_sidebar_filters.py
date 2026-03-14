#!/usr/bin/env python3

import frappe

def execute():
    """Restore sidebar filters and ensure they work after sign in"""

    # Get the Web Page document
    doc = frappe.get_doc("Web Page", "icd-marketplace-ebay-style-it-equipment")
    content = doc.main_section

    # Make sure we have the sidebar HTML structure in place
    if 'id="categoriesSection"' not in content:
        # Find where to insert the sidebar
        sidebar_location = content.find('<!-- Enhanced Left Sidebar -->')
        if sidebar_location == -1:
            sidebar_location = content.find('<aside class="sidebar-ultra">')

        if sidebar_location != -1:
            # Find the end of the existing sidebar
            sidebar_end = content.find('</aside>', sidebar_location) + len('</aside>')

            # Replace with proper sidebar structure
            new_sidebar = '''    <!-- Enhanced Left Sidebar -->
    <aside class="sidebar-ultra">
        <!-- Smart Search Section -->
        <div class="sidebar-section-ultra">
            <h3 class="sidebar-title-ultra">Search</h3>
            <div class="sidebar-search-box">
                <input type="text" id="sidebarSearch" placeholder="Search products..." onkeyup="smartSearch(this.value)">
                <button onclick="smartSearch(document.getElementById('sidebarSearch').value)">
                    <i class="fa fa-search"></i>
                </button>
            </div>
        </div>

        <!-- Categories Section -->
        <div class="sidebar-section-ultra" id="categoriesSection">
            <h3 class="sidebar-title-ultra">
                Categories
                <button class="expand-btn" onclick="toggleSection('categories')" id="catExpandBtn">
                    <i class="fa fa-chevron-down"></i>
                </button>
            </h3>
            <div class="sidebar-content" id="categoriesContent">
                <!-- Dynamic categories will be loaded here -->
            </div>
        </div>

        <!-- Brands Section -->
        <div class="sidebar-section-ultra" id="brandsSection">
            <h3 class="sidebar-title-ultra">
                Brands
                <button class="expand-btn" onclick="toggleSection('brands')" id="brandExpandBtn">
                    <i class="fa fa-chevron-down"></i>
                </button>
            </h3>
            <div class="sidebar-content collapsed" id="brandsContent">
                <!-- Dynamic brands will be loaded here -->
            </div>
        </div>

        <!-- Price Range Section -->
        <div class="sidebar-section-ultra">
            <h3 class="sidebar-title-ultra">
                Price (SAR)
                <button class="expand-btn" onclick="toggleSection('price')" id="priceExpandBtn">
                    <i class="fa fa-chevron-down"></i>
                </button>
            </h3>
            <div class="sidebar-content collapsed" id="priceContent">
                <div class="sidebar-item-ultra">
                    <input type="checkbox" id="price-0-1000" data-price="0-1000">
                    <label for="price-0-1000">Under SAR 1,000</label>
                    <span class="sidebar-count-ultra">0</span>
                </div>
                <div class="sidebar-item-ultra">
                    <input type="checkbox" id="price-1000-5000" data-price="1000-5000">
                    <label for="price-1000-5000">SAR 1,000 - 5,000</label>
                    <span class="sidebar-count-ultra">0</span>
                </div>
                <div class="sidebar-item-ultra">
                    <input type="checkbox" id="price-5000-15000" data-price="5000-15000">
                    <label for="price-5000-15000">SAR 5,000 - 15,000</label>
                    <span class="sidebar-count-ultra">0</span>
                </div>
                <div class="sidebar-item-ultra">
                    <input type="checkbox" id="price-15000-plus" data-price="15000+">
                    <label for="price-15000-plus">SAR 15,000+</label>
                    <span class="sidebar-count-ultra">0</span>
                </div>
            </div>
        </div>

        <!-- Clear Filters -->
        <div class="sidebar-section-ultra">
            <button onclick="clearAllFilters()" class="clear-filters-btn">
                <i class="fa fa-times"></i> Clear All Filters
            </button>
        </div>

        <!-- Active Filters Display -->
        <div class="sidebar-section-ultra" id="activeFiltersSection" style="display: none;">
            <h3 class="sidebar-title-ultra">Active Filters</h3>
            <div id="activeFiltersList"></div>
        </div>
    </aside>'''

            content = content[:sidebar_location] + new_sidebar + content[sidebar_end:]

    # Make sure the initialization calls the sidebar update
    init_start = content.find('async function initializeMarketplace() {')
    init_end = content.find('async function loadItemGroups() {')

    if init_start != -1 and init_end != -1:
        new_init = '''async function initializeMarketplace() {
    try {
        console.log('Initializing marketplace...');

        // Show loading in results area
        updateResultsCount(0, 'Loading...');

        // Load real item groups from ERPNext
        await loadItemGroups();

        // Load categories and brands data
        await loadCategoriesAndBrands();

        // Update sidebar with loaded data
        updateSidebarWithRealData();

        // Load and display initial products
        await loadAllProducts();

        // Update UI elements
        updateUI();

        console.log('Marketplace initialized successfully');

    } catch (error) {
        console.error('Error initializing marketplace:', error);
        showToast('Error loading marketplace data', 'error');
    }
}

'''
        content = content[:init_start] + new_init + content[init_end:]

    # Ensure the categories section update function exists and works
    if 'function updateCategoriesSection()' not in content:
        categories_function = '''
// Update categories section
function updateCategoriesSection() {
    const categoriesSection = document.getElementById('categoriesSection');
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
}

// Update brands section
function updateBrandsSection() {
    const brandsSection = document.getElementById('brandsSection');
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
}

// Toggle sidebar sections
function toggleSection(sectionName) {
    const content = document.getElementById(sectionName + 'Content');
    const btn = document.getElementById(sectionName + 'ExpandBtn');

    if (content && btn) {
        content.classList.toggle('collapsed');
        btn.querySelector('i').classList.toggle('fa-chevron-down');
        btn.querySelector('i').classList.toggle('fa-chevron-up');
    }
}

'''

        # Insert before the last script tag
        script_end = content.rfind('</script>')
        if script_end != -1:
            content = content[:script_end] + categories_function + content[script_end:]

    # Make sure the DOM loaded event also calls the sidebar initialization
    dom_loaded_start = content.find("document.addEventListener('DOMContentLoaded', async function() {")
    if dom_loaded_start != -1:
        dom_loaded_end = content.find('});', dom_loaded_start) + 3

        new_dom_loaded = '''document.addEventListener('DOMContentLoaded', async function() {
    console.log('DOM loaded, starting initialization...');

    // Check authentication first
    await checkAuthentication();

    // Initialize marketplace data and sidebar
    await initializeMarketplace();

    console.log('Page initialization complete');
});'''

        content = content[:dom_loaded_start] + new_dom_loaded + content[dom_loaded_end:]

    # Save the updated content
    doc.main_section = content
    doc.save()
    frappe.db.commit()

    print("✅ SIDEBAR FILTERS RESTORED!")
    print("✅ Categories section with real item groups")
    print("✅ Brands section with real brands")
    print("✅ Price filters")
    print("✅ Search functionality")
    print("✅ Expandable/collapsible sections")
    print("✅ Clear filters button")
    print("✅ Proper initialization after login")

if __name__ == "__main__":
    execute()