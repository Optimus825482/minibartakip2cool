/**
 * Gelişmiş Tablo Arama, Filtreleme ve Sıralama Sistemi
 * Responsive tasarım ve tema uyumluluğu ile
 */

class TableSearchFilter {
    constructor(options) {
        this.tableId = options.tableId;
        this.searchInputId = options.searchInputId;
        this.filters = options.filters || [];
        this.sortable = options.sortable !== false;
        this.itemsPerPageOptions = options.itemsPerPageOptions || [10, 25, 50, 100];
        this.defaultItemsPerPage = options.defaultItemsPerPage || 25;
        this.noResultsMessage = options.noResultsMessage || 'Sonuç bulunamadı';
        this.searchPlaceholder = options.searchPlaceholder || 'Ara...';
        
        this.table = document.getElementById(this.tableId);
        this.tbody = this.table.querySelector('tbody');
        this.originalRows = Array.from(this.tbody.querySelectorAll('tr'));
        this.filteredRows = [...this.originalRows];
        
        this.currentPage = 1;
        this.itemsPerPage = this.defaultItemsPerPage;
        this.sortColumn = -1;
        this.sortDirection = 'asc';
        this.searchTerm = '';
        this.activeFilters = {};
        
        this.init();
    }
    
    init() {
        this.createSearchBar();
        if (this.filters.length > 0) {
            this.createFilterBar();
        }
        if (this.sortable) {
            this.addSortableHeaders();
        }
        this.createPagination();
        this.updateDisplay();
    }
    
