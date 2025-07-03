import React, { useState, useEffect, useCallback } from 'react';
import { Search, Filter, X, ChevronDown, Users, MapPin, Calendar, Package, Brain, Eye, EyeOff, Network, List } from 'lucide-react';
import LoadingSpinner from '../LoadingSpinner';
import GraphVisualization from './GraphVisualization';
import GraphControls from './GraphControls';
import { GraphData, GraphNode, GraphEdge, GraphConfig, FilterConfig, EntityType, KGEntity } from './types';
import { GraphDataService } from './GraphDataService';

// Existing interfaces from the original component
interface KGSearchResponse {
  success: boolean;
  entities: KGEntity[];
  count: number;
  query: string;
}

interface KGStatistics {
  success: boolean;
  statistics: {
    entity_counts: Record<string, number>;
    total_entities: number;
    total_relationships: number;
    total_mentions: number;
    top_entities: Array<{
      kg_id: string;
      labels: { en: string; sa?: string };
      mention_count: number;
    }>;
  };
}

const ENTITY_TYPES = [
  { value: '', label: 'All Types', icon: Filter },
  { value: 'Person', label: 'People', icon: Users },
  { value: 'Place', label: 'Places', icon: MapPin },
  { value: 'Event', label: 'Events', icon: Calendar },
  { value: 'Object', label: 'Objects', icon: Package },
  { value: 'Concept', label: 'Concepts', icon: Brain }
];

const DEFAULT_GRAPH_CONFIG: GraphConfig = {
  width: 800,
  height: 600,
  nodeRadius: (d: GraphNode) => Math.max(8, Math.min(20, Math.sqrt(d.mentions) * 2)),
  linkDistance: 120,
  chargeStrength: -400,
  showLabels: true,
  showEdgeLabels: false,
  layout: 'force',
  colorScheme: 'type'
};

const DEFAULT_FILTERS: FilterConfig = {
  entityTypes: ['Person', 'Place', 'Event', 'Object', 'Concept'],
  minMentions: 1,
  minConfidence: 0.0,
  maxNodes: 50,
  showIsolatedNodes: true
};

