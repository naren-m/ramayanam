import React, { useState } from 'react';
import { Play, Plus, Trash2, Edit3, Bookmark, TrendingUp } from 'lucide-react';
import { SearchPreset, DEFAULT_SEARCH_PRESETS } from '../../types/search';

interface SearchPresetsProps {
  customPresets: SearchPreset[];
  onApplyPreset: (presetId: string) => void;
  onSaveCustomPreset: (name: string, description: string) => void;
  onDeleteCustomPreset: (presetId: string) => void;
  className?: string;
  disabled?: boolean;
}

export const SearchPresets: React.FC<SearchPresetsProps> = ({
  customPresets,
  onApplyPreset,
  onSaveCustomPreset,
  onDeleteCustomPreset,
  className = '',
  disabled = false
}) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newPresetName, setNewPresetName] = useState('');
  const [newPresetDescription, setNewPresetDescription] = useState('');

  const allPresets = [...DEFAULT_SEARCH_PRESETS, ...customPresets];

  const handleCreatePreset = () => {
    if (newPresetName.trim()) {
      onSaveCustomPreset(newPresetName.trim(), newPresetDescription.trim());
      setNewPresetName('');
      setNewPresetDescription('');
      setShowCreateForm(false);
    }
  };

  const handleCancelCreate = () => {
    setNewPresetName('');
    setNewPresetDescription('');
    setShowCreateForm(false);
  };

  const getPresetUsageText = (preset: SearchPreset) => {
    if (!preset.usageCount) return '';
    const count = preset.usageCount;
    if (count === 1) return '1 use';
    if (count < 10) return `${count} uses`;
    if (count < 100) return `${count} uses`;
    return '99+ uses';
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            Search Presets
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Quick access to common search patterns
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          disabled={disabled || showCreateForm}
          className="flex items-center space-x-2 px-3 py-2 text-sm bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Create Custom</span>
        </button>
      </div>

      {/* Create Custom Preset Form */}
      {showCreateForm && (
        <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
          <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-3">
            Create Custom Preset
          </h4>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Preset Name *
              </label>
              <input
                type="text"
                value={newPresetName}
                onChange={(e) => setNewPresetName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    e.stopPropagation();
                    if (newPresetName.trim()) {
                      handleCreatePreset();
                    }
                  }
                }}
                placeholder="e.g., Rama's Speeches in Ayodhya"
                className="w-full px-3 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-md focus:outline-none focus:ring-1 focus:ring-orange-400"
                maxLength={50}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Description (optional)
              </label>
              <input
                type="text"
                value={newPresetDescription}
                onChange={(e) => setNewPresetDescription(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    e.stopPropagation();
                    if (newPresetName.trim()) {
                      handleCreatePreset();
                    }
                  }
                }}
                placeholder="Brief description of this search pattern"
                className="w-full px-3 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-md focus:outline-none focus:ring-1 focus:ring-orange-400"
                maxLength={100}
              />
            </div>
            <div className="flex space-x-2">
              <button
                onClick={handleCreatePreset}
                disabled={!newPresetName.trim()}
                className="flex-1 px-3 py-2 text-sm bg-orange-500 text-white rounded-md hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Save Current Filters as Preset
              </button>
              <button
                onClick={handleCancelCreate}
                className="px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Default Presets */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center">
          <Bookmark className="w-4 h-4 mr-2" />
          Default Presets
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {DEFAULT_SEARCH_PRESETS.map((preset) => (
            <button
              key={preset.id}
              onClick={() => !disabled && onApplyPreset(preset.id)}
              disabled={disabled}
              className="group p-4 text-left bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-orange-300 dark:hover:border-orange-500 hover:shadow-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="flex items-start justify-between mb-2">
                <span className="text-2xl">{preset.icon}</span>
                <Play className="w-4 h-4 text-gray-400 group-hover:text-orange-500 transition-colors" />
              </div>
              <div className="space-y-1">
                <h5 className="font-medium text-gray-800 dark:text-gray-200 group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors">
                  {preset.name}
                </h5>
                <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
                  {preset.description}
                </p>
                {preset.usageCount && (
                  <div className="flex items-center text-xs text-gray-400 dark:text-gray-500">
                    <TrendingUp className="w-3 h-3 mr-1" />
                    {getPresetUsageText(preset)}
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Custom Presets */}
      {customPresets.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center">
            <Edit3 className="w-4 h-4 mr-2" />
            Your Custom Presets ({customPresets.length})
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {customPresets.map((preset) => (
              <div
                key={preset.id}
                className="group p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-orange-300 dark:hover:border-orange-500 hover:shadow-sm transition-all"
              >
                <div className="flex items-start justify-between mb-2">
                  <span className="text-2xl">📝</span>
                  <div className="flex space-x-1">
                    <button
                      onClick={() => !disabled && onApplyPreset(preset.id)}
                      disabled={disabled}
                      className="p-1 text-gray-400 hover:text-orange-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      title="Apply preset"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => !disabled && onDeleteCustomPreset(preset.id)}
                      disabled={disabled}
                      className="p-1 text-gray-400 hover:text-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      title="Delete preset"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="space-y-1">
                  <h5 className="font-medium text-gray-800 dark:text-gray-200">
                    {preset.name}
                  </h5>
                  {preset.description && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
                      {preset.description}
                    </p>
                  )}
                  {preset.usageCount && (
                    <div className="flex items-center text-xs text-gray-400 dark:text-gray-500">
                      <TrendingUp className="w-3 h-3 mr-1" />
                      {getPresetUsageText(preset)}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Custom Presets Message */}
      {customPresets.length === 0 && !showCreateForm && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <Edit3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p className="text-sm">No custom presets yet</p>
          <p className="text-xs mt-1">
            Create your own presets by setting up filters and clicking "Create Custom"
          </p>
        </div>
      )}
    </div>
  );
};

export default SearchPresets;