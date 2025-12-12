/**
 * Create Modal - Monglo Admin
 * Dynamic form for creating new documents
 */

class CreateModal {
    constructor() {
        this.modal = null;
        this.currentCollection = null;
        this.detectedFields = null;
    }

    async open(collection) {
        this.currentCollection = collection;

        // Detect fields from existing documents
        await this.detectFields();

        this.createModal();
        this.populateForm();
    }

    async detectFields() {
        try {
            // Fetch sample documents to detect common fields
            const response = await fetch(`/api/admin/${this.currentCollection}?per_page=5`);
            const result = await response.json();
            const items = result.items || [];

            if (items.length > 0) {
                // Merge all field names from samples
                const fieldSet = new Set();
                items.forEach(item => {
                    Object.keys(item).forEach(key => {
                        if (key !== '_id') fieldSet.add(key);
                    });
                });

                // Detect types from first document
                this.detectedFields = {};
                const sample = items[0];
                fieldSet.forEach(field => {
                    this.detectedFields[field] = this.detectFieldType(sample[field]);
                });
            } else {
                // No documents exist, start with empty fields
                this.detectedFields = {};
            }
        } catch (error) {
            console.error('Error detecting fields:', error);
            this.detectedFields = {};
        }
    }

    detectFieldType(value) {
        if (value === null || value === undefined) return 'text';
        if (typeof value === 'boolean') return 'checkbox';
        if (typeof value === 'number') return 'number';
        if (typeof value === 'object') return 'json';
        if (typeof value === 'string' && value.includes('T') && !isNaN(Date.parse(value))) {
            return 'datetime-local';
        }
        return 'text';
    }

    createModal() {
        // Remove existing modal if any
        const existing = document.getElementById('create-modal');
        if (existing) existing.remove();

        const modal = document.createElement('div');
        modal.id = 'create-modal';
        modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.6);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9999;
      animation: fadeIn 0.2s ease-out;
    `;

        modal.innerHTML = `
      <div style="
        background: var(--bg-primary);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-xl);
        max-width: 600px;
        width: 90%;
        max-height: 80vh;
        overflow: hidden;
        display: flex;
        flex-direction: column;
      ">
        <div style="
          padding: var(--spacing-lg) var(--spacing-xl);
          border-bottom: 1px solid var(--border-color);
          display: flex;
          justify-content: space-between;
          align-items: center;
        ">
          <h2 style="margin: 0; color: var(--text-primary); font-size: var(--font-size-xl);">
            <i class="fas fa-plus"></i> Create Document
          </h2>
          <button onclick="createModal.close()" class="monglo-btn monglo-btn-secondary monglo-btn-sm">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div id="create-form-container" style="
          padding: var(--spacing-xl);
          overflow-y: auto;
          flex: 1;
        "></div>
        
        <div style="
          padding: var(--spacing-md) var(--spacing-xl);
          border-top: 1px solid var(--border-color);
          display: flex;
          gap: var(--spacing-sm);
          justify-content: space-between;
          align-items: center;
        ">
          <button onclick="createModal.addCustomField()" class="monglo-btn monglo-btn-secondary monglo-btn-sm">
            <i class="fas fa-plus"></i> Add Field
          </button>
          <div style="display: flex; gap: var(--spacing-md);">
            <button onclick="createModal.close()" class="monglo-btn monglo-btn-secondary">
              Cancel
            </button>
            <button onclick="createModal.save()" class="monglo-btn monglo-btn-primary">
              <i class="fas fa-save"></i> Create
            </button>
          </div>
        </div>
      </div>
    `;

        document.body.appendChild(modal);
        this.modal = modal;

        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.close();
        });
    }

    populateForm() {
        const container = document.getElementById('create-form-container');
        if (!container) return;

        let formHtml = '';

        if (Object.keys(this.detectedFields).length > 0) {
            formHtml += '<p style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-bottom: var(--spacing-lg);">Fill in the fields below. Detected from existing documents.</p>';

            for (const [key, type] of Object.entries(this.detectedFields)) {
                formHtml += this.generateField(key, '', type);
            }
        } else {
            formHtml += '<p style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-bottom: var(--spacing-lg);">No existing documents found. Click "Add Field" to add custom fields.</p>';
        }

        container.innerHTML = formHtml;
    }

    generateField(key, value, type, isCustom = false) {
        const checked = type === 'checkbox' && value ? 'checked' : '';

        return `
      <div style="margin-bottom: var(--spacing-lg);" class="field-group">
        <div style="display: flex; gap: var(--spacing-sm); align-items: center; margin-bottom: var(--spacing-sm);">
          ${isCustom ? `
            <input 
              type="text" 
              value="${key}"
              class="monglo-input field-name"
              placeholder="Field name"
              style="flex: 1; font-weight: 600; font-size: var(--font-size-sm);"
            />
            <button onclick="this.closest('.field-group').remove()" class="monglo-btn monglo-btn-danger monglo-btn-sm" title="Remove field">
              <i class="fas fa-times"></i>
            </button>
          ` : `
            <label style="
              flex: 1;
              font-weight: 600;
              color: var(--text-primary);
              font-size: var(--font-size-sm);
            ">
              ${key}
            </label>
          `}
        </div>
        ${type === 'checkbox' ? `
          <input 
            type="checkbox" 
            name="${key}" 
            ${checked}
            style="width: 20px; height: 20px; cursor: pointer;"
          />
        ` : type === 'json' ? `
          <textarea 
            name="${key}" 
            class="monglo-input"
            rows="4"
            placeholder="JSON object or array"
            style="font-family: var(--font-mono); font-size: var(--font-size-sm);"
          >${value}</textarea>
        ` : `
          <input 
            type="${type}" 
            name="${key}" 
            value="${value}"
            class="monglo-input"
            placeholder="Enter ${key}"
          />
        `}
      </div>
    `;
    }

    addCustomField() {
        const container = document.getElementById('create-form-container');
        if (!container) return;

        const fieldHtml = this.generateField('new_field', '', 'text', true);
        const div = document.createElement('div');
        div.innerHTML = fieldHtml;
        container.appendChild(div.firstElementChild);
    }

    async save() {
        const container = document.getElementById('create-form-container');
        if (!container) return;

        // Collect form data
        const formData = {};

        // Process field groups
        const fieldGroups = container.querySelectorAll('.field-group');
        fieldGroups.forEach(group => {
            const nameInput = group.querySelector('.field-name');
            const fieldName = nameInput ? nameInput.value.trim() : null;

            const input = group.querySelector('input[name], textarea[name]');
            if (!input) return;

            const key = fieldName || input.name;
            if (!key) return;

            let value = input.type === 'checkbox' ? input.checked : input.value;

            // Skip empty values
            if (value === '' || value === null) return;

            // Try to parse JSON fields
            if (input.tagName === 'TEXTAREA') {
                try {
                    value = JSON.parse(value);
                } catch (e) {
                    // Keep as string if not valid JSON
                }
            } else if (input.type === 'number') {
                value = parseFloat(value);
            }

            formData[key] = value;
        });

        // Create document
        try {
            const response = await fetch(`/api/admin/${this.currentCollection}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                this.close();
                window.location.reload(); // Reload to show new document
            } else {
                const error = await response.json();
                alert('Error creating document: ' + (error.message || 'Unknown error'));
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }

    close() {
        if (this.modal) {
            this.modal.remove();
            this.modal = null;
        }
    }
}

// Global instance
window.createModal = new CreateModal();

// Override the global createDocument function
window.createDocument = function () {
    const collection = window.location.pathname.split('/')[2];
    window.createModal.open(collection);
};
