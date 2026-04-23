/**
 * TechGraph — vis.js helper compartido
 */

const TYPE_COLORS = {
  language:  { bg: '#1e3a6b', border: '#3b82f6', font: '#93c5fd' },
  framework: { bg: '#2d1b5c', border: '#8b5cf6', font: '#c4b5fd' },
  library:   { bg: '#0d3d30', border: '#10b981', font: '#6ee7b7' },
  tool:      { bg: '#3d2b00', border: '#f59e0b', font: '#fcd34d' },
  database:  { bg: '#4a1212', border: '#ef4444', font: '#fca5a5' },
  platform:  { bg: '#0a3040', border: '#06b6d4', font: '#67e8f9' },
  other:     { bg: '#1e2740', border: '#64748b', font: '#94a3b8' },
  project:   { bg: '#3d1a00', border: '#f97316', font: '#fdba74' },
};

const REL_COLORS = {
  USES:            '#f9741655',
  COMPATIBLE_WITH: '#10b98155',
  DEPENDS_ON:      '#3b82f655',
  ALTERNATIVE_TO:  '#f59e0b55',
  EXTENDS:         '#8b5cf655',
  compatible_with: '#10b98155',
  depends_on:      '#3b82f655',
  alternative_to:  '#f59e0b55',
  extends:         '#8b5cf655',
  uses:            '#f9741655',
  used_by:         '#f9741655',
};

function buildNode(n) {
  const type = n.subtype || n.type || 'other';
  const colors = TYPE_COLORS[type] || TYPE_COLORS.other;
  return {
    id: n.id,
    label: n.label,
    title: `${n.label}\n${type}`,
    color: {
      background: n.main ? colors.border : colors.bg,
      border: colors.border,
      highlight: { background: colors.border, border: '#fff' },
    },
    font: { color: n.main ? '#fff' : colors.font, size: n.main ? 14 : 12 },
    size: n.main ? 22 : 14,
    shape: n.type === 'project' ? 'diamond' : 'dot',
    borderWidth: n.main ? 2 : 1,
  };
}

function buildEdge(e) {
  const color = REL_COLORS[e.label] || '#ffffff20';
  return {
    from: e.from,
    to: e.to,
    label: e.label ? e.label.toLowerCase().replace(/_/g, ' ') : '',
    color: { color, highlight: '#ffffff80' },
    font: { color: '#64748b', size: 9, align: 'middle' },
    arrows: { to: { enabled: true, scaleFactor: 0.6 } },
    smooth: { type: 'curvedCW', roundness: 0.15 },
    width: 1.5,
  };
}

const BASE_OPTIONS = {
  nodes: { borderWidth: 1, shadow: false },
  edges: { shadow: false },
  physics: {
    enabled: true,
    barnesHut: {
      gravitationalConstant: -8000,
      centralGravity: 0.3,
      springLength: 120,
      springConstant: 0.04,
      damping: 0.09,
    },
    stabilization: { iterations: 150 },
  },
  interaction: { hover: true, tooltipDelay: 150 },
  layout: { improvedLayout: true },
};

function initGraph(containerId, graphData, options = {}) {
  const container = document.getElementById(containerId);
  if (!container) return null;

  const nodes = new vis.DataSet(graphData.nodes.map(buildNode));
  const edges = new vis.DataSet(graphData.edges.map(buildEdge));

  const network = new vis.Network(
    container,
    { nodes, edges },
    { ...BASE_OPTIONS, ...options }
  );

  network.once('stabilizationIterationsDone', () => {
    network.setOptions({ physics: false });
  });

  return { network, nodes, edges };
}