    createSearchBar() {
        const searchContainer = document.createElement('div');
        searchContainer.className = 'mb-4 flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between';
        searchContainer.innerHTML = `
            <div class="relative flex-1 w-full sm:max-w-md">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg class="h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                </div>
                <input type="text" 
                       id="${this.searchInputId}"
                       class="block w-full pl-10 pr-3 py-2 border border-slate-300 rounded-lg 
                              focus:ring-2 focus:ring-slate-500 focus:border-slate-500 
                              text-sm placeholder-slate-400 transition-all"
                       placeholder="${this.searchPlaceholder}">
                <div id="${this.searchInputId}-clear" 
                     class="absolute inset-y-0 right-0 pr-3 flex items-center cursor-pointer hidden">
                    <svg class="h-5 w-5 text-slate-400 hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </div>
            </div>
            <div class="flex items-center gap-2 w-full sm:w-auto">
                <span class="text-sm text-slate-600 whitespace-nowrap">Sayfa başına:</span>
                <select id="${this.tableId}-per-page" 
                        class="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-slate-500 focus:border-slate-500">
                    ${this.itemsPerPageOptions.map(opt => 
                        `<option value="${opt}" ${opt === this.defaultItemsPerPage ? 'selected' : ''}>${opt}</option>`
                    ).join('')}
                </select>
            </div>
        `;
        
        this.table.parentElement.insertBefore(searchContainer, this.table);
        
        // Arama input event listener
        const searchInput = document.getElementById(this.searchInputId);
        const clearBtn = document.getElementById(`${this.searchInputId}-clear`);
        
        searchInput.addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase().trim();
            clearBtn.classList.toggle('hidden', !this.searchTerm);
            this.applyFiltersAndSearch();
        });
        
        clearBtn.addEventListener('click', () => {
            searchInput.value = '';
            this.searchTerm = '';
            clearBtn.classList.add('hidden');
            this.applyFiltersAndSearch();
        });
        
        // Items per page değişimi
        document.getElementById(`${this.tableId}-per-page`).addEventListener('change', (e) => {
            this.itemsPerPage = parseInt(e.target.value);
            this.currentPage = 1;
            this.updateDisplay();
        });
    }
    
    createFilterBar() {
        const filterContainer = document.createElement('div');
        filterContainer.className = 'mb-4 p-4 bg-slate-50 rounded-lg border border-slate-200';
        filterContainer.innerHTML = `
            <div class="flex flex-wrap items-center gap-3">
                <div class="flex items-center gap-2">
                    <svg class="h-5 w-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
                    </svg>
                    <span class="text-sm font-medium text-slate-700">Filtreler:</span>
                </div>
                <div class="flex flex-wrap items-center gap-2 flex-1">
                    ${this.filters.map(filter => this.createFilterElement(filter)).join('')}
                </div>
                <button id="${this.tableId}-clear-filters" 
                        class="text-sm text-slate-600 hover:text-slate-900 font-medium px-3 py-1 rounded-md hover:bg-slate-200 transition-colors whitespace-nowrap">
                    Filtreleri Temizle
                </button>
            </div>
            <div id="${this.tableId}-active-filters" class="mt-3 flex flex-wrap gap-2 hidden"></div>
        `;
        
        this.table.parentElement.insertBefore(filterContainer, this.table);
        
        // Filter event listeners
        this.filters.forEach(filter => {
            const filterElement = document.getElementById(`${this.tableId}-filter-${filter.column}`);
            filterElement.addEventListener('change', (e) => {
                const value = e.target.value;
                if (value) {
                    this.activeFilters[filter.column] = value;
                } else {
                    delete this.activeFilters[filter.column];
                }
                this.updateActiveFilterBadges();
                this.applyFiltersAndSearch();
            });
        });
        
        // Clear filters button
        document.getElementById(`${this.tableId}-clear-filters`).addEventListener('click', () => {
            this.clearAllFilters();
        });
    }
    
    createFilterElement(filter) {
        const filterId = `${this.tableId}-filter-${filter.column}`;
        return `
            <select id="${filterId}" 
                    class="border border-slate-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-slate-500 focus:border-slate-500 bg-white">
                <option value="">${filter.label}</option>
                ${filter.options.map(opt => 
                    `<option value="${opt.value}">${opt.label}</option>`
                ).join('')}
            </select>
        `;
    }
    
    updateActiveFilterBadges() {
        const container = document.getElementById(`${this.tableId}-active-filters`);
        if (Object.keys(this.activeFilters).length === 0) {
            container.classList.add('hidden');
            return;
        }
        
        container.classList.remove('hidden');
        container.innerHTML = Object.entries(this.activeFilters).map(([column, value]) => {
            const filter = this.filters.find(f => f.column == column);
            const option = filter.options.find(o => o.value === value);
            return `
                <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-600 text-white">
                    <span>${filter.label}: ${option.label}</span>
                    <button onclick="tableSearchFilter_${this.tableId}.removeFilter(${column})" 
                            class="hover:bg-slate-700 rounded-full p-0.5">
                        <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </span>
            `;
        }).join('');
    }
    
    removeFilter(column) {
        delete this.activeFilters[column];
        document.getElementById(`${this.tableId}-filter-${column}`).value = '';
        this.updateActiveFilterBadges();
        this.applyFiltersAndSearch();
    }
    
    clearAllFilters() {
        this.activeFilters = {};
        this.filters.forEach(filter => {
            document.getElementById(`${this.tableId}-filter-${filter.column}`).value = '';
        });
        this.updateActiveFilterBadges();
        this.applyFiltersAndSearch();
    }
    
    addSortableHeaders() {
        const headers = this.table.querySelectorAll('thead th');
        headers.forEach((header, index) => {
            if (header.classList.contains('no-sort')) return;
            
            header.classList.add('cursor-pointer', 'select-none', 'hover:bg-slate-100', 'transition-colors', 'group');
            header.style.position = 'relative';
            
            const sortIcon = document.createElement('span');
            sortIcon.className = 'ml-1 inline-block opacity-0 group-hover:opacity-50 transition-opacity';
            sortIcon.innerHTML = `
                <svg class="h-4 w-4 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"></path>
                </svg>
            `;
            header.appendChild(sortIcon);
            
            header.addEventListener('click', () => {
                this.sortTable(index);
            });
        });
    }
    
    sortTable(columnIndex) {
        if (this.sortColumn === columnIndex) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = columnIndex;
            this.sortDirection = 'asc';
        }
        
        // Update header icons
        const headers = this.table.querySelectorAll('thead th');
        headers.forEach((header, index) => {
            const icon = header.querySelector('span svg');
            if (!icon) return;
            
            if (index === columnIndex) {
                icon.parentElement.classList.remove('opacity-0', 'group-hover:opacity-50');
                icon.parentElement.classList.add('opacity-100');
                
                if (this.sortDirection === 'asc') {
                    icon.innerHTML = `
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M5 15l7-7 7 7"></path>
                    `;
                } else {
                    icon.innerHTML = `
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M19 9l-7 7-7-7"></path>
                    `;
                }
            } else {
                icon.parentElement.classList.add('opacity-0', 'group-hover:opacity-50');
                icon.parentElement.classList.remove('opacity-100');
                icon.innerHTML = `
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"></path>
                `;
            }
        });
        
        this.filteredRows.sort((a, b) => {
            const aVal = a.cells[columnIndex]?.textContent.trim().toLowerCase() || '';
            const bVal = b.cells[columnIndex]?.textContent.trim().toLowerCase() || '';
            
            // Sayısal karşılaştırma
            const aNum = parseFloat(aVal.replace(/[^\d.-]/g, ''));
            const bNum = parseFloat(bVal.replace(/[^\d.-]/g, ''));
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return this.sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
            }
            
            // Alfabetik karşılaştırma
            if (this.sortDirection === 'asc') {
                return aVal.localeCompare(bVal, 'tr');
            } else {
                return bVal.localeCompare(aVal, 'tr');
            }
        });
        
        this.currentPage = 1;
        this.updateDisplay();
    }
    
    applyFiltersAndSearch() {
        this.filteredRows = this.originalRows.filter(row => {
            // Arama filtresi
            if (this.searchTerm) {
                const rowText = row.textContent.toLowerCase();
                if (!rowText.includes(this.searchTerm)) {
                    return false;
                }
            }
            
            // Diğer filtreler
            for (const [column, value] of Object.entries(this.activeFilters)) {
                const cellText = row.cells[column]?.textContent.trim().toLowerCase() || '';
                const filterValue = value.toLowerCase();
                
                if (!cellText.includes(filterValue)) {
                    return false;
                }
            }
            
            return true;
        });
        
        this.currentPage = 1;
        this.updateDisplay();
    }
    
    createPagination() {
        const paginationContainer = document.createElement('div');
        paginationContainer.id = `${this.tableId}-pagination`;
        paginationContainer.className = 'mt-4 flex flex-col sm:flex-row items-center justify-between gap-4';
        this.table.parentElement.appendChild(paginationContainer);
    }
    
    updateDisplay() {
        const start = (this.currentPage - 1) * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        const totalPages = Math.ceil(this.filteredRows.length / this.itemsPerPage);
        
        // Tüm satırları gizle
        this.originalRows.forEach(row => row.style.display = 'none');
        
        // Sadece mevcut sayfadaki satırları göster
        const rowsToShow = this.filteredRows.slice(start, end);
        rowsToShow.forEach(row => row.style.display = '');
        
        // No results message
        this.showNoResults(this.filteredRows.length === 0);
        
        // Pagination güncelle
        this.updatePagination(totalPages);
        
        // Stats güncelle
        this.updateStats();
    }
    
    showNoResults(show) {
        let noResultsRow = this.tbody.querySelector('.no-results-row');
        
        if (show) {
            if (!noResultsRow) {
                noResultsRow = document.createElement('tr');
                noResultsRow.className = 'no-results-row';
                noResultsRow.innerHTML = `
                    <td colspan="100" class="px-6 py-12 text-center">
                        <svg class="mx-auto h-12 w-12 text-slate-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                  d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 12h.01M12 12h.01M12 12h.01M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <p class="text-slate-600 font-medium">${this.noResultsMessage}</p>
                        <p class="text-slate-500 text-sm mt-2">Farklı arama kriterleri veya filtreler deneyin.</p>
                    </td>
                `;
                this.tbody.appendChild(noResultsRow);
            }
            noResultsRow.style.display = '';
        } else {
            if (noResultsRow) {
                noResultsRow.style.display = 'none';
            }
        }
    }
    
    updatePagination(totalPages) {
        const container = document.getElementById(`${this.tableId}-pagination`);
        
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        const createButton = (page, text, disabled = false) => {
            return `
                <button onclick="tableSearchFilter_${this.tableId}.goToPage(${page})"
                        class="px-3 py-2 text-sm font-medium rounded-md transition-colors
                               ${disabled ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 
                                 page === this.currentPage ? 'bg-slate-600 text-white' : 
                                 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-300'}"
                        ${disabled ? 'disabled' : ''}>
                    ${text}
                </button>
            `;
        };
        
        let buttons = [];
        
        // Previous button
        buttons.push(createButton(this.currentPage - 1, '←', this.currentPage === 1));
        
        // Page numbers
        const maxButtons = 7;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxButtons / 2));
        let endPage = Math.min(totalPages, startPage + maxButtons - 1);
        
        if (endPage - startPage < maxButtons - 1) {
            startPage = Math.max(1, endPage - maxButtons + 1);
        }
        
        if (startPage > 1) {
            buttons.push(createButton(1, '1'));
            if (startPage > 2) {
                buttons.push('<span class="px-2 py-2 text-slate-500">...</span>');
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            buttons.push(createButton(i, i.toString()));
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                buttons.push('<span class="px-2 py-2 text-slate-500">...</span>');
            }
            buttons.push(createButton(totalPages, totalPages.toString()));
        }
        
        // Next button
        buttons.push(createButton(this.currentPage + 1, '→', this.currentPage === totalPages));
        
        container.innerHTML = `
            <div class="text-sm text-slate-700">
                <span class="font-medium">${this.filteredRows.length}</span> kayıttan 
                <span class="font-medium">${(this.currentPage - 1) * this.itemsPerPage + 1}</span> - 
                <span class="font-medium">${Math.min(this.currentPage * this.itemsPerPage, this.filteredRows.length)}</span> 
                arası gösteriliyor
            </div>
            <div class="flex flex-wrap items-center gap-1">
                ${buttons.join('')}
            </div>
        `;
    }
    
    updateStats() {
        // İstatistikleri güncelle (eğer varsa)
        const statsElements = document.querySelectorAll(`[data-stats-for="${this.tableId}"]`);
        statsElements.forEach(el => {
            const stat = el.dataset.stat;
            if (stat === 'total') {
                el.textContent = this.originalRows.length;
            } else if (stat === 'filtered') {
                el.textContent = this.filteredRows.length;
            }
        });
    }
    
    goToPage(page) {
        const totalPages = Math.ceil(this.filteredRows.length / this.itemsPerPage);
        if (page < 1 || page > totalPages) return;
        this.currentPage = page;
        this.updateDisplay();
        
        // Sayfanın en üstüne kaydır (smooth scroll)
        this.table.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Global instance holder
window.tableSearchFilterInstances = window.tableSearchFilterInstances || {};
