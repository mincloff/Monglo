/**
 * Sidebar Resizer - Monglo Admin
 * Allows dragging to resize the sidebar width
 */

class SidebarResizer {
    constructor() {
        this.sidebar = document.querySelector('.monglo-sidebar');
        this.minWidth = 200;
        this.maxWidth = 500;
        this.storageKey = 'monglo-sidebar-width';
        this.isDragging = false;

        if (this.sidebar) {
            this.init();
        }
    }

    init() {
        // Load saved width
        const savedWidth = localStorage.getItem(this.storageKey);
        if (savedWidth) {
            this.sidebar.style.width = savedWidth + 'px';
        }

        // Create resizer handle
        this.createResizer();
    }

    createResizer() {
        const resizer = document.createElement('div');
        resizer.className = 'monglo-sidebar-resizer';
        this.sidebar.appendChild(resizer);
        this.resizer = resizer;

        // Mouse events
        resizer.addEventListener('mousedown', (e) => this.startResize(e));
        document.addEventListener('mousemove', (e) => this.resize(e));
        document.addEventListener('mouseup', () => this.stopResize());
    }

    startResize(e) {
        this.isDragging = true;
        this.resizer.classList.add('resizing');
        document.body.style.cursor = 'ew-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault();
    }

    resize(e) {
        if (!this.isDragging) return;

        const newWidth = e.clientX;

        // Enforce min/max constraints
        if (newWidth >= this.minWidth && newWidth <= this.maxWidth) {
            this.sidebar.style.width = newWidth + 'px';
        }
    }

    stopResize() {
        if (!this.isDragging) return;

        this.isDragging = false;
        this.resizer.classList.remove('resizing');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';

        // Save to localStorage
        const width = parseInt(this.sidebar.style.width);
        localStorage.setItem(this.storageKey, width);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.sidebarResizer = new SidebarResizer();
});
