import React from 'react';
import { Users, MapPin, Calendar, Package, Brain, Star, Eye } from 'lucide-react';
import { GraphNode, EntityType } from './types';

interface EntityNodeProps {
  node: GraphNode;
  isSelected: boolean;
  isHovered: boolean;
  onClick: () => void;
  onHover: (hovered: boolean) => void;
  showDetails?: boolean;
}

const ENTITY_ICONS: Record<EntityType, React.ComponentType<any>> = {
  'Person': Users,
  'Place': MapPin,
  'Event': Calendar,
  'Object': Package,
  'Concept': Brain
};

const ENTITY_COLORS: Record<EntityType, string> = {
  'Person': 'text-blue-600 bg-blue-50 border-blue-200',
  'Place': 'text-green-600 bg-green-50 border-green-200',
  'Event': 'text-purple-600 bg-purple-50 border-purple-200',
  'Object': 'text-orange-600 bg-orange-50 border-orange-200',
  'Concept': 'text-pink-600 bg-pink-50 border-pink-200'
};

export const EntityNode: React.FC<EntityNodeProps> = ({
  node,
  isSelected,
  isHovered,
  onClick,
  onHover,
  showDetails = false
}) => {
  const IconComponent = ENTITY_ICONS[node.type];
  const colorClass = ENTITY_COLORS[node.type];

  const getNodeSize = () => {
    const baseSize = 40;
    const mentionBonus = Math.min(20, Math.sqrt(node.mentions) * 2);
    const relevanceBonus = node.relevance * 10;
    return baseSize + mentionBonus + relevanceBonus;
  };

  const nodeSize = getNodeSize();

  return (
    <div 
      className={`
        relative cursor-pointer transition-all duration-200 transform
        ${isHovered ? 'scale-110 z-10' : 'scale-100'}
        ${isSelected ? 'z-20' : ''}
      `}
      onClick={onClick}
      onMouseEnter={() => onHover(true)}
      onMouseLeave={() => onHover(false)}
      data-testid={`entity-node-${node.id}`}
    >
      {/* Node Circle */}
      <div 
        className={`
          rounded-full border-2 flex items-center justify-center
          transition-all duration-200
          ${colorClass}
          ${isSelected ? 'border-orange-500 border-4 shadow-lg' : ''}
          ${isHovered ? 'shadow-md' : ''}
        `}
        style={{
          width: `${nodeSize}px`,
          height: `${nodeSize}px`
        }}
      >
        <IconComponent 
          className={`w-${Math.max(4, nodeSize / 8)} h-${Math.max(4, nodeSize / 8)}`}
        />
      </div>

      {/* Confidence indicator */}
      {node.confidence && node.confidence > 0.8 && (
        <div className="absolute -top-1 -right-1 bg-yellow-400 rounded-full p-1">
          <Star className="w-3 h-3 text-yellow-800" fill="currentColor" />
        </div>
      )}

      {/* Mention count badge */}
      {node.mentions > 10 && (
        <div className="absolute -bottom-1 -right-1 bg-orange-500 text-white rounded-full text-xs px-2 py-1 font-bold min-w-[20px] text-center">
          {node.mentions > 999 ? '999+' : node.mentions}
        </div>
      )}

      {/* Node Label */}
      <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 text-center">
        <div className="bg-white dark:bg-gray-800 px-2 py-1 rounded-md shadow-sm border border-gray-200 dark:border-gray-600">
          <div className="text-sm font-semibold text-gray-800 dark:text-gray-200 whitespace-nowrap">
            {node.name.length > 15 ? node.name.substring(0, 15) + '...' : node.name}
          </div>
          {node.sanskritName && (
            <div className="text-xs text-gray-500 dark:text-gray-400 sanskrit-text">
              {node.sanskritName.length > 15 ? node.sanskritName.substring(0, 15) + '...' : node.sanskritName}
            </div>
          )}
        </div>
      </div>

      {/* Detailed info panel (on hover) */}
      {showDetails && isHovered && (
        <div className="absolute top-0 left-full ml-4 z-30 w-72">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-600 p-4">
            <div className="flex items-start space-x-3">
              <div className={`p-2 rounded-lg ${colorClass}`}>
                <IconComponent className="w-5 h-5" />
              </div>
              
              <div className="flex-1">
                <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-1">
                  {node.name}
                </h3>
                
                {node.sanskritName && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 sanskrit-text mb-2">
                    {node.sanskritName}
                  </p>
                )}

                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-sm">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${colorClass}`}>
                      {node.type}
                    </span>
                    {node.confidence && (
                      <span className="text-gray-500 dark:text-gray-400">
                        {(node.confidence * 100).toFixed(0)}% confidence
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Mentions:</span>
                      <span className="ml-1 font-medium text-gray-800 dark:text-gray-200">
                        {node.mentions.toLocaleString()}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Relevance:</span>
                      <span className="ml-1 font-medium text-gray-800 dark:text-gray-200">
                        {(node.relevance * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  {node.epithets && node.epithets.length > 0 && (
                    <div>
                      <span className="text-sm text-gray-500 dark:text-gray-400 block mb-1">Epithets:</span>
                      <div className="flex flex-wrap gap-1">
                        {node.epithets.slice(0, 3).map((epithet, index) => (
                          <span 
                            key={index}
                            className="inline-block px-2 py-1 bg-gray-100 dark:bg-gray-700 text-xs text-gray-700 dark:text-gray-300 rounded sanskrit-text"
                          >
                            {epithet}
                          </span>
                        ))}
                        {node.epithets.length > 3 && (
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            +{node.epithets.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Action button */}
            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
              <button 
                className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400 hover:bg-orange-100 dark:hover:bg-orange-900/30 rounded-lg transition-colors text-sm"
                onClick={(e) => {
                  e.stopPropagation();
                  // Handle view details action
                }}
              >
                <Eye className="w-4 h-4" />
                <span>View Details</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EntityNode;