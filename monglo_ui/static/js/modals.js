/**
 * EDIT & CREATE MODALS - Monglo Admin
 * With relationship dropdown support
 */

// Get prefix from page context (set by template)
const ADMIN_PREFIX = window.MONGLO_PREFIX || '/admin';
const CURRENT_COLLECTION = window.location.pathname.split('/').filter(Boolean)[1];

// Helper to detect if field is a relationship
function isRelationshipField(key) {
    return key.endsWith('_id') || key.endsWith('_ids');
}

// Helper to guess target collection from field name
function guessTargetCollection(fieldName) {
    if (fieldName.endsWith('_ids')) {
        const base = fieldName.slice(0, -4); // Remove '_ids'
        return pluralize(base);
    } else if (fieldName.endsWith('_id')) {
        const base = fieldName.slice(0, -3); // Remove '_id'
        return pluralize(base);
    }
    return null;
}

// Simple pluralization
function pluralize(word) {
    if (word.endsWith('y') && word.length > 1 && !'aeiou'.includes(word[word.length - 2])) {
        return word.slice(0, -1) + 'ies'; // category → categories
    } else if (word.match(/(s|ss|x|z|ch|sh)$/)) {
        return word + 'es';
    } else {
        return word + 's';
    }
}

// ==================== EDIT MODAL ====================
class EditModal {
    constructor() {
        this.modal = null;
        this.currentDocument = null;
        this.currentId = null;
        this.relationshipData = {};
    }

    async open(id) {
        this.currentId = id;

        // Fetch document via JSON API endpoint
        try {
            const response = await fetch(`${ADMIN_PREFIX}/${CURRENT_COLLECTION}/${id}/json`);
            if (!response.ok) throw new Error('Failed to fetch document');

            const data = await response.json();
            this.currentDocument = data.document || data;

            // Fetch relationship data
            await this.loadRelationships();

            this.createModal();
            this.populateForm();
        } catch (error) {
            console.error('Edit error:', error);
            alert('Error loading document: ' + error.message);
        }
    }

    async loadRelationships() {
        this.relationshipData = {};

        for (const [key, value] of Object.entries(this.currentDocument)) {
            if (isRelationshipField(key)) {
                const targetCollection = guessTargetCollection(key);
                // Skip if target collection is invalid or too short
                if (targetCollection && targetCollection.length > 1) {
                    try {
                        const response = await fetch(`${ADMIN_PREFIX}/${targetCollection}/list?per_page=100`);
                        if (response.ok) {
                            const data = await response.json();
                            this.relationshipData[key] = data.items || [];
                            console.log(`Loaded ${this.relationshipData[key].length} items for ${key} from ${targetCollection}`);
                        } else {
                            console.warn(`Failed to fetch ${targetCollection} (HTTP ${response.status})`);
                        }
                    } catch (error) {
                        console.warn(`Failed to load ${targetCollection} for ${key}:`, error);
                    }
                }
            }
        }
    }