export const EnhancedKnowledgeGraphSearch: React.FC = () => {
  // Original state
  const [query, setQuery] = useState('');
  const [entityType, setEntityType] = useState('');
  const [results, setResults] = useState<KGEntity[]>([]);
  const [statistics, setStatistics] = useState<KGStatistics['statistics'] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedEntity, setSelectedEntity] = useState<KGEntity | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  
  // New graph visualization state
  const [viewMode, setViewMode] = useState<'search' | 'browse' | 'graph'>('search');
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });
  const [graphConfig, setGraphConfig] = useState<GraphConfig>(DEFAULT_GRAPH_CONFIG);
  const [graphFilters, setGraphFilters] = useState<FilterConfig>(DEFAULT_FILTERS);
  const [selectedNodes, setSelectedNodes] = useState<Set<string>>(new Set());
  const [centerEntity, setCenterEntity] = useState<string | null>(null);

  const API_BASE = '';

  useEffect(() => {
    fetchStatistics();
    if (viewMode === 'browse') {
      fetchAllEntities();
    } else if (viewMode === 'graph') {
      loadGraphData();
    }
  }, [viewMode]);

  const fetchStatistics = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/kg/statistics`);
      const data: KGStatistics = await response.json();
      if (data.success) {
        setStatistics(data.statistics);
      }
    } catch (err) {
      console.error('Failed to fetch statistics:', err);
    }
  };

  const fetchAllEntities = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/kg/entities?limit=50${entityType ? `&type=${entityType}` : ''}`);
      const data = await response.json();
      if (data.success) {
        setResults(data.entities);
      } else {
        setError('Failed to fetch entities');
      }
    } catch (err) {
      setError('Failed to connect to knowledge graph API');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const searchUrl = `${API_BASE}/api/kg/search?q=${encodeURIComponent(query)}${entityType ? `&type=${entityType}` : ''}`;
      const response = await fetch(searchUrl);
      const data: KGSearchResponse = await response.json();
      
      if (data.success) {
        setResults(data.entities);
        setViewMode('search');
      } else {
        setError('Search failed');
      }
    } catch (err) {
      setError('Failed to connect to knowledge graph API');
    } finally {
      setLoading(false);
    }
  };

  const loadGraphData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await GraphDataService.createGraphData(
        centerEntity || undefined,
        graphFilters.maxNodes,
        true
      );
      
      // Apply filters to the data
      const filteredData = applyFiltersToGraphData(data, graphFilters);
      setGraphData(filteredData);
    } catch (err) {
      setError('Failed to load graph data');
      console.error('Graph loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const applyFiltersToGraphData = (data: GraphData, filters: FilterConfig): GraphData => {
    let filteredNodes = data.nodes.filter(node => {
      // Entity type filter
      if (!filters.entityTypes.includes(node.type)) return false;
      
      // Mentions filter
      if (node.mentions < filters.minMentions) return false;
      
      // Confidence filter
      if (node.confidence && node.confidence < filters.minConfidence) return false;
      
      return true;
    });

    // Limit nodes
    filteredNodes = filteredNodes.slice(0, filters.maxNodes);
    
    // Filter edges to only include connections between remaining nodes
    const nodeIds = new Set(filteredNodes.map(n => n.id));
    let filteredEdges = data.edges.filter(edge => {
      const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id;
      const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id;
      return nodeIds.has(sourceId) && nodeIds.has(targetId);
    });

    // Remove isolated nodes if not wanted
    if (!filters.showIsolatedNodes) {
      const connectedNodeIds = new Set<string>();
      filteredEdges.forEach(edge => {
        const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id;
        const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id;
        connectedNodeIds.add(sourceId);
        connectedNodeIds.add(targetId);
      });
      
      filteredNodes = filteredNodes.filter(node => connectedNodeIds.has(node.id));
    }

    return {
      nodes: filteredNodes,
      edges: filteredEdges,
      metadata: data.metadata
    };
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleNodeClick = useCallback((node: GraphNode) => {
    setSelectedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(node.id)) {
        newSet.delete(node.id);
      } else {
        newSet.add(node.id);
      }
      return newSet;
    });
    
    // Find the original entity data for the selected node
    const entity = results.find(e => e.kg_id === node.id);
    if (entity) {
      setSelectedEntity(entity);
    }
  }, [results]);

  const handleNodeHover = useCallback((node: GraphNode | null) => {
    // Could add hover effects here
  }, []);

  const handleGraphConfigChange = (newConfig: Partial<GraphConfig>) => {
    setGraphConfig(prev => ({ ...prev, ...newConfig }));
  };

  const handleGraphFiltersChange = (newFilters: Partial<FilterConfig>) => {
    const updatedFilters = { ...graphFilters, ...newFilters };
    setGraphFilters(updatedFilters);
    
    // Reapply filters to existing data
    if (graphData.nodes.length > 0) {
      const filteredData = applyFiltersToGraphData(graphData, updatedFilters);
      setGraphData(filteredData);
    }
  };

  const handleGraphExport = (format: 'png' | 'svg' | 'json') => {
    // Implementation for graph export
    console.log(`Exporting graph as ${format}`);
  };

  const handleGraphReset = () => {
    setGraphConfig(DEFAULT_GRAPH_CONFIG);
    setGraphFilters(DEFAULT_FILTERS);
    setSelectedNodes(new Set());
    setCenterEntity(null);
    loadGraphData();
  };

  const getEntityIcon = (type: string) => {
    const entityType = ENTITY_TYPES.find(t => t.value === type);
    return entityType ? entityType.icon : Filter;
  };

  const getEntityColor = (type: string) => {
    const colors: Record<string, string> = {
      'Person': 'text-blue-600 bg-blue-50 border-blue-200',
      'Place': 'text-green-600 bg-green-50 border-green-200',
      'Event': 'text-purple-600 bg-purple-50 border-purple-200',
      'Object': 'text-orange-600 bg-orange-50 border-orange-200',
      'Concept': 'text-pink-600 bg-pink-50 border-pink-200'
    };
    return colors[type] || 'text-gray-600 bg-gray-50 border-gray-200';
  };

  const formatEntityId = (kg_id: string) => {
    return kg_id.replace('http://ramayanam.hanuma.com/entity/', '');
  };

  return (
    <div className="space-y-6" data-testid="enhanced-knowledge-graph-search">
      {/* Header with Statistics */}
      {statistics && (
        <div className="bg-gradient-to-r from-orange-50 to-yellow-50 dark:from-gray-800 dark:to-gray-700 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
              Enhanced Knowledge Graph Explorer
            </h2>
            <div className="flex space-x-2">
              <button
                onClick={() => setViewMode('search')}
                className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
                  viewMode === 'search'
                    ? 'bg-orange-500 text-white'
                    : 'bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                }`}
              >
                <Search className="w-4 h-4" />
                <span>Search</span>
              </button>
              <button
                onClick={() => setViewMode('browse')}
                className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
                  viewMode === 'browse'
                    ? 'bg-orange-500 text-white'
                    : 'bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                }`}
              >
                <List className="w-4 h-4" />
                <span>Browse</span>
              </button>
              <button
                onClick={() => setViewMode('graph')}
                className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
                  viewMode === 'graph'
                    ? 'bg-orange-500 text-white'
                    : 'bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                }`}
              >
                <Network className="w-4 h-4" />
                <span>Graph</span>
              </button>
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3">
              <div className="text-2xl font-bold text-orange-600">{statistics.total_entities}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Total Entities</div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3">
              <div className="text-2xl font-bold text-blue-600">{(statistics.total_mentions || 0).toLocaleString()}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Text Mentions</div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3">
              <div className="text-2xl font-bold text-green-600">{statistics.entity_counts?.Person || 0}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">People</div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3">
              <div className="text-2xl font-bold text-purple-600">{statistics.entity_counts?.Place || 0}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Places</div>
            </div>
          </div>
        </div>
      )}

      {/* Graph Visualization View */}
      {viewMode === 'graph' && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Graph Controls */}
          <div className="lg:col-span-1">
            <GraphControls
              config={graphConfig}
              filters={graphFilters}
              onConfigChange={handleGraphConfigChange}
              onFiltersChange={handleGraphFiltersChange}
              onExport={handleGraphExport}
              onReset={handleGraphReset}
            />
          </div>
          
          {/* Graph Visualization */}
          <div className="lg:col-span-3">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
              <div className="h-[600px]">
                {loading ? (
                  <div className="flex items-center justify-center h-full">
                    <LoadingSpinner />
                  </div>
                ) : graphData.nodes.length > 0 ? (
                  <GraphVisualization
                    data={graphData}
                    config={graphConfig}
                    eventHandlers={{
                      onNodeClick: handleNodeClick,
                      onNodeHover: handleNodeHover,
                      onBackgroundClick: () => setSelectedNodes(new Set())
                    }}
                    className="w-full h-full"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
                    <div className="text-center">
                      <Network className="w-16 h-16 mx-auto mb-4 opacity-50" />
                      <p>No graph data available</p>
                      <button
                        onClick={loadGraphData}
                        className="mt-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                      >
                        Load Graph Data
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search Interface - Original implementation for other modes */}
      {(viewMode === 'search' || viewMode === 'browse') && (
        <>
          {viewMode === 'search' && (
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Search Knowledge Graph
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-orange-500 w-5 h-5" />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Search entities like 'rama', 'sita', 'ayodhya', 'dharma'..."
                    className="w-full pl-12 pr-12 py-4 rounded-xl text-lg font-medium placeholder-gray-500 dark:placeholder-gray-400 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-600 focus:outline-none focus:border-orange-400 focus:ring-2 focus:ring-orange-400/20 transition-colors"
                    disabled={loading}
                    data-testid="kg-search-input"
                  />
                  {query && (
                    <button
                      onClick={() => {
                        setQuery('');
                        setResults([]);
                      }}
                      className="absolute right-12 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  )}
                  <button
                    onClick={handleSearch}
                    disabled={loading || !query.trim()}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-orange-500 hover:text-orange-600 dark:hover:text-orange-400 disabled:text-gray-300 dark:disabled:text-gray-600"
                    aria-label="Search"
                  >
                    <Search className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <Filter className="w-4 h-4" />
                  <span>Entity Type</span>
                  <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
                </button>

                <select
                  value={entityType}
                  onChange={(e) => setEntityType(e.target.value)}
                  className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-400"
                >
                  {ENTITY_TYPES.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>

                <div className="text-sm text-gray-500 dark:text-gray-400 ml-auto hidden lg:block">
                  💡 Try searching for: "rama", "sita", "ayodhya", "dharma"
                </div>
              </div>
            </div>
          )}

          {/* Loading */}
          {loading && <LoadingSpinner />}

          {/* Error */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg p-4">
              <div className="text-red-600 dark:text-red-300">{error}</div>
            </div>
          )}

          {/* Results */}
          {results.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                  {viewMode === 'search' ? `Search Results (${results.length})` : `All Entities (${results.length})`}
                </h3>
                {viewMode === 'search' && (
                  <button
                    onClick={() => {
                      setCenterEntity(query);
                      setViewMode('graph');
                    }}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/50 rounded-lg transition-colors"
                  >
                    <Network className="w-4 h-4" />
                    <span>View as Graph</span>
                  </button>
                )}
              </div>

              <div className="grid gap-4">
                {results.map((entity) => {
                  const IconComponent = getEntityIcon(entity.entity_type);
                  const colorClass = getEntityColor(entity.entity_type);
                  
                  return (
                    <div
                      key={entity.kg_id}
                      className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${colorClass}`}>
                              <IconComponent className="w-3 h-3 mr-1" />
                              {entity.entity_type}
                            </span>
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              ID: {formatEntityId(entity.kg_id)}
                            </span>
                          </div>
                          
                          <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-1">
                            {entity.labels.en}
                          </h4>
                          
                          {entity.labels.sa && (
                            <p className="text-gray-600 dark:text-gray-400 sanskrit-text mb-2">
                              {entity.labels.sa}
                            </p>
                          )}

                          {entity.properties.epithets && entity.properties.epithets.length > 0 && (
                            <div className="mb-2">
                              <span className="text-sm text-gray-500 dark:text-gray-400">Epithets: </span>
                              <span className="text-sm text-gray-700 dark:text-gray-300 sanskrit-text">
                                {entity.properties.epithets.join(', ')}
                              </span>
                            </div>
                          )}

                          <div className="flex gap-4 text-sm text-gray-500 dark:text-gray-400">
                            {entity.properties.occurrence_count && (
                              <span>Mentions: {(entity.properties.occurrence_count || 0).toLocaleString()}</span>
                            )}
                            {entity.properties.confidence_score && (
                              <span>Confidence: {(entity.properties.confidence_score * 100).toFixed(0)}%</span>
                            )}
                          </div>
                        </div>

                        <div className="flex space-x-2">
                          <button
                            onClick={() => {
                              setCenterEntity(entity.kg_id);
                              setViewMode('graph');
                            }}
                            className="flex items-center space-x-1 px-3 py-1 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                          >
                            <Network className="w-4 h-4" />
                            <span className="text-sm">Graph</span>
                          </button>
                          <button
                            onClick={() => setSelectedEntity(entity)}
                            className="flex items-center space-x-1 px-3 py-1 text-orange-600 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-orange-900/20 rounded-lg transition-colors"
                          >
                            <Eye className="w-4 h-4" />
                            <span className="text-sm">Details</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Empty State */}
          {!loading && results.length === 0 && viewMode === 'search' && query && (
            <div className="text-center py-12">
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-8 max-w-md mx-auto">
                <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  No entities found
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                  Try searching for character names like "rama" or "sita", places like "ayodhya", or concepts like "dharma".
                </p>
              </div>
            </div>
          )}
        </>
      )}

      {/* Entity Details Modal - Enhanced with graph navigation */}
      {selectedEntity && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                Entity Details
              </h3>
              <button
                onClick={() => setSelectedEntity(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <strong className="text-gray-700 dark:text-gray-300">Name:</strong>
                <span className="ml-2 text-gray-900 dark:text-gray-100">{selectedEntity.labels.en}</span>
              </div>
              
              {selectedEntity.labels.sa && (
                <div>
                  <strong className="text-gray-700 dark:text-gray-300">Sanskrit:</strong>
                  <span className="ml-2 text-gray-900 dark:text-gray-100 sanskrit-text">{selectedEntity.labels.sa}</span>
                </div>
              )}
              
              <div>
                <strong className="text-gray-700 dark:text-gray-300">Type:</strong>
                <span className="ml-2 text-gray-900 dark:text-gray-100">{selectedEntity.entity_type}</span>
              </div>
              
              <div>
                <strong className="text-gray-700 dark:text-gray-300">URI:</strong>
                <span className="ml-2 text-gray-900 dark:text-gray-100 text-sm font-mono break-all">{selectedEntity.kg_id}</span>
              </div>
              
              {selectedEntity.properties.epithets && (
                <div>
                  <strong className="text-gray-700 dark:text-gray-300">Epithets:</strong>
                  <div className="mt-1 flex flex-wrap gap-2">
                    {selectedEntity.properties.epithets.map((epithet, index) => (
                      <span key={index} className="px-2 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-200 rounded text-sm sanskrit-text">
                        {epithet}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                {selectedEntity.properties.occurrence_count && (
                  <div>
                    <strong className="text-gray-700 dark:text-gray-300">Occurrences:</strong>
                    <div className="text-2xl font-bold text-orange-600">{(selectedEntity.properties.occurrence_count || 0).toLocaleString()}</div>
                  </div>
                )}
                {selectedEntity.properties.confidence_score && (
                  <div>
                    <strong className="text-gray-700 dark:text-gray-300">Confidence:</strong>
                    <div className="text-2xl font-bold text-green-600">{(selectedEntity.properties.confidence_score * 100).toFixed(0)}%</div>
                  </div>
                )}
              </div>
              
              {/* Graph Navigation Button */}
              <div className="pt-4 border-t border-gray-200 dark:border-gray-600">
                <button
                  onClick={() => {
                    setCenterEntity(selectedEntity.kg_id);
                    setSelectedEntity(null);
                    setViewMode('graph');
                  }}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/50 rounded-lg transition-colors"
                >
                  <Network className="w-5 h-5" />
                  <span>Explore in Graph View</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedKnowledgeGraphSearch;