// TypeScript interfaces for Knowledge Graph Visualization

export interface GraphNode {
  id: string;
  name: string;
  type: EntityType;
  mentions: number;
  relevance: number;
  confidence?: number;
  epithets?: string[];
  sanskritName?: string;
  x?: number;
  y?: number;
  fx?: number | null; // Fixed position x (for dragging)
  fy?: number | null; // Fixed position y (for dragging)
}

export interface GraphEdge {
  source: string | GraphNode;
  target: string | GraphNode;
  relationship: string;
  weight: number;
  verified?: boolean;
  confidence?: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: {
    centerEntity?: string;
    searchQuery?: string;
    totalEntities?: number;
    maxDepth?: number;
  };
}

export type EntityType = 'Person' | 'Place' | 'Event' | 'Object' | 'Concept';

export type LayoutType = 'force' | 'hierarchical' | 'radial' | 'circular';

export interface GraphConfig {
  width: number;
  height: number;
  nodeRadius: (d: GraphNode) => number;
  linkDistance: number;
  chargeStrength: number;
  showLabels: boolean;
  showEdgeLabels: boolean;
  layout: LayoutType;
  colorScheme: 'default' | 'type' | 'confidence';
}

export interface GraphEventHandlers {
  onNodeClick?: (node: GraphNode) => void;
  onNodeHover?: (node: GraphNode | null) => void;
  onEdgeClick?: (edge: GraphEdge) => void;
  onBackgroundClick?: () => void;
}

export interface FilterConfig {
  entityTypes: EntityType[];
  minMentions: number;
  minConfidence: number;
  maxNodes: number;
  showIsolatedNodes: boolean;
}

// API response interfaces
export interface KGEntity {
  kg_id: string;
  entity_type: string;
  labels: {
    en: string;
    sa?: string;
  };
  properties: {
    confidence_score?: number;
    extraction_confidence?: number;
    occurrence_count?: number;
    epithets?: string[];
  };
  created_at?: string;
  updated_at?: string;
}

export interface KGRelationship {
  id: string;
  source_entity_id: string;
  target_entity_id: string;
  relationship_type: string;
  confidence: number;
  properties?: Record<string, any>;
}

export interface GraphApiResponse {
  success: boolean;
  entities: KGEntity[];
  relationships: KGRelationship[];
  center_entity?: string;
  max_depth?: number;
}

// Graph visualization state
export interface GraphState {
  selectedNodes: Set<string>;
  hoveredNode: GraphNode | null;
  selectedEdge: GraphEdge | null;
  isLoading: boolean;
  error: string | null;
  transform: {
    x: number;
    y: number;
    k: number;
  };
}

// Search and path finding
export interface PathResult {
  path: GraphNode[];
  edges: GraphEdge[];
  distance: number;
  confidence: number;
}

export interface SearchHighlight {
  nodeIds: string[];
  edgeIds: string[];
  query: string;
}