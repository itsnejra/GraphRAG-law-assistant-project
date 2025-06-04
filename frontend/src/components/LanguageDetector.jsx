import React from 'react';
import { Globe, Zap } from 'lucide-react';

const LanguageDetector = ({ detectedLanguage, className = "" }) => {
  const getLanguageInfo = (langCode) => {
    const languages = {
      'bs': { name: 'Bosanski', flag: '🇧🇦', color: 'from-blue-500 to-green-500' },
      'en': { name: 'English', flag: '🇺🇸', color: 'from-blue-500 to-red-500' },
      'de': { name: 'Deutsch', flag: '🇩🇪', color: 'from-yellow-500 to-red-500' },
      'fr': { name: 'Français', flag: '🇫🇷', color: 'from-blue-500 to-white' },
      'hr': { name: 'Hrvatski', flag: '🇭🇷', color: 'from-red-500 to-blue-500' },
      'sr': { name: 'Srpski', flag: '🇷🇸', color: 'from-red-500 to-blue-500' }
    };
    
    return languages[langCode] || languages['bs'];
  };

  const langInfo = getLanguageInfo(detectedLanguage);

  if (!detectedLanguage) return null;

  return (
    <div className={`inline-flex items-center space-x-2 px-3 py-1.5 bg-gradient-to-r ${langInfo.color} bg-opacity-20 border border-current border-opacity-30 rounded-full text-sm font-medium ${className}`}>
      <Globe className="h-4 w-4" />
      <span className="text-xs">{langInfo.flag}</span>
      <span>{langInfo.name}</span>
      <Zap className="h-3 w-3 animate-pulse" />
    </div>
  );
};

export default LanguageDetector;