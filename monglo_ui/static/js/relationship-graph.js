// Monglo Relationship Graph - D3.js visualization

class MongloRelationshipGraph {
    constructor(containerId, data) {
        this.container = document.getElementById(containerId);
        this.data = data;
        this.width = this.container.offsetWidth;
        this.height = 600;

        this.init();
    }

    init() {
        // Create SVG
        this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        this.svg.setAttribute('width', this.width);
        this.svg.setAttribute('height', this.height);
        this.svg.style.background = '#fff';
        this.svg.style.borderRadius = 'var(--radius-lg)';
        this.svg.style.boxShadow = 'var(--shadow-sm)';

        this.container.appendChild(this.svg);

        this.render();
    }

    render() {
        const { nodes, links } = this.prepareData();

        // Simple force-directed layout (without D3.js dependency)
        this.renderWithSimpleLayout(nodes, links);
    }

    prepareData() {
        const nodes = [];
        const links = [];
        const nodeMap = new Map();

        // Create nodes from collections
        this.data.collections.forEach((collection, index) => {
            const node = {
                id: collection.name,
                label: collection.display_name || collection.name,
                x: (this.width / (this.data.collections.length + 1)) * (index + 1),
                y: this.height / 2,
                vx: 0,
                vy: 0
            };
            nodes.push(node);
            nodeMap.set(collection.name, node);
        });

        // Create links from relationships
        this.data.relationships.forEach(rel => {
            const source = nodeMap.get(rel.source_collection);
            const target = nodeMap.get(rel.target_collection);

            if (source && target) {
                links.push({
                    source: source,
                    target: target,
                    type: rel.type,
                    field: rel.source_field
                });
            }
        });

        return { nodes, links };
    }

    renderWithSimpleLayout(nodes, links) {
        // Simple force simulation
        const iterations = 100;
        for (let i = 0; i < iterations; i++) {
            this.applyForces(nodes, links);
        }

        // Render links
        links.forEach(link => {
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', link.source.x);
            line.setAttribute('y1', link.source.y);
            line.setAttribute('x2', link.target.x);
            line.setAttribute('y2', link.target.y);
            line.setAttribute('stroke', '#d1d5db');
            line.setAttribute('stroke-width', '2');
            line.setAttribute('marker-end', 'url(#arrowhead)');

            // Tooltip
            const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
            title.textContent = `${link.field} (${link.type})`;
            line.appendChild(title);

            this.svg.appendChild(line);
        });

        // Add arrowhead marker
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.setAttribute('id', 'arrowhead');
        marker.setAttribute('markerWidth', '10');
        marker.setAttribute('markerHeight', '10');
        marker.setAttribute('refX', '25');
        marker.setAttribute('refY', '3');
        marker.setAttribute('orient', 'auto');

        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '0 0, 6 3, 0 6');
        polygon.setAttribute('fill', '#d1d5db');
        marker.appendChild(polygon);
        defs.appendChild(marker);
        this.svg.insertBefore(defs, this.svg.firstChild);

        // Render nodes
        nodes.forEach(node => {
            const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            group.setAttribute('transform', `translate(${node.x}, ${node.y})`);
            group.style.cursor = 'pointer';

            // Circle
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('r', '30');
            circle.setAttribute('fill', '#2563eb');
            circle.setAttribute('stroke', '#fff');
            circle.setAttribute('stroke-width', '3');

            // Hover effect
            group.addEventListener('mouseenter', () => {
                circle.setAttribute('r', '35');
                circle.setAttribute('fill', '#1d4ed8');
            });
            group.addEventListener('mouseleave', () => {
                circle.setAttribute('r', '30');
                circle.setAttribute('fill', '#2563eb');
            });

            // Click to navigate
            group.addEventListener('click', () => {
                window.location.href = `/admin/${node.id}`;
            });

            group.appendChild(circle);

            // Label
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('dy', '50');
            text.setAttribute('fill', '#374151');
            text.setAttribute('font-weight', '600');
            text.setAttribute('font-size', '14');
            text.textContent = node.label;

            group.appendChild(text);
            this.svg.appendChild(group);
        });
    }

    applyForces(nodes, links) {
        const repulsion = 5000;
        const attraction = 0.01;
        const damping = 0.8;

        // Repulsion between nodes
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const dx = nodes[j].x - nodes[i].x;
                const dy = nodes[j].y - nodes[i].y;
                const distSq = dx * dx + dy * dy + 0.01; // Avoid division by zero
                const force = repulsion / distSq;

                const fx = (dx / Math.sqrt(distSq)) * force;
                const fy = (dy / Math.sqrt(distSq)) * force;

                nodes[i].vx -= fx;
                nodes[i].vy -= fy;
                nodes[j].vx += fx;
                nodes[j].vy += fy;
            }
        }

        // Attraction along links
        links.forEach(link => {
            const dx = link.target.x - link.source.x;
            const dy = link.target.y - link.source.y;

            link.source.vx += dx * attraction;
            link.source.vy += dy * attraction;
            link.target.vx -= dx * attraction;
            link.target.vy -= dy * attraction;
        });

        // Update positions
        nodes.forEach(node => {
            node.x += node.vx;
            node.y += node.vy;

            // Apply damping
            node.vx *= damping;
            node.vy *= damping;

            // Keep within bounds
            const margin = 50;
            node.x = Math.max(margin, Math.min(this.width - margin, node.x));
            node.y = Math.max(margin, Math.min(this.height - margin, node.y));
        });
    }
}

// Export
window.MongloRelationshipGraph = MongloRelationshipGraph;
