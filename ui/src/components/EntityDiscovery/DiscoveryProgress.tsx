import React from 'react';
import { 
  TrendingUp, 
  Clock, 
  Database, 
  CheckCircle, 
  AlertCircle,
  BarChart3,
  Activity,
  Target,
  Zap
} from 'lucide-react';

interface DiscoveryProgressProps {
  progress?: {
    percentage: number;
    currentKanda?: string;
    currentSarga?: string;
    processedSlokas: number;
    totalSlokas: number;
    entitiesFound: number;
    processingRate: number; // slokas per minute
    estimatedTimeRemaining: number; // minutes
    status: 'running' | 'paused' | 'completed' | 'error';
  };
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
  isRunning: boolean;
}

export const DiscoveryProgress: React.FC<DiscoveryProgressProps> = ({
  progress,
  statistics,
  isRunning
}) => {
  const formatTime = (minutes: number) => {
    if (minutes < 60) return `${Math.round(minutes)}m`;
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return `${hours}h ${mins}m`;
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 50) return 'bg-orange-500';
    return 'bg-blue-500';
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'running': return <Activity className="w-5 h-5 text-green-500 animate-pulse" />;
      case 'paused': return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'completed': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error': return <AlertCircle className="w-5 h-5 text-red-500" />;
      default: return <Database className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6" data-testid="discovery-progress">
      {/* Main Progress Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            {getStatusIcon(progress?.status)}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                Discovery Progress
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {progress?.status === 'running' && 'Processing corpus...'}
                {progress?.status === 'paused' && 'Discovery paused'}
                {progress?.status === 'completed' && 'Discovery completed'}
                {progress?.status === 'error' && 'Discovery encountered an error'}
                {!progress?.status && 'Ready to start discovery'}
              </p>
            </div>
          </div>
          
          {progress && (
            <div className="text-right">
              <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                {progress.percentage.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Complete
              </div>
            </div>
          )}
        </div>

        {/* Progress Bar */}
        {progress && (
          <div className="mb-6">
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
              <div 
                className={`h-3 rounded-full transition-all duration-300 ${getProgressColor(progress.percentage)}`}
                style={{ width: `${progress.percentage}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
              <span>{formatNumber(progress.processedSlokas)} processed</span>
              <span>{formatNumber(progress.totalSlokas)} total slokas</span>
            </div>
          </div>
        )}

        {/* Current Status */}
        {progress && isRunning && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Database className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <span className="text-sm font-medium text-blue-800 dark:text-blue-200">Current Location</span>
              </div>
              <div className="text-blue-600 dark:text-blue-400">
                <div className="font-semibold">{progress.currentKanda}</div>
                <div className="text-sm">Sarga {progress.currentSarga}</div>
              </div>
            </div>

            <div className="bg-green-50 dark:bg-green-900/30 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="w-4 h-4 text-green-600 dark:text-green-400" />
                <span className="text-sm font-medium text-green-800 dark:text-green-200">Processing Rate</span>
              </div>
              <div className="text-green-600 dark:text-green-400">
                <div className="font-semibold">{progress.processingRate.toFixed(1)}</div>
                <div className="text-sm">slokas/min</div>
              </div>
            </div>

            <div className="bg-orange-50 dark:bg-orange-900/30 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-orange-600 dark:text-orange-400" />
                <span className="text-sm font-medium text-orange-800 dark:text-orange-200">Time Remaining</span>
              </div>
              <div className="text-orange-600 dark:text-orange-400">
                <div className="font-semibold">{formatTime(progress.estimatedTimeRemaining)}</div>
                <div className="text-sm">estimated</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Entity Type Distribution */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            <h4 className="font-semibold text-gray-800 dark:text-gray-200">Entity Types Found</h4>
          </div>
          
          {statistics?.entityTypeCounts ? (
            <div className="space-y-3">
              {Object.entries(statistics.entityTypeCounts).map(([type, count]) => {
                const total = Object.values(statistics.entityTypeCounts).reduce((sum, c) => sum + c, 0);
                const percentage = total > 0 ? (count / total) * 100 : 0;
                const colors = {
                  Person: 'bg-blue-500',
                  Place: 'bg-green-500',
                  Event: 'bg-purple-500',
                  Object: 'bg-yellow-500',
                  Concept: 'bg-indigo-500'
                };
                
                return (
                  <div key={type} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${colors[type as keyof typeof colors] || 'bg-gray-500'}`} />
                      <span className="text-sm text-gray-600 dark:text-gray-400">{type}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${colors[type as keyof typeof colors] || 'bg-gray-500'}`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-800 dark:text-gray-200 w-8 text-right">
                        {formatNumber(count)}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-4 text-gray-500 dark:text-gray-400">
              <BarChart3 className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No data available</p>
            </div>
          )}
        </div>

        {/* Processing Statistics */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            <h4 className="font-semibold text-gray-800 dark:text-gray-200">Processing Statistics</h4>
          </div>
          
          {statistics?.processingStats ? (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Total Processing Time</span>
                <span className="font-medium text-gray-800 dark:text-gray-200">
                  {formatTime(statistics.processingStats.totalProcessingTime)}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Average Confidence</span>
                <span className="font-medium text-gray-800 dark:text-gray-200">
                  {(statistics.processingStats.averageConfidence * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Patterns Matched</span>
                <span className="font-medium text-gray-800 dark:text-gray-200">
                  {formatNumber(statistics.processingStats.patternsMatched)}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Unique Entities</span>
                <span className="font-medium text-gray-800 dark:text-gray-200">
                  {formatNumber(statistics.processingStats.uniqueEntitiesFound)}
                </span>
              </div>
              
              {progress && (
                <div className="pt-2 border-t border-gray-200 dark:border-gray-600">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Entities Found This Session</span>
                    <span className="font-medium text-orange-600 dark:text-orange-400">
                      {formatNumber(progress.entitiesFound)}
                    </span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-4 text-gray-500 dark:text-gray-400">
              <TrendingUp className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No statistics available</p>
            </div>
          )}
        </div>
      </div>

      {/* Confidence Distribution */}
      {statistics?.confidenceDistribution && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
          <div className="flex items-center gap-2 mb-4">
            <Target className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            <h4 className="font-semibold text-gray-800 dark:text-gray-200">Confidence Distribution</h4>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {Object.entries(statistics.confidenceDistribution).map(([range, count]) => {
              const colors = {
                '90-100%': 'bg-green-500 text-green-100',
                '80-89%': 'bg-blue-500 text-blue-100',
                '70-79%': 'bg-yellow-500 text-yellow-100',
                '60-69%': 'bg-orange-500 text-orange-100',
                '0-59%': 'bg-red-500 text-red-100'
              };
              
              return (
                <div key={range} className={`p-4 rounded-lg ${colors[range as keyof typeof colors] || 'bg-gray-500 text-gray-100'}`}>
                  <div className="text-lg font-bold">{formatNumber(count)}</div>
                  <div className="text-sm opacity-90">{range}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default DiscoveryProgress;