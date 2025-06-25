import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, BookOpen, Heart, Copy, Share2, ExternalLink, ChevronLeft, ChevronRight, Home } from 'lucide-react';
import { Verse } from '../types';
import { fetchSargaData, SargaData } from '../utils/api';
import LoadingSpinner from './LoadingSpinner';

const SargaView: React.FC = () => {
  const { source, kanda, sarga } = useParams<{
    source: string;
    kanda: string;
    sarga: string;
  }>();
  const navigate = useNavigate();
  
  const [sargaData, setSargaData] = useState<SargaData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentSloka, setCurrentSloka] = useState<number>(0);
  const [favorites, setFavorites] = useState<string[]>([]);

  useEffect(() => {
    const loadSargaData = async () => {
      if (!source || !kanda || !sarga) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const data = await fetchSargaData(source!, kanda!, sarga!);
        setSargaData(data);
        
        // Load favorites from localStorage (namespaced by source)
        const favoritesKey = `${source}-favorites`;
        const savedFavorites = localStorage.getItem(favoritesKey);
        if (savedFavorites) {
          setFavorites(JSON.parse(savedFavorites));
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load sarga');
      } finally {
        setLoading(false);
      }
    };

    loadSargaData();
  }, [source, kanda, sarga]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      // Only handle keys when not typing in an input
      if (event.target instanceof HTMLInputElement) return;
      
      switch (event.key) {
        case 'ArrowLeft':
        case 'h':
          event.preventDefault();
          if (currentSloka > 0) {
            navigateSloka('prev');
          }
          break;
        case 'ArrowRight':
        case 'l':
          event.preventDefault();
          if (sargaData && currentSloka < sargaData.slokas.length - 1) {
            navigateSloka('next');
          }
          break;
        case 'Home':
          event.preventDefault();
          setCurrentSloka(0);
          break;
        case 'End':
          event.preventDefault();
          if (sargaData) {
            setCurrentSloka(sargaData.slokas.length - 1);
          }
          break;
        case 'f':
          event.preventDefault();
          if (sargaData) {
            handleToggleFavorite(sargaData.slokas[currentSloka].sloka_number);
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [currentSloka, sargaData]);

  const handleToggleFavorite = (slokaId: string) => {
    const newFavorites = favorites.includes(slokaId)
      ? favorites.filter(id => id !== slokaId)
      : [...favorites, slokaId];
    
    setFavorites(newFavorites);
    // Use namespaced localStorage key by source
    const favoritesKey = `${source}-favorites`;
    localStorage.setItem(favoritesKey, JSON.stringify(newFavorites));
  };

  const handleCopySloka = async (verse: Verse) => {
    const text = `${verse.sloka}\n\n${verse.translation}\n\n— ${sargaData?.kanda.name} ${sargaData?.sarga.number}.${verse.sloka_number.split('.')[2]}`;
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleShareSloka = async (verse: Verse) => {
    const text = `${verse.sloka}\n\n${verse.translation}\n\n— ${sargaData?.kanda.name} ${sargaData?.sarga.number}.${verse.sloka_number.split('.')[2]}`;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${sargaData?.kanda.name} - Sarga ${sargaData?.sarga.number}`,
          text: text,
        });
      } catch (err) {
        handleCopySloka(verse);
      }
    } else {
      handleCopySloka(verse);
    }
  };

  const navigateSloka = (direction: 'prev' | 'next') => {
    if (!sargaData) return;
    
    if (direction === 'prev' && currentSloka > 0) {
      setCurrentSloka(currentSloka - 1);
    } else if (direction === 'next' && currentSloka < sargaData.slokas.length - 1) {
      setCurrentSloka(currentSloka + 1);
    }
  };

  const navigateSarga = async (direction: 'prev' | 'next') => {
    if (!sarga || !kanda) return;
    
    const sargaNum = parseInt(sarga);
    const newSarga = direction === 'prev' ? sargaNum - 1 : sargaNum + 1;
    
    // Check boundaries
    if (newSarga < 1) return;
    
    // For next sarga, verify it exists before navigating
    if (direction === 'next') {
      try {
        const response = await fetch(`/api/ramayanam/kandas/${kanda}/sargas/${newSarga}`);
        if (!response.ok) {
          // If 404, we've reached the end of the kanda
          if (response.status === 404) {
            console.log(`End of Kanda ${kanda} reached. Sarga ${newSarga} does not exist.`);
            return;
          }
          // For other errors, still attempt navigation (let the next page handle it)
        }
      } catch (error) {
        console.error('Error checking next sarga existence:', error);
        // Continue with navigation anyway
      }
    }
    
    navigate(`/sarga/${source}/${kanda}/${newSarga}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-cream-50 to-orange-50 dark:from-gray-900 dark:to-blue-900">
        <div className="container mx-auto px-4 py-8">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error || !sargaData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-cream-50 to-orange-50 dark:from-gray-900 dark:to-blue-900">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg p-6 max-w-md mx-auto">
              <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
                Error Loading Sarga
              </h3>
              <p className="text-red-600 dark:text-red-300 mb-4">
                {error || 'Sarga not found'}
              </p>
              <button
                onClick={() => navigate('/')}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Return to Search
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const currentVerse = sargaData.slokas[currentSloka];

  return (
    <div className="min-h-screen bg-gradient-to-br from-cream-50 to-orange-50 dark:from-gray-900 dark:to-blue-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => navigate('/')}
              className="flex items-center space-x-2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Search</span>
            </button>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/')}
                className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
                title="Home"
              >
                <Home className="w-5 h-5" />
              </button>
            </div>
          </div>
          
          <div className="text-center">
            <div className="flex items-center justify-center space-x-3 mb-2">
              <div className="bg-orange-500 text-white px-4 py-2 rounded-full flex items-center space-x-2">
                <BookOpen className="w-4 h-4" />
                <span className="font-semibold">{sargaData.kanda.name}</span>
              </div>
              <div className="bg-gradient-to-r from-saffron-500 to-gold-500 text-white px-4 py-2 rounded-full font-semibold">
                Sarga {sargaData.sarga.number}
              </div>
            </div>
            <p className="text-gray-600 dark:text-gray-300">
              {sargaData.sarga.total_slokas} verses • Reading verse {currentSloka + 1}
            </p>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => navigateSarga('prev')}
            className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            disabled={parseInt(sarga!) <= 1}
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Previous Sarga</span>
          </button>
          
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Verse {currentSloka + 1} of {sargaData.sarga.total_slokas}
          </div>
          
          <button
            onClick={() => navigateSarga('next')}
            className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <span>Next Sarga</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {/* Current Verse */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg">
            {/* Verse Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="bg-gradient-to-r from-saffron-400 to-gold-500 text-white px-4 py-2 rounded-full text-sm font-semibold">
                {currentVerse.sloka_number}
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleToggleFavorite(currentVerse.sloka_number)}
                  className={`p-2 rounded-lg transition-colors ${
                    favorites.includes(currentVerse.sloka_number)
                      ? 'text-red-500 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30' 
                      : 'text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20'
                  }`}
                  title={favorites.includes(currentVerse.sloka_number) ? 'Remove from favorites' : 'Add to favorites'}
                >
                  <Heart className={`w-5 h-5 ${favorites.includes(currentVerse.sloka_number) ? 'fill-current' : ''}`} />
                </button>
                
                <button
                  onClick={() => handleCopySloka(currentVerse)}
                  className="p-2 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  title="Copy verse"
                >
                  <Copy className="w-5 h-5" />
                </button>
                
                <button
                  onClick={() => handleShareSloka(currentVerse)}
                  className="p-2 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  title="Share verse"
                >
                  <Share2 className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Sanskrit Text */}
            <div className="mb-6">
              <div className="sanskrit-text text-2xl font-medium text-gray-800 dark:text-gray-200 leading-relaxed text-center">
                {currentVerse.sloka}
              </div>
            </div>

            {/* Translation */}
            <div className="mb-6">
              <div 
                className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed text-center"
                dangerouslySetInnerHTML={{ __html: currentVerse.translation }}
              />
            </div>

            {/* Meaning */}
            {currentVerse.meaning && (
              <div className="border-t border-gold-200 dark:border-gold-700/30 pt-6">
                <h4 className="text-sm font-medium text-gold-600 dark:text-gold-400 mb-3">Sanskrit Meaning:</h4>
                <div className="p-4 bg-gold-50 dark:bg-gray-700/50 rounded-lg">
                  <div className="sanskrit-text text-gray-700 dark:text-gray-300 leading-relaxed">
                    {currentVerse.meaning}
                  </div>
                </div>
              </div>
            )}

            {/* Verse Navigation */}
            <div className="flex items-center justify-between mt-8 pt-6 border-t border-gold-200 dark:border-gold-700/30">
              <button
                onClick={() => navigateSloka('prev')}
                disabled={currentSloka === 0}
                className="flex items-center space-x-2 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
                aria-label={`Go to previous verse ${currentSloka > 0 ? `(verse ${currentSloka})` : '(at first verse)'}`}
                title={currentSloka > 0 ? `Go to verse ${currentSloka}` : 'Already at first verse'}
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Previous Verse</span>
              </button>
              
              <div className="text-sm text-gray-500 dark:text-gray-400" role="status" aria-live="polite">
                Verse {currentSloka + 1} of {sargaData.sarga.total_slokas}
              </div>
              
              <button
                onClick={() => navigateSloka('next')}
                disabled={currentSloka === sargaData.slokas.length - 1}
                className="flex items-center space-x-2 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
                aria-label={`Go to next verse ${currentSloka < sargaData.slokas.length - 1 ? `(verse ${currentSloka + 2})` : '(at last verse)'}`}
                title={currentSloka < sargaData.slokas.length - 1 ? `Go to verse ${currentSloka + 2}` : 'Already at last verse'}
              >
                <span>Next Verse</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            {/* External Link */}
            <div className="text-center mt-6">
              <a
                href={`https://valmiki.iitk.ac.in/sloka?field_kanda_tid=${kanda}&field_sarga_value=${sarga}&field_sloka_value=${currentVerse.sloka_number.split('.')[2]}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-2 text-sm text-gold-600 dark:text-gold-400 hover:text-gold-700 dark:hover:text-gold-300 transition-colors"
              >
                <span>View on Valmiki Ramayana Source</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>

        {/* Quick Verse Selector */}
        <div className="mt-12">
          <div className="max-w-md mx-auto bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4 text-center">
              Jump to Verse
            </h3>
            <div className="flex items-center space-x-4">
              <label htmlFor="verse-selector" className="text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap">
                Go to verse:
              </label>
              <select
                id="verse-selector"
                value={currentSloka}
                onChange={(e) => setCurrentSloka(parseInt(e.target.value))}
                className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-400"
                aria-label="Select verse to jump to"
              >
                {sargaData.slokas.map((verse, index) => (
                  <option key={verse.sloka_number} value={index}>
                    Verse {index + 1} - {verse.sloka_number}
                  </option>
                ))}
              </select>
            </div>
            <div className="mt-3 text-sm text-gray-500 dark:text-gray-400 text-center">
              {sargaData.sarga.total_slokas} verses in this sarga
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SargaView;