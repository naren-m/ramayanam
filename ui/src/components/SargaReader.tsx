import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, BookOpen, ChevronLeft, ChevronRight, Heart, Copy, Share2 } from 'lucide-react';
import { Verse } from '../types';
import { useSearch } from '../contexts/SearchContext';
import LoadingSpinner from './LoadingSpinner';

const SargaReader: React.FC = () => {
  const { source, kanda, sarga } = useParams<{ source: string; kanda: string; sarga: string }>();
  const navigate = useNavigate();
  const { favorites, addToFavorites, removeFromFavorites } = useSearch();
  const [verses, setVerses] = useState<Verse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentVerseIndex, setCurrentVerseIndex] = useState(0);

  useEffect(() => {
    loadSargaVerses();
  }, [source, kanda, sarga]);

  const loadSargaVerses = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Mock API call - replace with actual API endpoint
      const mockVerses = generateMockSargaVerses();
      setVerses(mockVerses);
    } catch (err) {
      setError('Failed to load sarga verses');
    } finally {
      setLoading(false);
    }
  };

  const generateMockSargaVerses = (): Verse[] => {
    const verseCount = Math.floor(Math.random() * 20) + 10; // 10-30 verses
    const verses: Verse[] = [];
    
    for (let i = 1; i <= verseCount; i++) {
      verses.push({
        sloka_number: `${kanda}.${sarga}.${i}`,
        ratio: 100,
        sloka: `तत्र श्लोक ${i} संस्कृत पाठ यहाँ होगा। यह एक उदाहरण श्लोक है।`,
        meaning: `यहाँ श्लोक ${i} का अर्थ होगा। यह संस्कृत श्लोक का विस्तृत अर्थ है।`,
        translation: `This is the English translation of verse ${i} in Sarga ${sarga} of Kanda ${kanda}. This verse contains important teachings and narrative elements.`,
        source: source as string
      });
    }
    
    return verses;
  };

  const getSourceInfo = () => {
    if (source === 'bhagavad-gita') {
      return { name: 'Bhagavad Gita', color: 'bg-blue-500', chapter: `Chapter ${kanda}` };
    } else if (source === 'ramayana') {
      const kandaNames = ['', 'Bala', 'Ayodhya', 'Aranya', 'Kishkindha', 'Sundara', 'Yuddha'];
      return { 
        name: 'Valmiki Ramayana', 
        color: 'bg-orange-500', 
        chapter: `${kandaNames[parseInt(kanda || '1')]} Kandam - Sarga ${sarga}` 
      };
    }
    return { name: 'Sacred Text', color: 'bg-purple-500', chapter: `Section ${kanda}.${sarga}` };
  };

  const handleToggleFavorite = (verse: Verse) => {
    const isFavorite = favorites.some(f => f.id === verse.sloka_number);
    if (isFavorite) {
      removeFromFavorites(verse.sloka_number);
    } else {
      addToFavorites(verse);
    }
  };

  const handleCopyVerse = async (verse: Verse) => {
    const text = `${verse.sloka_number}: ${verse.sloka}\n\n${verse.translation}`;
    try {
      await navigator.clipboard.writeText(text);
    } catch (error) {
      console.error('Failed to copy verse');
    }
  };

  const navigateVerse = (direction: 'prev' | 'next') => {
    if (direction === 'prev' && currentVerseIndex > 0) {
      setCurrentVerseIndex(currentVerseIndex - 1);
    } else if (direction === 'next' && currentVerseIndex < verses.length - 1) {
      setCurrentVerseIndex(currentVerseIndex + 1);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error || verses.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg p-6 max-w-md mx-auto">
          <BookOpen className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
            Unable to Load Sarga
          </h3>
          <p className="text-red-600 dark:text-red-300 mb-4">
            {error || 'No verses found for this sarga'}
          </p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Return to Search
          </button>
        </div>
      </div>
    );
  }

  const sourceInfo = getSourceInfo();
  const currentVerse = verses[currentVerseIndex];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/')}
          className="flex items-center space-x-2 text-gray-600 dark:text-gray-300 hover:text-orange-600 dark:hover:text-orange-400 transition-colors mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Search</span>
        </button>
        
        <div className="flex items-center space-x-4 mb-4">
          <div className={`${sourceInfo.color} text-white px-4 py-2 rounded-full font-semibold flex items-center space-x-2`}>
            <BookOpen className="w-5 h-5" />
            <span>{sourceInfo.name}</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            {sourceInfo.chapter}
          </h1>
        </div>
        
        <p className="text-gray-600 dark:text-gray-400">
          Reading {verses.length} verses • Verse {currentVerseIndex + 1} of {verses.length}
        </p>
      </div>

      {/* Navigation Controls */}
      <div className="flex items-center justify-between mb-8">
        <button
          onClick={() => navigateVerse('prev')}
          disabled={currentVerseIndex === 0}
          className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="w-5 h-5" />
          <span>Previous</span>
        </button>
        
        <div className="flex items-center space-x-4">
          <select
            value={currentVerseIndex}
            onChange={(e) => setCurrentVerseIndex(parseInt(e.target.value))}
            className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-400"
          >
            {verses.map((verse, index) => (
              <option key={verse.sloka_number} value={index}>
                Verse {verse.sloka_number}
              </option>
            ))}
          </select>
        </div>
        
        <button
          onClick={() => navigateVerse('next')}
          disabled={currentVerseIndex === verses.length - 1}
          className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span>Next</span>
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Current Verse Display */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg mb-8">
        {/* Verse Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="bg-gradient-to-br from-saffron-400 to-gold-500 text-white px-4 py-2 rounded-full text-lg font-semibold">
            {currentVerse.sloka_number}
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleToggleFavorite(currentVerse)}
              className={`p-2 rounded-lg transition-colors ${
                favorites.some(f => f.id === currentVerse.sloka_number)
                  ? 'text-red-500 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30' 
                  : 'text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20'
              }`}
            >
              <Heart className={`w-5 h-5 ${favorites.some(f => f.id === currentVerse.sloka_number) ? 'fill-current' : ''}`} />
            </button>
            
            <button
              onClick={() => handleCopyVerse(currentVerse)}
              className="p-2 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <Copy className="w-5 h-5" />
            </button>
            
            <button
              onClick={() => handleCopyVerse(currentVerse)}
              className="p-2 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <Share2 className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Sanskrit Text */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Sanskrit</h3>
          <div className="sanskrit-text text-2xl font-medium text-gray-800 dark:text-gray-200 leading-relaxed">
            {currentVerse.sloka}
          </div>
        </div>

        {/* Translation */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Translation</h3>
          <div className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed">
            {currentVerse.translation}
          </div>
        </div>

        {/* Meaning */}
        {currentVerse.meaning && (
          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Sanskrit Meaning</h3>
            <div className="sanskrit-text text-gray-700 dark:text-gray-300 leading-relaxed">
              {currentVerse.meaning}
            </div>
          </div>
        )}
      </div>

      {/* Verse List Overview */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
          All Verses in this Sarga
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {verses.map((verse, index) => (
            <button
              key={verse.sloka_number}
              onClick={() => setCurrentVerseIndex(index)}
              className={`p-4 rounded-lg border text-left transition-colors ${
                index === currentVerseIndex
                  ? 'border-orange-400 bg-orange-50 dark:bg-orange-900/20'
                  : 'border-gray-200 dark:border-gray-600 hover:border-orange-300 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              <div className="font-semibold text-sm text-orange-600 dark:text-orange-400 mb-1">
                {verse.sloka_number}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                {verse.translation.substring(0, 80)}...
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SargaReader;