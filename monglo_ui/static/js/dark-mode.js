/**
 * Dark Mode Toggle - Monglo Admin
 * Handles dark mode switching with localStorage persistence
 */

class DarkModeToggle {
    constructor() {
        this.storageKey = 'monglo-dark-mode';
        this.init();
    }

    init() {
        // Load saved preference
        const savedMode = localStorage.getItem(this.storageKey);
        if (savedMode === 'dark') {
            this.enableDarkMode(false);
        }

        // Create toggle button
        this.createToggleButton();
    }

    createToggleButton() {
        const toggle = document.createElement('button');
        toggle.className = 'monglo-btn monglo-btn-secondary monglo-btn-sm';
        toggle.id = 'dark-mode-toggle';
        toggle.innerHTML = `
      <i class="fas fa-moon"></i>
    `;
        toggle.title = 'Toggle Dark Mode';
        toggle.addEventListener('click', () => this.toggle());

        // Insert into header actions
        const actions = document.querySelector('.monglo-actions');
        if (actions) {
            actions.insertBefore(toggle, actions.firstChild);
        }

        this.toggleButton = toggle;
    }

    toggle() {
        if (document.body.classList.contains('dark-mode')) {
            this.disableDarkMode();
        } else {
            this.enableDarkMode(true);
        }
    }

    enableDarkMode(save = true) {
        document.body.classList.add('dark-mode');
        if (this.toggleButton) {
            this.toggleButton.innerHTML = '<i class="fas fa-sun"></i>';
            this.toggleButton.title = 'Toggle Light Mode';
        }
        if (save) {
            localStorage.setItem(this.storageKey, 'dark');
        }
    }

    disableDarkMode() {
        document.body.classList.remove('dark-mode');
        if (this.toggleButton) {
            this.toggleButton.innerHTML = '<i class="fas fa-moon"></i>';
            this.toggleButton.title = 'Toggle Dark Mode';
        }
        localStorage.setItem(this.storageKey, 'light');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.darkModeToggle = new DarkModeToggle();
});
