import React, { useState } from 'react';
import { 
  Settings, 
  Layout, 
  Filter, 
  Download, 
  Search, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw,
  Users,
  MapPin,
  Calendar,
  Package,
  Brain,
  Eye,
  EyeOff,
  Sliders,
  ChevronDown,
  X
} from 'lucide-react';
import { LayoutType, EntityType, FilterConfig, GraphConfig } from './types';

interface GraphControlsProps {
  config: GraphConfig;
  filters: FilterConfig;
  onConfigChange: (config: Partial<GraphConfig>) => void;
  onFiltersChange: (filters: Partial<FilterConfig>) => void;
  onExport?: (format: 'png' | 'svg' | 'json') => void;
  onReset?: () => void;
  className?: string;
}

const LAYOUT_OPTIONS: { value: LayoutType; label: string; icon: React.ComponentType<any> }[] = [
  { value: 'force', label: 'Force-Directed', icon: Layout },
  { value: 'hierarchical', label: 'Hierarchical', icon: Layout },
  { value: 'radial', label: 'Radial', icon: Layout },
  { value: 'circular', label: 'Circular', icon: Layout }
];

const ENTITY_TYPES: { value: EntityType; label: string; icon: React.ComponentType<any> }[] = [
  { value: 'Person', label: 'People', icon: Users },
  { value: 'Place', label: 'Places', icon: MapPin },
  { value: 'Event', label: 'Events', icon: Calendar },
  { value: 'Object', label: 'Objects', icon: Package },
  { value: 'Concept', label: 'Concepts', icon: Brain }
];

export const GraphControls: React.FC<GraphControlsProps> = ({
  config,
  filters,
  onConfigChange,
  onFiltersChange,
  onExport,
  onReset,
  className = ''
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [showExport, setShowExport] = useState(false);

  const handleLayoutChange = (layout: LayoutType) => {
    onConfigChange({ layout });
  };

  const handleEntityTypeToggle = (entityType: EntityType) => {
    const newTypes = filters.entityTypes.includes(entityType)
      ? filters.entityTypes.filter(t => t !== entityType)
      : [...filters.entityTypes, entityType];
    onFiltersChange({ entityTypes: newTypes });
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4 space-y-4 ${className}`} data-testid="graph-controls">
      
      {/* Layout Controls */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
          <Layout className="w-4 h-4 mr-2" />
          Layout
        </h3>
        <div className="grid grid-cols-2 gap-2">
          {LAYOUT_OPTIONS.map(({ value, label, icon: Icon }) => (
            <button
              key={value}
              onClick={() => handleLayoutChange(value)}
              className={`
                flex items-center justify-center space-x-2 px-3 py-2 rounded-lg text-sm transition-colors
                ${config.layout === value
                  ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 border border-orange-300 dark:border-orange-600'
                  : 'bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-600 border border-gray-200 dark:border-gray-600'
                }
              `}
            >
              <Icon className="w-4 h-4" />
              <span className="hidden sm:inline">{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Visual Controls */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
          <Eye className="w-4 h-4 mr-2" />
          Display
        </h3>
        <div className="space-y-2">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={config.showLabels}
              onChange={(e) => onConfigChange({ showLabels: e.target.checked })}
              className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">Show Labels</span>
          </label>
          
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={config.showEdgeLabels}
              onChange={(e) => onConfigChange({ showEdgeLabels: e.target.checked })}
              className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">Show Edge Labels</span>
          </label>
        </div>
      </div>

      {/* Entity Filters */}
      <div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="w-full flex items-center justify-between text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3"
        >
          <div className="flex items-center">
            <Filter className="w-4 h-4 mr-2" />
            Entity Filters
            {filters.entityTypes.length < ENTITY_TYPES.length && (
              <span className="ml-2 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 px-2 py-1 rounded-full text-xs">
                {filters.entityTypes.length} of {ENTITY_TYPES.length}
              </span>
            )}
          </div>
          <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </button>
        
        {showFilters && (
          <div className="space-y-3">
            {/* Entity Type Toggles */}
            <div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">Entity Types</div>
              <div className="grid grid-cols-1 gap-2">
                {ENTITY_TYPES.map(({ value, label, icon: Icon }) => (
                  <label key={value} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={filters.entityTypes.includes(value)}
                      onChange={() => handleEntityTypeToggle(value)}
                      className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
                    />
                    <Icon className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Numeric Filters */}
            <div className="space-y-3">
              <div>
                <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                  Min Mentions: {filters.minMentions}
                </label>
                <input
                  type="range"
                  min="1"
                  max="100"
                  value={filters.minMentions}
                  onChange={(e) => onFiltersChange({ minMentions: parseInt(e.target.value) })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                  Min Confidence: {(filters.minConfidence * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={filters.minConfidence * 100}
                  onChange={(e) => onFiltersChange({ minConfidence: parseInt(e.target.value) / 100 })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                  Max Nodes: {filters.maxNodes}
                </label>
                <input
                  type="range"
                  min="10"
                  max="200"
                  value={filters.maxNodes}
                  onChange={(e) => onFiltersChange({ maxNodes: parseInt(e.target.value) })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={filters.showIsolatedNodes}
                  onChange={(e) => onFiltersChange({ showIsolatedNodes: e.target.checked })}
                  className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">Show Isolated Nodes</span>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Advanced Controls */}
      <div>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="w-full flex items-center justify-between text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3"
        >
          <div className="flex items-center">
            <Sliders className="w-4 h-4 mr-2" />
            Advanced
          </div>
          <ChevronDown className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
        </button>
        
        {showAdvanced && (
          <div className="space-y-3">
            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                Link Distance: {config.linkDistance}
              </label>
              <input
                type="range"
                min="50"
                max="300"
                value={config.linkDistance}
                onChange={(e) => onConfigChange({ linkDistance: parseInt(e.target.value) })}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                Charge Strength: {Math.abs(config.chargeStrength)}
              </label>
              <input
                type="range"
                min="100"
                max="800"
                value={Math.abs(config.chargeStrength)}
                onChange={(e) => onConfigChange({ chargeStrength: -parseInt(e.target.value) })}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                Color Scheme
              </label>
              <select
                value={config.colorScheme}
                onChange={(e) => onConfigChange({ colorScheme: e.target.value as 'default' | 'type' | 'confidence' })}
                className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-sm"
              >
                <option value="default">Default</option>
                <option value="type">By Entity Type</option>
                <option value="confidence">By Confidence</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-2 pt-3 border-t border-gray-200 dark:border-gray-600">
        {/* Export Button */}
        <div className="relative">
          <button
            onClick={() => setShowExport(!showExport)}
            className="flex items-center space-x-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/50 rounded-lg transition-colors text-sm"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
          
          {showExport && (
            <div className="absolute bottom-full left-0 mb-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2 z-10">
              {['png', 'svg', 'json'].map((format) => (
                <button
                  key={format}
                  onClick={() => {
                    onExport?.(format as 'png' | 'svg' | 'json');
                    setShowExport(false);
                  }}
                  className="block w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  Export as {format.toUpperCase()}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Reset Button */}
        <button
          onClick={onReset}
          className="flex items-center space-x-2 px-3 py-2 bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Reset</span>
        </button>
      </div>
    </div>
  );
};

export default GraphControls;