# Monglo UI

Professional admin interface for Monglo.

## Features

- ✨ **Modern Design** - Beautiful, professional interface
- 📱 **Responsive** - Works on desktop, tablet, and mobile
- ⚡ **Fast** - Optimized CSS and JavaScript
- 🎨 **Themeable** - Customizable design system
- ♿ **Accessible** - WCAG 2.1 AA compliant

## Components

### Table View
- Sortable columns
- Search and filters
- Pagination
- Bulk actions
- Export functionality

### Document View
- JSON tree display
- Syntax highlighting
- Relationship navigation
- Edit/delete actions

### Sidebar
- Collection list
- Document counts
- Active state
- Responsive collapse

## Installation

The UI is automatically included with Monglo. No separate installation needed.

## Customization

### Custom Styles

```python
from monglo_ui import MongloUI

ui = MongloUI(
    custom_css="/path/to/custom.css",
    theme={
        "primary": "#your-color",
        "border_radius": "12px"
    }
)
```

### Custom Templates

```python
ui = MongloUI(
    template_dir="/path/to/templates"
)
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers

## License

MIT
