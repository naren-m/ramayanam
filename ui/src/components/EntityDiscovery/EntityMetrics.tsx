import React from 'react';
import { BarChart3, TrendingUp, Target, Users, MapPin, Calendar, BookOpen, Zap } from 'lucide-react';

interface EntityMetricsProps {
  statistics?: {
    entityTypeCounts: Record<string, number>;
    confidenceDistribution: Record<string, number>;
    processingStats: {
      totalProcessingTime: number;
      averageConfidence: number;
      patternsMatched: number;
      uniqueEntitiesFound: number;
    };
  };
  className?: string;
}

export const EntityMetrics: React.FC<EntityMetricsProps> = ({
  statistics,
  className = ''
}) => {
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  const formatTime = (minutes: number) => {
    if (minutes < 60) return `${Math.round(minutes)}m`;
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return `${hours}h ${mins}m`;
  };

  const entityTypeIcons = {
    Person: Users,
    Place: MapPin,
    Event: Calendar,
    Object: Target,
    Concept: BookOpen
  };

  const entityTypeColors = {
    Person: 'text-blue-600 bg-blue-100 dark:bg-blue-900/30',
    Place: 'text-green-600 bg-green-100 dark:bg-green-900/30',
    Event: 'text-purple-600 bg-purple-100 dark:bg-purple-900/30',
    Object: 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30',
    Concept: 'text-indigo-600 bg-indigo-100 dark:bg-indigo-900/30'
  };

  if (!statistics) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600 ${className}`}>
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <BarChart3 className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p>No metrics data available</p>
        </div>
      </div>
    );
  }

  const totalEntities = Object.values(statistics.entityTypeCounts).reduce((sum, count) => sum + count, 0);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Entity Type Overview */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            Entity Distribution
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {Object.entries(statistics.entityTypeCounts).map(([type, count]) => {
            const IconComponent = entityTypeIcons[type as keyof typeof entityTypeIcons] || Target;
            const colorClass = entityTypeColors[type as keyof typeof entityTypeColors] || 'text-gray-600 bg-gray-100 dark:bg-gray-700';
            const percentage = totalEntities > 0 ? ((count / totalEntities) * 100).toFixed(1) : '0';

            return (
              <div
                key={type}
                className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 text-center"
              >
                <div className={`inline-flex p-3 rounded-full ${colorClass} mb-3`}>
                  <IconComponent className="w-6 h-6" />
                </div>
                <div className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-1">
                  {formatNumber(count)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  {type}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-500">
                  {percentage}%
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Processing Statistics */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            Processing Statistics
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="bg-green-100 dark:bg-green-900/30 rounded-full p-3 inline-flex mb-3">
              <Zap className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-1">
              {formatTime(statistics.processingStats.totalProcessingTime)}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Processing Time
            </div>
          </div>

          <div className="text-center">
            <div className="bg-blue-100 dark:bg-blue-900/30 rounded-full p-3 inline-flex mb-3">
              <Target className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-1">
              {(statistics.processingStats.averageConfidence * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Avg Confidence
            </div>
          </div>

          <div className="text-center">
            <div className="bg-purple-100 dark:bg-purple-900/30 rounded-full p-3 inline-flex mb-3">
              <BarChart3 className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-1">
              {formatNumber(statistics.processingStats.patternsMatched)}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Patterns Matched
            </div>
          </div>

          <div className="text-center">
            <div className="bg-orange-100 dark:bg-orange-900/30 rounded-full p-3 inline-flex mb-3">
              <Users className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-1">
              {formatNumber(statistics.processingStats.uniqueEntitiesFound)}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Unique Entities
            </div>
          </div>
        </div>
      </div>

      {/* Confidence Distribution */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
        <div className="flex items-center gap-2 mb-4">
          <Target className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            Confidence Distribution
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {Object.entries(statistics.confidenceDistribution).map(([range, count]) => {
            const colors = {
              '90-100%': 'bg-green-500 text-white',
              '80-89%': 'bg-blue-500 text-white',
              '70-79%': 'bg-yellow-500 text-white',
              '60-69%': 'bg-orange-500 text-white',
              '0-59%': 'bg-red-500 text-white'
            };
            
            const colorClass = colors[range as keyof typeof colors] || 'bg-gray-500 text-white';
            
            return (
              <div
                key={range}
                className={`p-4 rounded-lg text-center ${colorClass}`}
              >
                <div className="text-2xl font-bold mb-1">
                  {formatNumber(count)}
                </div>
                <div className="text-sm opacity-90">
                  {range}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default EntityMetrics;