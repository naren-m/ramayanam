import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, Copy, ExternalLink, Share2, ChevronDown, ChevronUp, BookOpen, Eye } from 'lucide-react';
import { Verse } from '../types';
import { useSearch } from '../contexts/SearchContext';
import { copyToClipboard, formatVerseForSharing } from '../utils/api';

interface VerseCardProps {
  verse: Verse;
  index: number;
}

const VerseCard: React.FC<VerseCardProps> = ({ verse, index }) => {
  const navigate = useNavigate();
  const { favorites, addToFavorites, removeFromFavorites } = useSearch();
  const [expanded, setExpanded] = useState(false);
  const [copyStatus, setCopyStatus] = useState<'idle' | 'copied' | 'error'>('idle');

  const isFavorite = favorites.some(f => f.id === verse.sloka_number);

  const handleToggleFavorite = () => {
    if (isFavorite) {
      removeFromFavorites(verse.sloka_number);
    } else {
      addToFavorites(verse);
    }
  };

  const handleCopy = async () => {
    const text = formatVerseForSharing(verse);
    const success = await copyToClipboard(text);
    setCopyStatus(success ? 'copied' : 'error');
    setTimeout(() => setCopyStatus('idle'), 2000);
  };

  const handleShare = async () => {
    const text = formatVerseForSharing(verse);
    if (navigator.share) {
      await navigator.share({
        title: `${verse.source || 'Sacred Text'} Verse ${verse.sloka_number}`,
        text: text,
      });
    } else {
      handleCopy();
    }
  };

  const handleReadSarga = () => {
    const parts = verse.sloka_number.split('.');
    if (parts.length >= 3) {
      const kanda = parts[0];
      const sarga = parts[1];
      const verseNum = parts[2];
      const source = verse.source || 'ramayana';
      navigate(`/sarga/${source}/${kanda}/${sarga}/${verseNum}`);
    }
  };

  const getSourceInfo = () => {
    if (verse.source === 'bhagavad-gita') {
      return { name: 'Bhagavad Gita', color: 'bg-blue-500' };
    } else if (verse.source === 'ramayana') {
      return { name: 'Ramayana', color: 'bg-orange-500' };
    } else if (verse.source === 'mahabharata') {
      return { name: 'Mahabharata', color: 'bg-purple-500' };
    }
    return { name: 'Ramayana', color: 'bg-orange-500' };
  };

  const sourceInfo = getSourceInfo();
  const externalUrl = verse.source === 'ramayana' 
    ? `https://valmiki.iitk.ac.in/sloka?field_kanda_tid=${verse.sloka_number.split('.')[0]}&field_sarga_value=${verse.sloka_number.split('.')[1]}&field_sloka_value=${verse.sloka_number.split('.')[2]}`
    : '#';

  return (
    <div 
      className="verse-card rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 fade-in-up"
      style={{ animationDelay: `${index * 100}ms` }}
      data-testid="verse-card"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`${sourceInfo.color} text-white px-3 py-1 rounded-full text-sm font-semibold flex items-center space-x-1`}>
            <BookOpen className="w-3 h-3" />
            <span>{sourceInfo.name}</span>
          </div>
          <div className="bg-gradient-to-br from-saffron-400 to-gold-500 text-white px-3 py-1 rounded-full text-sm font-semibold" data-testid="verse-metadata">
            {verse.sloka_number}
          </div>
          <div className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-2 py-1 rounded-full text-xs font-medium">
            {verse.ratio}% match
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleReadSarga}
            className="p-2 rounded-lg text-blue-500 bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
            title="Read full sarga"
          >
            <Eye className="w-5 h-5" />
          </button>
          
          <button
            onClick={handleToggleFavorite}
            className={`p-2 rounded-lg transition-colors ${
              isFavorite 
                ? 'text-red-500 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30' 
                : 'text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20'
            }`}
            title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
          >
            <Heart className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
          </button>
          
          <button
            onClick={handleCopy}
            className={`p-2 rounded-lg transition-colors ${
              copyStatus === 'copied' 
                ? 'text-green-500 bg-green-50 dark:bg-green-900/20' 
                : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
            title="Copy verse"
          >
            <Copy className="w-5 h-5" />
          </button>
          
          <button
            onClick={handleShare}
            className="p-2 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            title="Share verse"
          >
            <Share2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Sanskrit Text */}
      <div className="mb-4">
        <div className="sanskrit-text text-lg font-medium text-gray-800 dark:text-gray-200 leading-relaxed" data-testid="verse-text">
          {verse.sloka}
        </div>
      </div>

      {/* Translation */}
      <div className="mb-4">
        <div 
          className="text-gray-700 dark:text-gray-300 leading-relaxed"
          data-testid="verse-translation"
          dangerouslySetInnerHTML={{ __html: verse.translation }}
        />
      </div>

      {/* Expandable Meaning */}
      {verse.meaning && (
        <div className="border-t border-gold-200 dark:border-gold-700/30 pt-4">
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center space-x-2 text-gold-600 dark:text-gold-400 hover:text-gold-700 dark:hover:text-gold-300 transition-colors"
          >
            <span className="text-sm font-medium">Sanskrit Meaning</span>
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          
          {expanded && (
            <div className="mt-3 p-4 bg-gold-50 dark:bg-gray-700/50 rounded-lg">
              <div className="sanskrit-text text-gray-700 dark:text-gray-300 leading-relaxed">
                {verse.meaning}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between mt-4 pt-4 border-t border-gold-200 dark:border-gold-700/30">
        <div className="text-xs text-gray-500 dark:text-gray-400">
          {copyStatus === 'copied' && (
            <span className="text-green-600 dark:text-green-400">Copied to clipboard!</span>
          )}
          {copyStatus === 'error' && (
            <span className="text-red-600 dark:text-red-400">Failed to copy</span>
          )}
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={handleReadSarga}
            className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors font-medium"
          >
            Read Full Sarga
          </button>
          
          {verse.source === 'ramayana' && (
            <a
              href={externalUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1 text-xs text-gold-600 dark:text-gold-400 hover:text-gold-700 dark:hover:text-gold-300 transition-colors"
            >
              <span>View Source</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
};

export default VerseCard;