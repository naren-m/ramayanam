import React from 'react';

interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  description?: string;
  size?: 'sm' | 'md' | 'lg';
  color?: 'orange' | 'blue' | 'green' | 'purple';
  disabled?: boolean;
  className?: string;
}

export const ToggleSwitch: React.FC<ToggleSwitchProps> = ({
  checked,
  onChange,
  label,
  description,
  size = 'md',
  color = 'orange',
  disabled = false,
  className = ''
}) => {
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return {
          container: 'w-8 h-4',
          thumb: 'w-3 h-3',
          translate: 'translate-x-4'
        };
      case 'lg':
        return {
          container: 'w-12 h-6',
          thumb: 'w-5 h-5',
          translate: 'translate-x-6'
        };
      default:
        return {
          container: 'w-10 h-5',
          thumb: 'w-4 h-4',
          translate: 'translate-x-5'
        };
    }
  };

  const getColorClasses = () => {
    const colors = {
      orange: checked ? 'bg-orange-500' : 'bg-gray-300 dark:bg-gray-600',
      blue: checked ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600',
      green: checked ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600',
      purple: checked ? 'bg-purple-500' : 'bg-gray-300 dark:bg-gray-600'
    };
    return colors[color];
  };

  const sizeClasses = getSizeClasses();
  const colorClasses = getColorClasses();

  const handleToggle = () => {
    if (!disabled) {
      onChange(!checked);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleToggle();
    }
  };

  return (
    <div className={`flex items-center ${className}`}>
      {/* Toggle Switch */}
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-disabled={disabled}
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        className={`
          relative inline-flex items-center rounded-full transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-400 
          ${sizeClasses.container} 
          ${colorClasses}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        <span className="sr-only">
          {label ? `Toggle ${label}` : 'Toggle switch'}
        </span>
        
        {/* Thumb */}
        <span
          className={`
            inline-block bg-white rounded-full shadow-lg transform transition-transform duration-200 ease-in-out
            ${sizeClasses.thumb}
            ${checked ? sizeClasses.translate : 'translate-x-0.5'}
          `}
        />
      </button>

      {/* Label and Description */}
      {(label || description) && (
        <div className="ml-3 flex-1">
          {label && (
            <label
              className={`block text-sm font-medium cursor-pointer ${
                disabled 
                  ? 'text-gray-400 dark:text-gray-500 cursor-not-allowed' 
                  : 'text-gray-700 dark:text-gray-300'
              }`}
              onClick={handleToggle}
            >
              {label}
            </label>
          )}
          {description && (
            <p className={`text-xs mt-1 ${
              disabled 
                ? 'text-gray-400 dark:text-gray-500' 
                : 'text-gray-500 dark:text-gray-400'
            }`}>
              {description}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default ToggleSwitch;