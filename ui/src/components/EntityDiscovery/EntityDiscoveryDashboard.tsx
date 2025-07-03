import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Play, 
  Pause, 
  RotateCcw, 
  Database, 
  TrendingUp, 
  Users, 
  MapPin, 
  Calendar,
  BookOpen,
  Eye,
  CheckCircle,
  XCircle,
  AlertCircle,
  Settings
} from 'lucide-react';
import EntityValidationPanel from './EntityValidationPanel';
import DiscoveryProgress from './DiscoveryProgress';
import EntityMetrics from './EntityMetrics';
import { useEntityDiscovery } from '../../hooks/useEntityDiscovery';

interface EntityDiscoveryDashboardProps {
  className?: string;
}

export const EntityDiscoveryDashboard: React.FC<EntityDiscoveryDashboardProps> = ({
  className = ''
}) => {
  const {
    discoveryProgress,
    pendingEntities,
    validatedEntities,
    conflictingEntities,
    statistics,
    startDiscovery,
    stopDiscovery,
    resetDiscovery,
    isRunning,
    error,
    loading
  } = useEntityDiscovery();

  const [activeTab, setActiveTab] = useState<'overview' | 'progress' | 'validation' | 'settings'>('overview');

  const handleStartDiscovery = async () => {
    try {
      await startDiscovery({
        processAllKandas: true,
        confidence_threshold: 0.7,
        max_entities_per_sloka: 10
      });
    } catch (error) {
      console.error('Failed to start discovery:', error);
    }
  };

  const entityTypeCounts = statistics?.entityTypeCounts || {};
  const totalEntities = Object.values(entityTypeCounts).reduce((sum, count) => sum + count, 0);

  return (
    <div className={`space-y-6 ${className}`} data-testid="entity-discovery-dashboard">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 flex items-center gap-3">
              <Database className="w-7 h-7 text-orange-500" />
              Entity Discovery Module
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              Automatically discover and extract entities from the Ramayana corpus using advanced NLP and AI
            </p>
          </div>
          
          {/* Control Buttons */}
          <div className="flex items-center gap-3">
            <button
              onClick={handleStartDiscovery}
              disabled={isRunning || loading}
              className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white rounded-lg transition-colors"
              data-testid="start-discovery-button"
            >
              <Play className="w-4 h-4" />
              {isRunning ? 'Running...' : 'Start Discovery'}
            </button>
            
            {isRunning && (
              <button
                onClick={stopDiscovery}
                className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
                data-testid="stop-discovery-button"
              >
                <Pause className="w-4 h-4" />
                Stop
              </button>
            )}
            
            <button
              onClick={resetDiscovery}
              disabled={isRunning}
              className="flex items-center gap-2 px-4 py-2 bg-gray-500 hover:bg-gray-600 disabled:bg-gray-400 text-white rounded-lg transition-colors"
              data-testid="reset-discovery-button"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
          </div>
        </div>

        {/* Status Banner */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-600 rounded-lg">
            <div className="flex items-center gap-2 text-red-700 dark:text-red-300">
              <XCircle className="w-5 h-5" />
              <span className="font-medium">Discovery Error:</span>
              <span>{error}</span>
            </div>
          </div>
        )}

        {isRunning && (
          <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-600 rounded-lg">
            <div className="flex items-center gap-2 text-blue-700 dark:text-blue-300">
              <AlertCircle className="w-5 h-5 animate-pulse" />
              <span className="font-medium">Discovery in Progress...</span>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
          {[
            { id: 'overview', label: 'Overview', icon: TrendingUp },
            { id: 'progress', label: 'Progress', icon: RotateCcw },
            { id: 'validation', label: 'Validation', icon: CheckCircle },
            { id: 'settings', label: 'Settings', icon: Settings }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors text-sm font-medium ${
                activeTab === id
                  ? 'bg-white dark:bg-gray-800 text-orange-600 shadow-sm'
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100'
              }`}
              data-testid={`tab-${id}`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Entity Statistics Cards */}
          <div className="space-y-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <Users className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800 dark:text-gray-200">Characters</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">People & Divine Beings</p>
                </div>
              </div>
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {entityTypeCounts.Person || 0}
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                  <MapPin className="w-5 h-5 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800 dark:text-gray-200">Places</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Locations & Regions</p>
                </div>
              </div>
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                {entityTypeCounts.Place || 0}
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  <BookOpen className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800 dark:text-gray-200">Concepts</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Ideas & Principles</p>
                </div>
              </div>
              <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                {entityTypeCounts.Concept || 0}
              </div>
            </div>
          </div>

          {/* Discovery Status */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">Discovery Status</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Total Entities</span>
                <span className="font-semibold text-gray-800 dark:text-gray-200">{totalEntities}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Pending Validation</span>
                <span className="font-semibold text-orange-600 dark:text-orange-400">
                  {pendingEntities?.length || 0}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Validated</span>
                <span className="font-semibold text-green-600 dark:text-green-400">
                  {validatedEntities?.length || 0}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Conflicts</span>
                <span className="font-semibold text-red-600 dark:text-red-400">
                  {conflictingEntities?.length || 0}
                </span>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-600">
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">Discovery Progress</div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-orange-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${discoveryProgress?.percentage || 0}%` }}
                />
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {discoveryProgress?.percentage || 0}% Complete
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">Recent Activity</h3>
            
            <div className="space-y-3">
              {statistics?.recentActivity ? statistics.recentActivity.map((activity: any, index: number) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="p-1 bg-orange-100 dark:bg-orange-900/30 rounded">
                    {activity.type === 'discovery' && <Search className="w-3 h-3 text-orange-600" />}
                    {activity.type === 'validation' && <CheckCircle className="w-3 h-3 text-green-600" />}
                    {activity.type === 'conflict' && <AlertCircle className="w-3 h-3 text-red-600" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-800 dark:text-gray-200 truncate">
                      {activity.message}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {activity.timestamp}
                    </p>
                  </div>
                </div>
              )) : (
                <div className="text-center py-6 text-gray-500 dark:text-gray-400">
                  <Search className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No recent activity</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'progress' && (
        <DiscoveryProgress
          progress={discoveryProgress}
          statistics={statistics}
          isRunning={isRunning}
        />
      )}

      {activeTab === 'validation' && (
        <EntityValidationPanel
          pendingEntities={pendingEntities}
          conflictingEntities={conflictingEntities}
          onValidateEntity={(entityId, validation) => {
            // Handle entity validation
            console.log('Validating entity:', entityId, validation);
          }}
          onResolveConflict={(conflictId, resolution) => {
            // Handle conflict resolution
            console.log('Resolving conflict:', conflictId, resolution);
          }}
        />
      )}

      {activeTab === 'settings' && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">Discovery Settings</h3>
          <p className="text-gray-500 dark:text-gray-400">Settings panel coming soon...</p>
        </div>
      )}
    </div>
  );
};

export default EntityDiscoveryDashboard;