import React from 'react';
import { X, RotateCcw } from 'lucide-react';
import { AdvancedSearchFilters, KANDAS } from '../../types/search';

interface FilterChip {
  key: string;
  label: string;
  value: any;
  removable: boolean;
  color?: 'blue' | 'green' | 'purple' | 'orange' | 'gray';
}

interface FilterChipsProps {
  filters: AdvancedSearchFilters;
  onRemoveFilter: (key: string) => void;
  onClearAll: () => void;
  className?: string;
}

export const FilterChips: React.FC<FilterChipsProps> = ({
  filters,
  onRemoveFilter,
  onClearAll,
  className = ''
}) => {
  // Generate filter chips from current filters
  const generateFilterChips = (): FilterChip[] => {
    const chips: FilterChip[] = [];

    // Kanda filters
    if (filters.kanda.length > 0) {
      const kandaNames = filters.kanda
        .map(k => KANDAS.find(kanda => kanda.value === k)?.label || `Kanda ${k}`)
        .join(', ');
      chips.push({
        key: 'kanda',
        label: `Kandas: ${kandaNames}`,
        value: filters.kanda,
        removable: true,
        color: 'blue'
      });
    }

    // Sarga filters
    if (filters.sarga.length > 0) {
      const sargaText = filters.sarga.length <= 3 
        ? `Sargas: ${filters.sarga.join(', ')}`
        : `Sargas: ${filters.sarga.slice(0, 3).join(', ')} +${filters.sarga.length - 3} more`;
      chips.push({
        key: 'sarga',
        label: sargaText,
        value: filters.sarga,
        removable: true,
        color: 'blue'
      });
    }

    // Search mode (if not default)
    if (filters.searchMode !== 'fuzzy') {
      const modeLabels = {
        exact: 'Exact Match',
        semantic: 'Semantic Search',
        fuzzy: 'Fuzzy Search'
      };
      chips.push({
        key: 'searchMode',
        label: `Mode: ${modeLabels[filters.searchMode]}`,
        value: filters.searchMode,
        removable: true,
        color: 'purple'
      });
    }

    // Match ratio (if not default)
    if (filters.minRatio !== 30) {
      chips.push({
        key: 'minRatio',
        label: `Match: ${filters.minRatio}%+`,
        value: filters.minRatio,
        removable: true,
        color: 'purple'
      });
    }

    // Text length filters
    if (filters.textLength.min !== undefined || filters.textLength.max !== undefined) {
      const min = filters.textLength.min || 'any';
      const max = filters.textLength.max || 'any';
      chips.push({
        key: 'textLength',
        label: `Length: ${min} - ${max} words`,
        value: filters.textLength,
        removable: true,
        color: 'green'
      });
    }

    // Sort order (if not default)
    if (filters.sortBy !== 'relevance') {
      const sortLabels = {
        relevance: 'Relevance',
        chronological: 'Chronological',
        textLength: 'Text Length'
      };
      chips.push({
        key: 'sortBy',
        label: `Sort: ${sortLabels[filters.sortBy]}`,
        value: filters.sortBy,
        removable: true,
        color: 'gray'
      });
    }

    // Language filter (if not default)
    if (filters.language !== 'both') {
      const languageLabels = {
        sanskrit: 'Sanskrit Only',
        english: 'English Only',
        both: 'Both Languages'
      };
      chips.push({
        key: 'language',
        label: languageLabels[filters.language],
        value: filters.language,
        removable: true,
        color: 'orange'
      });
    }

    // Annotations (if disabled)
    if (!filters.includeAnnotations) {
      chips.push({
        key: 'includeAnnotations',
        label: 'No Annotations',
        value: false,
        removable: true,
        color: 'gray'
      });
    }

    // Entity filters (when available)
    if (filters.characterFilter.length > 0) {
      const characters = filters.characterFilter.slice(0, 2).join(', ');
      const extra = filters.characterFilter.length > 2 ? ` +${filters.characterFilter.length - 2}` : '';
      chips.push({
        key: 'characterFilter',
        label: `Characters: ${characters}${extra}`,
        value: filters.characterFilter,
        removable: true,
        color: 'blue'
      });
    }

    if (filters.placeFilter.length > 0) {
      const places = filters.placeFilter.slice(0, 2).join(', ');
      const extra = filters.placeFilter.length > 2 ? ` +${filters.placeFilter.length - 2}` : '';
      chips.push({
        key: 'placeFilter',
        label: `Places: ${places}${extra}`,
        value: filters.placeFilter,
        removable: true,
        color: 'green'
      });
    }

    if (filters.conceptFilter.length > 0) {
      const concepts = filters.conceptFilter.slice(0, 2).join(', ');
      const extra = filters.conceptFilter.length > 2 ? ` +${filters.conceptFilter.length - 2}` : '';
      chips.push({
        key: 'conceptFilter',
        label: `Concepts: ${concepts}${extra}`,
        value: filters.conceptFilter,
        removable: true,
        color: 'purple'
      });
    }

    return chips;
  };

  const filterChips = generateFilterChips();

  const getChipColorClasses = (color: string) => {
    const colors = {
      blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 border-blue-200 dark:border-blue-700',
      green: 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 border-green-200 dark:border-green-700',
      purple: 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 border-purple-200 dark:border-purple-700',
      orange: 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-200 border-orange-200 dark:border-orange-700',
      gray: 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border-gray-200 dark:border-gray-600'
    };
    return colors[color] || colors.gray;
  };

  if (filterChips.length === 0) {
    return null;
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Active Filters Header */}
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Active Filters ({filterChips.length})
        </h4>
        <button
          onClick={onClearAll}
          className="flex items-center space-x-1 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Clear All</span>
        </button>
      </div>

      {/* Filter Chips */}
      <div className="flex flex-wrap gap-2">
        {filterChips.map((chip) => (
          <div
            key={chip.key}
            className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium border transition-all hover:shadow-sm ${getChipColorClasses(chip.color || 'gray')}`}
          >
            <span className="truncate max-w-48">{chip.label}</span>
            {chip.removable && (
              <button
                onClick={() => onRemoveFilter(chip.key)}
                className="ml-2 flex-shrink-0 hover:bg-black hover:bg-opacity-10 dark:hover:bg-white dark:hover:bg-opacity-10 rounded-full p-0.5 transition-colors"
                aria-label={`Remove ${chip.label} filter`}
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Filter Summary */}
      {filterChips.length > 3 && (
        <div className="text-xs text-gray-500 dark:text-gray-400">
          Showing results matching all {filterChips.length} active filters
        </div>
      )}
    </div>
  );
};

export default FilterChips;