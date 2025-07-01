import React from 'react';

interface RadioOption {
  value: string;
  label: string;
  description?: string;
  icon?: React.ComponentType<{ className?: string }>;
  disabled?: boolean;
}

interface RadioGroupProps {
  options: RadioOption[];
  value: string;
  onChange: (value: string) => void;
  name: string;
  label?: string;
  layout?: 'horizontal' | 'vertical' | 'grid';
  className?: string;
  disabled?: boolean;
}

export const RadioGroup: React.FC<RadioGroupProps> = ({
  options,
  value,
  onChange,
  name,
  label,
  layout = 'horizontal',
  className = '',
  disabled = false
}) => {
  const getLayoutClasses = () => {
    switch (layout) {
      case 'vertical':
        return 'flex flex-col space-y-2';
      case 'grid':
        return 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2';
      default:
        return 'flex flex-wrap gap-2';
    }
  };

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Label */}
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
        </label>
      )}

      {/* Radio Options */}
      <div className={getLayoutClasses()}>
        {options.map((option) => {
          const isSelected = value === option.value;
          const isDisabled = disabled || option.disabled;
          const IconComponent = option.icon;

          return (
            <label
              key={option.value}
              className={`relative flex items-center cursor-pointer ${
                isDisabled ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <input
                type="radio"
                name={name}
                value={option.value}
                checked={isSelected}
                onChange={(e) => !isDisabled && onChange(e.target.value)}
                disabled={isDisabled}
                className="sr-only"
              />
              
              <div
                className={`flex items-center w-full px-4 py-3 rounded-lg border-2 transition-all ${
                  isSelected
                    ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/30'
                    : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 hover:border-orange-300 dark:hover:border-orange-500'
                } ${
                  isDisabled ? 'cursor-not-allowed' : 'cursor-pointer'
                }`}
              >
                {/* Custom Radio Button */}
                <div
                  className={`flex-shrink-0 w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center ${
                    isSelected
                      ? 'border-orange-500 bg-orange-500'
                      : 'border-gray-300 dark:border-gray-500 bg-white dark:bg-gray-800'
                  }`}
                >
                  {isSelected && (
                    <div className="w-2 h-2 rounded-full bg-white"></div>
                  )}
                </div>

                {/* Icon */}
                {IconComponent && (
                  <IconComponent
                    className={`w-5 h-5 mr-3 ${
                      isSelected
                        ? 'text-orange-600 dark:text-orange-400'
                        : 'text-gray-400 dark:text-gray-500'
                    }`}
                  />
                )}

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div
                    className={`font-medium ${
                      isSelected
                        ? 'text-orange-700 dark:text-orange-300'
                        : 'text-gray-700 dark:text-gray-300'
                    }`}
                  >
                    {option.label}
                  </div>
                  {option.description && (
                    <div
                      className={`text-sm mt-1 ${
                        isSelected
                          ? 'text-orange-600 dark:text-orange-400'
                          : 'text-gray-500 dark:text-gray-400'
                      }`}
                    >
                      {option.description}
                    </div>
                  )}
                </div>

                {/* Selected Indicator */}
                {isSelected && (
                  <div className="flex-shrink-0 ml-2">
                    <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  </div>
                )}
              </div>
            </label>
          );
        })}
      </div>
    </div>
  );
};

export default RadioGroup;