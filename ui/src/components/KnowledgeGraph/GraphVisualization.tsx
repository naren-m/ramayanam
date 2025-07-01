import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as d3 from 'd3';
import { GraphNode, GraphEdge, GraphData, GraphConfig, GraphEventHandlers, GraphState, EntityType } from './types';

interface GraphVisualizationProps {
  data: GraphData;
  config?: Partial<GraphConfig>;
  eventHandlers?: GraphEventHandlers;
  className?: string;
}

const DEFAULT_CONFIG: GraphConfig = {
  width: 800,
  height: 600,
  nodeRadius: (d: GraphNode) => Math.max(8, Math.min(20, Math.sqrt(d.mentions) * 2)),
  linkDistance: 100,
  chargeStrength: -300,
  showLabels: true,
  showEdgeLabels: false,
  layout: 'force',
  colorScheme: 'type'
};

const ENTITY_COLORS: Record<EntityType, string> = {
  'Person': '#3B82F6',     // Blue
  'Place': '#10B981',      // Green
  'Event': '#8B5CF6',      // Purple
  'Object': '#F59E0B',     // Amber
  'Concept': '#EC4899'     // Pink
};

export const GraphVisualization: React.FC<GraphVisualizationProps> = ({
  data,
  config: userConfig = {},
  eventHandlers = {},
  className = ''
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [config, setConfig] = useState<GraphConfig>({ ...DEFAULT_CONFIG, ...userConfig });
  const [state, setState] = useState<GraphState>({
    selectedNodes: new Set(),
    hoveredNode: null,
    selectedEdge: null,
    isLoading: false,
    error: null,
    transform: { x: 0, y: 0, k: 1 }
  });

  // Update config when userConfig changes
  useEffect(() => {
    setConfig({ ...DEFAULT_CONFIG, ...userConfig });
  }, [userConfig]);

  // Resize handler
  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        setConfig(prev => ({ ...prev, width, height }));
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Main graph rendering effect
  useEffect(() => {
    if (!data.nodes.length || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous content

    // Create main container group
    const container = svg.append('g').attr('class', 'graph-container');

    // Setup zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
        setState(prev => ({
          ...prev,
          transform: { x: event.transform.x, y: event.transform.y, k: event.transform.k }
        }));
      });

    svg.call(zoom);

    // Background click handler
    svg.on('click', (event) => {
      if (event.target === event.currentTarget) {
        eventHandlers.onBackgroundClick?.();
        setState(prev => ({
          ...prev,
          selectedNodes: new Set(),
          selectedEdge: null
        }));
      }
    });

    // Create force simulation
    const simulation = d3.forceSimulation<GraphNode>(data.nodes)
      .force('link', d3.forceLink<GraphNode, GraphEdge>(data.edges)
        .id(d => d.id)
        .distance(config.linkDistance))
      .force('charge', d3.forceManyBody().strength(config.chargeStrength))
      .force('center', d3.forceCenter(config.width / 2, config.height / 2))
      .force('collision', d3.forceCollide().radius(d => config.nodeRadius(d) + 2));

    // Create arrow markers for directed edges
    const defs = svg.append('defs');
    
    Object.entries(ENTITY_COLORS).forEach(([type, color]) => {
      defs.append('marker')
        .attr('id', `arrow-${type}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 15)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', color)
        .attr('opacity', 0.6);
    });

    // Create edges
    const links = container.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(data.edges)
      .enter().append('line')
      .attr('class', 'edge')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.3)
      .attr('stroke-width', d => Math.sqrt(d.weight))
      .attr('marker-end', d => {
        const sourceNode = data.nodes.find(n => n.id === (typeof d.source === 'string' ? d.source : d.source.id));
        return sourceNode ? `url(#arrow-${sourceNode.type})` : '';
      })
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        event.stopPropagation();
        eventHandlers.onEdgeClick?.(d);
        setState(prev => ({ ...prev, selectedEdge: d }));
      })
      .on('mouseover', function(event, d) {
        d3.select(this)
          .attr('stroke', '#ff6b35')
          .attr('stroke-opacity', 0.8)
          .attr('stroke-width', Math.sqrt(d.weight) + 2);
        
        // Show edge tooltip
        if (config.showEdgeLabels) {
          const tooltip = d3.select('body').append('div')
            .attr('class', 'edge-tooltip')
            .style('position', 'absolute')
            .style('background', 'rgba(0,0,0,0.8)')
            .style('color', 'white')
            .style('padding', '8px')
            .style('border-radius', '4px')
            .style('font-size', '12px')
            .style('pointer-events', 'none')
            .style('z-index', '1000')
            .text(d.relationship);
          
          tooltip
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px');
        }
      })
      .on('mouseout', function(event, d) {
        d3.select(this)
          .attr('stroke', '#999')
          .attr('stroke-opacity', 0.3)
          .attr('stroke-width', Math.sqrt(d.weight));
        
        d3.selectAll('.edge-tooltip').remove();
      });

    // Create nodes
    const nodes = container.append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(data.nodes)
      .enter().append('circle')
      .attr('class', 'node')
      .attr('r', config.nodeRadius)
      .attr('fill', d => ENTITY_COLORS[d.type] || '#6B7280')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .call(d3.drag<SVGCircleElement, GraphNode>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
      )
      .on('click', (event, d) => {
        event.stopPropagation();
        eventHandlers.onNodeClick?.(d);
        setState(prev => {
          const newSelected = new Set(prev.selectedNodes);
          if (newSelected.has(d.id)) {
            newSelected.delete(d.id);
          } else {
            newSelected.add(d.id);
          }
          return { ...prev, selectedNodes: newSelected };
        });
      })
      .on('mouseover', (event, d) => {
        eventHandlers.onNodeHover?.(d);
        setState(prev => ({ ...prev, hoveredNode: d }));
        
        // Highlight connected edges
        links
          .attr('stroke-opacity', edge => {
            const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id;
            const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id;
            return (sourceId === d.id || targetId === d.id) ? 0.8 : 0.1;
          });
        
        // Highlight connected nodes
        nodes
          .attr('opacity', node => {
            if (node.id === d.id) return 1;
            const isConnected = data.edges.some(edge => {
              const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id;
              const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id;
              return (sourceId === d.id && targetId === node.id) ||
                     (targetId === d.id && sourceId === node.id);
            });
            return isConnected ? 1 : 0.3;
          });
      })
      .on('mouseout', () => {
        eventHandlers.onNodeHover?.(null);
        setState(prev => ({ ...prev, hoveredNode: null }));
        
        // Reset highlighting
        links.attr('stroke-opacity', 0.3);
        nodes.attr('opacity', 1);
      });

    // Create labels
    let labels: d3.Selection<SVGTextElement, GraphNode, SVGGElement, unknown> | null = null;
    if (config.showLabels) {
      labels = container.append('g')
        .attr('class', 'labels')
        .selectAll('text')
        .data(data.nodes)
        .enter().append('text')
        .attr('class', 'node-label')
        .attr('text-anchor', 'middle')
        .attr('dy', d => config.nodeRadius(d) + 15)
        .attr('font-size', '12px')
        .attr('font-weight', 'bold')
        .attr('fill', '#374151')
        .style('pointer-events', 'none')
        .text(d => d.name.length > 12 ? d.name.substring(0, 12) + '...' : d.name);
    }

    // Update positions on simulation tick
    simulation.on('tick', () => {
      links
        .attr('x1', d => (d.source as GraphNode).x!)
        .attr('y1', d => (d.source as GraphNode).y!)
        .attr('x2', d => (d.target as GraphNode).x!)
        .attr('y2', d => (d.target as GraphNode).y!);

      nodes
        .attr('cx', d => d.x!)
        .attr('cy', d => d.y!);

      if (labels) {
        labels
          .attr('x', d => d.x!)
          .attr('y', d => d.y!);
      }
    });

    // Apply selection styling
    nodes
      .attr('stroke-width', d => state.selectedNodes.has(d.id) ? 4 : 2)
      .attr('stroke', d => state.selectedNodes.has(d.id) ? '#ff6b35' : '#fff');

    // Cleanup function
    return () => {
      simulation.stop();
    };

  }, [data, config, state.selectedNodes, eventHandlers]);

  return (
    <div 
      ref={containerRef}
      className={`relative w-full h-full bg-gray-50 dark:bg-gray-900 rounded-lg overflow-hidden ${className}`}
      data-testid="graph-visualization"
    >
      <svg
        ref={svgRef}
        width={config.width}
        height={config.height}
        className="w-full h-full"
      >
      </svg>
      
      {/* Graph info overlay */}
      <div className="absolute top-4 left-4 bg-white dark:bg-gray-800 rounded-lg p-3 shadow-lg">
        <div className="text-sm text-gray-600 dark:text-gray-400">
          <div>Nodes: {data.nodes.length}</div>
          <div>Edges: {data.edges.length}</div>
          {state.selectedNodes.size > 0 && (
            <div>Selected: {state.selectedNodes.size}</div>
          )}
        </div>
      </div>

      {/* Zoom controls */}
      <div className="absolute top-4 right-4 flex flex-col space-y-2">
        <button
          onClick={() => {
            const svg = d3.select(svgRef.current);
            svg.transition().duration(300).call(
              d3.zoom<SVGSVGElement, unknown>().transform,
              d3.zoomIdentity.scale(state.transform.k * 1.5)
            );
          }}
          className="bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg p-2 shadow-lg transition-colors"
          title="Zoom In"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </button>
        
        <button
          onClick={() => {
            const svg = d3.select(svgRef.current);
            svg.transition().duration(300).call(
              d3.zoom<SVGSVGElement, unknown>().transform,
              d3.zoomIdentity.scale(state.transform.k * 0.75)
            );
          }}
          className="bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg p-2 shadow-lg transition-colors"
          title="Zoom Out"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 12H6" />
          </svg>
        </button>
        
        <button
          onClick={() => {
            const svg = d3.select(svgRef.current);
            svg.transition().duration(500).call(
              d3.zoom<SVGSVGElement, unknown>().transform,
              d3.zoomIdentity
            );
          }}
          className="bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg p-2 shadow-lg transition-colors"
          title="Reset View"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      {/* Loading overlay */}
      {state.isLoading && (
        <div className="absolute inset-0 bg-white bg-opacity-75 dark:bg-gray-900 dark:bg-opacity-75 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500 mx-auto mb-2"></div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Loading graph...</div>
          </div>
        </div>
      )}

      {/* Error overlay */}
      {state.error && (
        <div className="absolute inset-0 bg-red-50 dark:bg-red-900 bg-opacity-75 flex items-center justify-center">
          <div className="text-center p-4">
            <div className="text-red-600 dark:text-red-300 mb-2">⚠️ Graph Error</div>
            <div className="text-sm text-red-500 dark:text-red-400">{state.error}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GraphVisualization;