import React, { useState, useCallback } from 'react';

interface RangeSliderProps {
  min: number;
  max: number;
  value: { min?: number; max?: number };
  onChange: (value: { min?: number; max?: number }) => void;
  step?: number;
  label?: string;
  unit?: string;
  showInput?: boolean;
  className?: string;
  disabled?: boolean;
}

export const RangeSlider: React.FC<RangeSliderProps> = ({
  min,
  max,
  value,
  onChange,
  step = 1,
  label,
  unit = '',
  showInput = true,
  className = '',
  disabled = false
}) => {
  const [isDragging, setIsDragging] = useState<'min' | 'max' | null>(null);

  const minValue = value.min ?? min;
  const maxValue = value.max ?? max;

  const handleMinChange = useCallback((newMin: number) => {
    const clampedMin = Math.max(min, Math.min(newMin, maxValue - step));
    onChange({ ...value, min: clampedMin === min ? undefined : clampedMin });
  }, [min, max, maxValue, step, value, onChange]);

  const handleMaxChange = useCallback((newMax: number) => {
    const clampedMax = Math.min(max, Math.max(newMax, minValue + step));
    onChange({ ...value, max: clampedMax === max ? undefined : clampedMax });
  }, [min, max, minValue, step, value, onChange]);

  const handleInputChange = (type: 'min' | 'max', inputValue: string) => {
    const numValue = parseInt(inputValue) || (type === 'min' ? min : max);
    if (type === 'min') {
      handleMinChange(numValue);
    } else {
      handleMaxChange(numValue);
    }
  };

  const getPercentage = (val: number) => ((val - min) / (max - min)) * 100;

  const minPercentage = getPercentage(minValue);
  const maxPercentage = getPercentage(maxValue);

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Label */}
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
        </label>
      )}

      {/* Range Display */}
      <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
        <span>
          {value.min !== undefined ? `${minValue}${unit}` : `${min}${unit} (any)`}
        </span>
        <span>to</span>
        <span>
          {value.max !== undefined ? `${maxValue}${unit}` : `${max}${unit} (any)`}
        </span>
      </div>

      {/* Slider Container */}
      <div className="relative h-6 flex items-center">
        {/* Track */}
        <div className="absolute w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-full">
          {/* Active Range */}
          <div
            className="absolute h-2 bg-orange-500 rounded-full"
            style={{
              left: `${minPercentage}%`,
              width: `${maxPercentage - minPercentage}%`
            }}
          />
        </div>

        {/* Min Thumb */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={minValue}
          onChange={(e) => handleMinChange(parseInt(e.target.value))}
          onMouseDown={() => setIsDragging('min')}
          onMouseUp={() => setIsDragging(null)}
          disabled={disabled}
          className="absolute w-full h-2 bg-transparent appearance-none cursor-pointer slider-thumb"
          style={{ zIndex: isDragging === 'min' ? 3 : 1 }}
        />

        {/* Max Thumb */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={maxValue}
          onChange={(e) => handleMaxChange(parseInt(e.target.value))}
          onMouseDown={() => setIsDragging('max')}
          onMouseUp={() => setIsDragging(null)}
          disabled={disabled}
          className="absolute w-full h-2 bg-transparent appearance-none cursor-pointer slider-thumb"
          style={{ zIndex: isDragging === 'max' ? 3 : 2 }}
        />
      </div>

      {/* Number Inputs */}
      {showInput && (
        <div className="flex items-center space-x-3">
          <div className="flex-1">
            <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
              Min {unit}
            </label>
            <input
              type="number"
              min={min}
              max={maxValue - step}
              step={step}
              value={value.min !== undefined ? minValue : ''}
              onChange={(e) => handleInputChange('min', e.target.value)}
              placeholder={`${min} (any)`}
              disabled={disabled}
              className="w-full px-3 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-md focus:outline-none focus:ring-1 focus:ring-orange-400"
            />
          </div>
          <div className="flex-1">
            <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
              Max {unit}
            </label>
            <input
              type="number"
              min={minValue + step}
              max={max}
              step={step}
              value={value.max !== undefined ? maxValue : ''}
              onChange={(e) => handleInputChange('max', e.target.value)}
              placeholder={`${max} (any)`}
              disabled={disabled}
              className="w-full px-3 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-md focus:outline-none focus:ring-1 focus:ring-orange-400"
            />
          </div>
        </div>
      )}

      {/* Reset Button */}
      {(value.min !== undefined || value.max !== undefined) && (
        <button
          type="button"
          onClick={() => onChange({ min: undefined, max: undefined })}
          disabled={disabled}
          className="text-xs text-orange-600 dark:text-orange-400 hover:text-orange-700 dark:hover:text-orange-300 disabled:opacity-50"
        >
          Reset to any length
        </button>
      )}

      <style jsx>{`
        .slider-thumb::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #f97316;
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
          cursor: pointer;
        }

        .slider-thumb::-webkit-slider-thumb:hover {
          background: #ea580c;
        }

        .slider-thumb::-webkit-slider-thumb:active {
          background: #dc2626;
          transform: scale(1.1);
        }

        .slider-thumb::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #f97316;
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
          cursor: pointer;
          border: none;
        }

        .slider-thumb::-moz-range-thumb:hover {
          background: #ea580c;
        }

        .slider-thumb::-moz-range-thumb:active {
          background: #dc2626;
          transform: scale(1.1);
        }

        .slider-thumb:disabled::-webkit-slider-thumb {
          background: #9ca3af;
          cursor: not-allowed;
        }

        .slider-thumb:disabled::-moz-range-thumb {
          background: #9ca3af;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default RangeSlider;