    createModal() {
        const existing = document.getElementById('edit-modal');
        if (existing) existing.remove();

        const modal = document.createElement('div');
        modal.id = 'edit-modal';
        modal.className = 'monglo-modal';
        modal.innerHTML = `
            <div class="monglo-modal-content">
                <div class="monglo-modal-header">
                    <h2><i class="fas fa-edit"></i> Edit Document</h2>
                    <button onclick="editModal.close()" class="monglo-btn monglo-btn-secondary monglo-btn-sm">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div id="edit-form-container" class="monglo-modal-body"></div>
                <div class="monglo-modal-footer">
                    <button onclick="editModal.close()" class="monglo-btn monglo-btn-secondary">Cancel</button>
                    <button onclick="editModal.save()" class="monglo-btn monglo-btn-primary">
                        <i class="fas fa-save"></i> Save
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.modal = modal;

        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.close();
        });
    }

    populateForm() {
        const container = document.getElementById('edit-form-container');
        if (!container || !this.currentDocument) return;

        let formHtml = '';
        for (const [key, value] of Object.entries(this.currentDocument)) {
            if (key === '_id') continue;
            formHtml += this.generateField(key, value);
        }

        container.innerHTML = formHtml;
    }

    generateField(key, value) {
        const type = this.detectType(value);
        let inputHtml = '';

        // Check if this is a relationship field
        if (isRelationshipField(key) && this.relationshipData[key] && this.relationshipData[key].length > 0) {
            const options = this.relationshipData[key];
            const isMulti = key.endsWith('_ids');

            console.log(`Rendering ${key} as dropdown with ${options.length} options`);

            if (isMulti && Array.isArray(value)) {
                // Multiple select
                inputHtml = `<select name="${key}" class="monglo-input" multiple style="height: 120px;">`;
                options.forEach(opt => {
                    const selected = value.some(v => v.toString() === opt._id.toString()) ? 'selected' : '';
                    const label = opt.name || opt.title || opt.email || opt._id.toString();
                    inputHtml += `<option value="${opt._id}" ${selected}>${label}</option>`;
                });
                inputHtml += `</select>`;
            } else {
                // Single select
                inputHtml = `<select name="${key}" class="monglo-input">`;
                inputHtml += `<option value="">-- Select --</option>`;
                options.forEach(opt => {
                    const selected = (value && value.toString() === opt._id.toString()) ? 'selected' : '';
                    const label = opt.name || opt.title || opt.email || opt._id.toString();
                    inputHtml += `<option value="${opt._id}" ${selected}>${label}</option>`;
                });
                inputHtml += `</select>`;
            }
        } else if (type === 'boolean') {
            inputHtml = `<input type="checkbox" name="${key}" ${value ? 'checked' : ''} style="width: 20px; height: 20px;">`;
        } else if (type === 'datetime') {
            // Handle datetime - convert ISO string to datetime-local format
            let datetimeValue = '';
            if (value) {
                try {
                    const date = new Date(value);
                    // Format as YYYY-MM-DDTHH:mm for datetime-local input
                    datetimeValue = date.toISOString().slice(0, 16);
                } catch (e) {
                    datetimeValue = value;
                }
            }
            inputHtml = `<input type="datetime-local" name="${key}" value="${datetimeValue}" class="monglo-input">`;
        } else if (type === 'object') {
            const jsonValue = JSON.stringify(value, null, 2);
            inputHtml = `<textarea name="${key}" class="monglo-input" rows="5" style="font-family: monospace;">${jsonValue}</textarea>`;
        } else if (type === 'number') {
            inputHtml = `<input type="number" name="${key}" value="${value || ''}" class="monglo-input">`;
        } else {
            inputHtml = `<input type="text" name="${key}" value="${value || ''}" class="monglo-input">`;
        }

        return `
            <div class="monglo-form-group">
                <label>${key}${isRelationshipField(key) ? ' <span style="color: var(--color-primary);">(relationship)</span>' : ''}</label>
                ${inputHtml}
            </div>
        `;
    }

    detectType(value) {
        if (value === null || value === undefined) return 'text';
        if (typeof value === 'boolean') return 'boolean';
        if (typeof value === 'number') return 'number';
        if (typeof value === 'object') return 'object';
        // Check if it's a datetime string
        if (typeof value === 'string' && /\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(value)) {
            return 'datetime';
        }
        return 'text';
    }

    async save() {
        const container = document.getElementById('edit-form-container');
        if (!container) return;

        const formData = {};
        container.querySelectorAll('input, textarea, select').forEach(input => {
            const key = input.name;
            let value;

            if (input.type === 'checkbox') {
                value = input.checked;
            } else if (input.tagName === 'SELECT' && input.multiple) {
                value = Array.from(input.selectedOptions).map(opt => opt.value);
            } else if (input.tagName === 'SELECT') {
                value = input.value;
            } else {
                value = input.value;
            }

            if (input.tagName === 'TEXTAREA') {
                try {
                    value = JSON.parse(value);
                } catch (e) {
                    // Keep as string
                }
            } else if (input.type === 'number') {
                value = parseFloat(value);
            }

            formData[key] = value;
        });

        try {
            const response = await fetch(`${ADMIN_PREFIX}/${CURRENT_COLLECTION}/${this.currentId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                this.close();
                window.location.reload();
            } else {
                const error = await response.text();
                alert('Error: ' + error);
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

// ==================== CREATE MODAL ====================
class CreateModal {
    constructor() {
        this.modal = null;
        this.fields = {};
        this.relationshipData = {};
    }

    async open() {
        await this.detectFields();
        await this.loadRelationships();
        this.createModal();
        this.populateForm();
    }

    async detectFields() {
        try {
            const response = await fetch(`${ADMIN_PREFIX}/${CURRENT_COLLECTION}/list?per_page=5`);
            if (!response.ok) {
                this.fields = {};
                return;
            }

            const data = await response.json();
            const items = data.items || [];

            if (items.length > 0) {
                const fieldSet = new Set();
                items.forEach(item => {
                    Object.keys(item).forEach(key => {
                        if (key !== '_id') fieldSet.add(key);
                    });
                });

                const sample = items[0];
                this.fields = {};
                fieldSet.forEach(field => {
                    this.fields[field] = this.detectType(sample[field]);
                });
            } else {
                this.fields = {};
            }
        } catch (error) {
            console.error('Field detection error:', error);
            this.fields = {};
        }
    }

    async loadRelationships() {
        this.relationshipData = {};

        for (const key of Object.keys(this.fields)) {
            if (isRelationshipField(key)) {
                const targetCollection = guessTargetCollection(key);
                if (targetCollection) {
                    try {
                        const response = await fetch(`${ADMIN_PREFIX}/${targetCollection}/list?per_page=100`);
                        if (response.ok) {
                            const data = await response.json();
                            this.relationshipData[key] = data.items || [];
                        }
                    } catch (error) {
                        console.warn(`Failed to load ${targetCollection} for ${key}:`, error);
                    }
                }
            }
        }
    }

    detectType(value) {
        if (value === null || value === undefined) return 'text';
        if (typeof value === 'boolean') return 'boolean';
        if (typeof value === 'number') return 'number';
        if (typeof value === 'object') return 'object';
        return 'text';
    }

    createModal() {
        const existing = document.getElementById('create-modal');
        if (existing) existing.remove();

        const modal = document.createElement('div');
        modal.id = 'create-modal';
        modal.className = 'monglo-modal';
        modal.innerHTML = `
            <div class="monglo-modal-content">
                <div class="monglo-modal-header">
                    <h2><i class="fas fa-plus"></i> Create Document</h2>
                    <button onclick="createModal.close()" class="monglo-btn monglo-btn-secondary monglo-btn-sm">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div id="create-form-container" class="monglo-modal-body"></div>
                <div class="monglo-modal-footer">
                    <button onclick="createModal.addField()" class="monglo-btn monglo-btn-secondary monglo-btn-sm">
                        <i class="fas fa-plus"></i> Add Field
                    </button>
                    <div style="flex: 1;"></div>
                    <button onclick="createModal.close()" class="monglo-btn monglo-btn-secondary">Cancel</button>
                    <button onclick="createModal.save()" class="monglo-btn monglo-btn-primary">
                        <i class="fas fa-save"></i> Create
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.modal = modal;

        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.close();
        });
    }

    populateForm() {
        const container = document.getElementById('create-form-container');
        if (!container) return;

        let formHtml = '';

        if (Object.keys(this.fields).length > 0) {
            formHtml += '<p class="monglo-hint">Fields detected from existing documents:</p>';
            for (const [key, type] of Object.entries(this.fields)) {
                formHtml += this.generateField(key, '', type, false);
            }
        } else {
            formHtml += '<p class="monglo-hint">No existing documents found. Click "Add Field" to add fields.</p>';
        }

        container.innerHTML = formHtml;
    }

    generateField(key, value, type, isCustom) {
        let inputHtml = '';

        // Check if this is a relationship field
        if (isRelationshipField(key) && this.relationshipData[key]) {
            const options = this.relationshipData[key];
            const isMulti = key.endsWith('_ids');

            if (isMulti) {
                inputHtml = `<select name="${key}" class="monglo-input" multiple style="height: 120px;">`;
                options.forEach(opt => {
                    const label = opt.name || opt.title || opt.email || opt._id;
                    inputHtml += `<option value="${opt._id}">${label}</option>`;
                });
                inputHtml += `</select>`;
            } else {
                inputHtml = `<select name="${key}" class="monglo-input">`;
                inputHtml += `<option value="">-- Select --</option>`;
                options.forEach(opt => {
                    const label = opt.name || opt.title || opt.email || opt._id;
                    inputHtml += `<option value="${opt._id}">${label}</option>`;
                });
                inputHtml += `</select>`;
            }
        } else if (type === 'boolean') {
            inputHtml = `<input type="checkbox" name="${key}" style="width: 20px; height: 20px;">`;
        } else if (type === 'object') {
            inputHtml = `<textarea name="${key}" class="monglo-input" rows="4" placeholder='{"key": "value"}'></textarea>`;
        } else if (type === 'number') {
            inputHtml = `<input type="number" name="${key}" class="monglo-input" placeholder="Enter number">`;
        } else {
            inputHtml = `<input type="text" name="${key}" class="monglo-input" placeholder="Enter ${key}">`;
        }

        return `
            <div class="monglo-form-group ${isCustom ? 'custom-field' : ''}">
                ${isCustom ? `
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <input type="text" class="monglo-input field-name-input" value="${key}" placeholder="Field name" style="flex: 1;">
                        <button onclick="this.closest('.monglo-form-group').remove()" class="monglo-btn monglo-btn-danger monglo-btn-sm">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                ` : `<label>${key}${isRelationshipField(key) ? ' <span style="color: var(--color-primary);">(relationship)</span>' : ''}</label>`}
                ${inputHtml}
            </div>
        `;
    }

    addField() {
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

        const formData = {};

        // Get all form groups
        container.querySelectorAll('.monglo-form-group').forEach(group => {
            const nameInput = group.querySelector('.field-name-input');
            const valueInput = group.querySelector('input[name], textarea[name], select[name]');

            if (!valueInput) return;

            const key = nameInput ? nameInput.value.trim() : valueInput.name;
            if (!key) return;

            let value;
            if (valueInput.type === 'checkbox') {
                value = valueInput.checked;
            } else if (valueInput.tagName === 'SELECT' && valueInput.multiple) {
                value = Array.from(valueInput.selectedOptions).map(opt => opt.value);
            } else if (valueInput.tagName === 'SELECT') {
                value = valueInput.value;
            } else {
                value = valueInput.value;
            }

            if (value === '' || value === null) return;

            if (valueInput.tagName === 'TEXTAREA') {
                try {
                    value = JSON.parse(value);
                } catch (e) {
                    // Keep as string
                }
            } else if (valueInput.type === 'number') {
                value = parseFloat(value);
            }

            formData[key] = value;
        });

        if (Object.keys(formData).length === 0) {
            alert('Please add at least one field');
            return;
        }

        try {
            const response = await fetch(`${ADMIN_PREFIX}/${CURRENT_COLLECTION}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                this.close();
                window.location.reload();
            } else {
                const error = await response.text();
                alert('Error: ' + error);
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

// Global instances
window.editModal = new EditModal();
window.createModal = new CreateModal();

// Global functions
window.editDocument = (id) => window.editModal.open(id);
window.createDocument = () => window.createModal.open();
