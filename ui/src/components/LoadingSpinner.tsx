import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-gold-200 dark:border-gold-700 rounded-full animate-spin border-t-gold-500 dark:border-t-gold-400"></div>
        <div className="absolute inset-0 w-16 h-16 border-4 border-transparent rounded-full animate-ping border-t-saffron-400 opacity-20"></div>
      </div>
      <div className="mt-6 text-center">
        <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
          Searching the Ancient Verses...
        </h3>
        <p className="text-gray-500 dark:text-gray-400 max-w-md">
          Exploring the vast digital corpus of the Ramayana to find matching verses.
        </p>
      </div>
    </div>
  );
};

export default LoadingSpinner;