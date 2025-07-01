import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, X, Check } from 'lucide-react';

interface Option {
  value: string | number;
  label: string;
  description?: string;
  disabled?: boolean;
}

interface MultiSelectProps {
  options: Option[];
  selectedValues: (string | number)[];
  onChange: (values: (string | number)[]) => void;
  placeholder?: string;
  maxDisplayed?: number;
  className?: string;
  disabled?: boolean;
  searchable?: boolean;
}

export const MultiSelect: React.FC<MultiSelectProps> = ({
  options,
  selectedValues,
  onChange,
  placeholder = "Select options...",
  maxDisplayed = 3,
  className = "",
  disabled = false,
  searchable = false
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredOptions = searchable ? 
    options.filter(option => 
      option.label.toLowerCase().includes(searchQuery.toLowerCase())
    ) : options;

  const handleToggleOption = (value: string | number) => {
    if (selectedValues.includes(value)) {
      onChange(selectedValues.filter(v => v !== value));
    } else {
      onChange([...selectedValues, value]);
    }
  };

  const handleRemoveValue = (value: string | number) => {
    onChange(selectedValues.filter(v => v !== value));
  };

  const getDisplayText = () => {
    if (selectedValues.length === 0) return placeholder;
    
    const selectedOptions = options.filter(opt => selectedValues.includes(opt.value));
    
    if (selectedValues.length <= maxDisplayed) {
      return selectedOptions.map(opt => opt.label).join(', ');
    }
    
    return `${selectedOptions.slice(0, maxDisplayed).map(opt => opt.label).join(', ')} +${selectedValues.length - maxDisplayed} more`;
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Main Button */}
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`w-full flex items-center justify-between px-4 py-2 text-left bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-400 transition-colors ${
          disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-orange-300'
        }`}
      >
        <span className="flex-1 truncate text-gray-700 dark:text-gray-300">
          {getDisplayText()}
        </span>
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Selected Values Chips */}
      {selectedValues.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {options
            .filter(opt => selectedValues.includes(opt.value))
            .slice(0, maxDisplayed)
            .map(option => (
              <span
                key={option.value}
                className="inline-flex items-center px-2 py-1 text-xs bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-200 rounded-md"
              >
                {option.label}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemoveValue(option.value);
                  }}
                  className="ml-1 hover:text-orange-600 dark:hover:text-orange-100"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          {selectedValues.length > maxDisplayed && (
            <span className="inline-flex items-center px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-md">
              +{selectedValues.length - maxDisplayed} more
            </span>
          )}
        </div>
      )}

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg max-h-64 overflow-hidden">
          {/* Search Input */}
          {searchable && (
            <div className="p-2 border-b border-gray-200 dark:border-gray-600">
              <input
                type="text"
                placeholder="Search options..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    e.stopPropagation();
                    // Don't trigger any action, just prevent default behavior
                    // This prevents the Enter key from interfering with the main search
                  }
                }}
                className="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-md focus:outline-none focus:ring-1 focus:ring-orange-400"
              />
            </div>
          )}

          {/* Options List */}
          <div className="max-h-48 overflow-y-auto">
            {filteredOptions.length === 0 ? (
              <div className="px-3 py-2 text-sm text-gray-500 dark:text-gray-400">
                No options found
              </div>
            ) : (
              filteredOptions.map(option => {
                const isSelected = selectedValues.includes(option.value);
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => !option.disabled && handleToggleOption(option.value)}
                    disabled={option.disabled}
                    className={`w-full flex items-center px-3 py-2 text-left text-sm transition-colors ${
                      option.disabled
                        ? 'opacity-50 cursor-not-allowed'
                        : isSelected
                        ? 'bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-200'
                        : 'hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                    }`}
                  >
                    <div className="flex-1">
                      <div className="font-medium">{option.label}</div>
                      {option.description && (
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                          {option.description}
                        </div>
                      )}
                    </div>
                    {isSelected && (
                      <Check className="w-4 h-4 text-orange-600 dark:text-orange-400" />
                    )}
                  </button>
                );
              })
            )}
          </div>

          {/* Clear All / Select All */}
          {filteredOptions.length > 0 && (
            <div className="p-2 border-t border-gray-200 dark:border-gray-600 flex justify-between">
              <button
                type="button"
                onClick={() => {
                  const allValues = filteredOptions.filter(opt => !opt.disabled).map(opt => opt.value);
                  const hasAll = allValues.every(val => selectedValues.includes(val));
                  if (hasAll) {
                    onChange(selectedValues.filter(val => !allValues.includes(val)));
                  } else {
                    const newValues = [...new Set([...selectedValues, ...allValues])];
                    onChange(newValues);
                  }
                }}
                className="text-xs text-orange-600 dark:text-orange-400 hover:text-orange-700 dark:hover:text-orange-300"
              >
                {filteredOptions.filter(opt => !opt.disabled).every(opt => selectedValues.includes(opt.value)) 
                  ? 'Deselect All' 
                  : 'Select All'
                }
              </button>
              {selectedValues.length > 0 && (
                <button
                  type="button"
                  onClick={() => onChange([])}
                  className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
                >
                  Clear All
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MultiSelect;