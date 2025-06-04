import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, BookOpen, Globe, Sparkles, RotateCcw, Copy, Check, Zap, Crown, Shield, ArrowRight } from 'lucide-react';
import TypewriterText from '../components/TypewriterText';
import { apiService } from '../services/api';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [messageCount, setMessageCount] = useState(0);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const exampleQuestions = [
    "Koliko dana godišnjeg odmora imam pravo?",
    "Šta je probni rad i kako se reguliše?", 
    "Kako se obračunava prekovremeni rad?",
    "Kakva su prava trudnica na poslu?",
    "Koji su načini prestanka radnog odnosa?",
    "Koliko traje otkazni rok?",
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (message = inputValue) => {
    if (!message.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date(),
      messageNumber: messageCount + 1
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setMessageCount(prev => prev + 1);

    try {
      const response = await apiService.sendMessage(message, true);
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.answer,
        sources: response.sources,
        timestamp: new Date(),
        showTypewriter: true,
        messageNumber: messageCount + 2
      };

      setMessages(prev => [...prev, botMessage]);
      setMessageCount(prev => prev + 1);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: 'Izvinjavam se, došlo je do greške. Molimo pokušajte ponovo.',
        error: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const copyToClipboard = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setMessageCount(0);
  };

  const SourceIndicator = ({ sources }) => {
    if (!sources) return null;

    const isInternetUsed = sources.internet_search_performed || sources.source_used === 'internet' || sources.source_used === 'hybrid';

    return (
      <div className="mb-5 space-y-3">
        {/* Professional Source Indicator */}
        <div className={`rounded-xl p-4 border ${
          sources.source_used === 'local' 
            ? 'bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-blue-200 dark:border-blue-700' 
            : sources.source_used === 'internet' 
            ? 'bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border-purple-200 dark:border-purple-700'
            : 'bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 border-indigo-200 dark:border-indigo-700'
        } backdrop-blur-sm`}>
          <div className="flex items-center space-x-3">
            {sources.source_used === 'local' && (
              <>
                <div className="flex items-center space-x-2">
                  <BookOpen className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  <Shield className="h-4 w-4 text-indigo-500" />
                </div>
                <span className="font-semibold text-blue-700 dark:text-blue-300">📚 Zakon o radu FBiH</span>
              </>
            )}
            {sources.source_used === 'internet' && (
              <>
                <div className="flex items-center space-x-2">
                  <Globe className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  <Zap className="h-4 w-4 text-blue-500" />
                </div>
                <span className="font-semibold text-purple-700 dark:text-purple-300">🌐 Internet pretraga</span>
              </>
            )}
            {sources.source_used === 'hybrid' && (
              <>
                <div className="flex items-center space-x-2">
                  <Sparkles className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
                  <Crown className="h-4 w-4 text-purple-500" />
                </div>
                <span className="font-semibold text-indigo-700 dark:text-indigo-300">✨ Kombinovano</span>
              </>
            )}
          </div>
        </div>

        {/* Professional Internet Warning */}
        {isInternetUsed && (
          <div className="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border border-amber-200 dark:border-amber-700 rounded-xl p-4">
            <div className="flex items-center space-x-3">
              <Globe className="h-5 w-5 text-amber-600 dark:text-amber-400" />
              <div>
                <div className="font-medium text-amber-800 dark:text-amber-300 text-sm">
                  ⚠️ Proširen odgovor internetom
                </div>
                <div className="text-amber-700 dark:text-amber-400 text-xs mt-1">
                  Ovaj odgovor sadrži dodatne informacije sa interneta jer specifičan sadržaj nije pronađen u Zakonu o radu FBiH
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Professional Sources Display */}
        {sources.local_sources && sources.local_sources.length > 0 && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-2">
              <BookOpen className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              <span className="font-medium text-blue-800 dark:text-blue-300 text-sm">Članci zakona:</span>
            </div>
            <div className="text-blue-700 dark:text-blue-400 text-sm">
              {sources.local_sources.filter(s => s && s !== 'Nepoznat članak').join(' • ')}
            </div>
          </div>
        )}
        
        {sources.internet_sources && sources.internet_sources.length > 0 && (
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border border-purple-200 dark:border-purple-700 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-2">
              <Globe className="h-4 w-4 text-purple-600 dark:text-purple-400" />
              <span className="font-medium text-purple-800 dark:text-purple-300 text-sm">Internet izvori:</span>
            </div>
            <div className="text-purple-700 dark:text-purple-400 text-sm">
              {sources.internet_sources.join(' • ')}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      {/* MATCHING HOME PAGE BACKGROUND */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900 bg-pattern">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 via-purple-600/10 to-pink-600/10" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-400/20 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" />
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-purple-400/20 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '2s' }} />
        <div className="absolute bottom-1/4 left-1/2 w-96 h-96 bg-pink-400/20 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '4s' }} />
      </div>

      {/* Professional Header - KOMPAKTNI I VISOKO POZICIONIRAN */}
      <div className="relative backdrop-blur-xl bg-white/90 dark:bg-gray-900/90 border-b border-gray-200/20 dark:border-gray-700/20 z-50 pt-20">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {/* KOMPAKTNI Avatar */}
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl blur opacity-50 group-hover:opacity-75 transition-opacity"></div>
                <div className="relative p-2 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-xl shadow-lg">
                  <Bot className="h-6 w-6 text-white" />
                </div>
              </div>
              
              {/* KOMPAKTNI Title */}
              <div>
                <div className="flex items-center space-x-2">
                  <h1 className="text-xl font-bold gradient-text">
                    Pravni AI Asistent
                  </h1>
                  <Sparkles className="h-4 w-4 text-yellow-400 animate-pulse" />
                </div>
                <div className="flex items-center space-x-2 mt-0.5">
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Zakon o radu FBiH</span>
                  {messageCount > 0 && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      • {messageCount} poruka
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            {messages.length > 0 && (
              <button
                onClick={clearChat}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg transition-all text-sm"
              >
                <RotateCcw className="h-4 w-4 mr-1 inline" />
                Reset
              </button>
            )}
          </div>
          
          {/* KOMPAKTNI Status Bar - samo kad nema poruka */}
          {messages.length === 0 && (
            <div className="mt-3 p-3 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-200/50 dark:border-gray-700/50">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-green-600 dark:text-green-400 font-semibold text-xs">Online</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Sparkles className="h-3 w-3 text-purple-500 animate-pulse" />
                    <span className="text-gray-600 dark:text-gray-300 text-xs">Automatska internet pretraga</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2 text-blue-600 dark:text-blue-400">
                  <Crown className="h-3 w-3 animate-pulse" />
                  <span className="font-semibold text-xs">AI Premium</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Messages Area - DODAO PRAVILNO PADDING-TOP */}
      <div className="relative flex-1 overflow-y-auto" style={{ paddingTop: messages.length > 0 ? '2rem' : '0' }}>
        <div className="max-w-6xl mx-auto px-6 py-8">
          {messages.length === 0 ? (
            <div className="text-center py-20 animate-fade-in">
              {/* SPECTACULAR WELCOME - HOME PAGE STYLE */}
              <div className="relative mb-12">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 rounded-full blur-3xl opacity-30 animate-pulse-glow"></div>
                <div className="relative inline-flex items-center justify-center w-32 h-32 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-full shadow-2xl animate-float">
                  <Bot className="h-16 w-16 text-white" />
                </div>
              </div>
              
              <h3 className="text-6xl font-bold mb-6">
                <span className="gradient-text">
                  Dobrodošli u AI Chat!
                </span>
              </h3>
              <p className="text-2xl text-gray-600 dark:text-gray-300 max-w-4xl mx-auto leading-relaxed mb-16">
                🚀 Najnapredniji AI asistent za <span className="font-bold gradient-text">Zakon o radu FBiH</span>
                <br />
                ✨ Automatski pristup internetu • 💎 Precizni odgovori • 🌟 Dostupno 24/7
              </p>
              
              {/* HOME PAGE STYLE Example Questions */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
                {exampleQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleSend(question)}
                    className="block p-8 bg-white dark:bg-gray-800 rounded-3xl shadow-lg hover:shadow-2xl transition-all transform hover:-translate-y-2 border border-gray-200 dark:border-gray-700 group animate-slide-up"
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl group-hover:scale-110 transition-transform">
                        <Sparkles className="h-6 w-6 text-white" />
                      </div>
                      <Send className="h-4 w-4 text-gray-400 group-hover:text-blue-500 transition-colors" />
                    </div>
                    <span className="text-gray-700 dark:text-gray-300 font-medium group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors text-left block leading-relaxed">
                      "{question}"
                    </span>
                    <div className="flex items-center mt-4 text-blue-600 dark:text-blue-400 font-medium group-hover:translate-x-2 transition-transform duration-300">
                      <span className="text-sm">Pitaj sada</span>
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-8">
              {messages.map((message, index) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up`}
                >
                  <div className={`flex items-start space-x-4 max-w-4xl ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    {/* Professional Avatar */}
                    <div className={`flex-shrink-0 w-12 h-12 rounded-2xl flex items-center justify-center ${
                      message.type === 'user' 
                        ? 'bg-gradient-to-br from-blue-500 to-indigo-600' 
                        : message.error
                        ? 'bg-gradient-to-br from-red-500 to-red-600'
                        : 'bg-gradient-to-br from-indigo-500 to-purple-600'
                    } shadow-lg`}>
                      {message.type === 'user' ? (
                        <User className="h-6 w-6 text-white" />
                      ) : (
                        <Bot className="h-6 w-6 text-white" />
                      )}
                    </div>
                    
                    {/* Professional Message Bubble */}
                    <div className={`rounded-3xl p-6 shadow-lg ${
                      message.type === 'user'
                        ? 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white'
                        : message.error
                        ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 text-red-700 dark:text-red-300'
                        : 'bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm border border-slate-200/50 dark:border-slate-700/50'
                    } hover-lift max-w-3xl relative`}>
                      
                      {/* Message Number Badge */}
                      {message.messageNumber && (
                        <div className={`absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                          message.type === 'user' ? 'bg-white/20 text-white' : 'bg-indigo-500 text-white'
                        }`}>
                          {message.messageNumber}
                        </div>
                      )}
                      
                      <div className="relative">
                        {message.type === 'assistant' && message.sources && (
                          <SourceIndicator sources={message.sources} />
                        )}
                        
                        <div className={`prose prose-lg max-w-none ${
                          message.type === 'user' ? 'text-white' : 'text-slate-700 dark:text-slate-200'
                        }`}>
                          {message.type === 'assistant' && message.showTypewriter ? (
                            <TypewriterText 
                              text={message.content} 
                              speed={20}
                              className="block leading-relaxed"
                            />
                          ) : (
                            <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
                          )}
                        </div>
                        
                        {message.type === 'assistant' && !message.error && (
                          <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-200/50 dark:border-slate-600/50">
                            <div className="flex items-center space-x-3">
                              <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                                {message.timestamp.toLocaleTimeString('bs-BA', { 
                                  hour: '2-digit', 
                                  minute: '2-digit' 
                                })}
                              </span>
                              <div className="flex items-center space-x-1">
                                <Shield className="h-3 w-3 text-indigo-400" />
                                <span className="text-xs text-indigo-600 dark:text-indigo-400 font-medium">AI</span>
                              </div>
                            </div>
                            <button
                              onClick={() => copyToClipboard(message.content, index)}
                              className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl transition-colors"
                            >
                              {copiedIndex === index ? (
                                <Check className="h-4 w-4 text-green-500" />
                              ) : (
                                <Copy className="h-4 w-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300" />
                              )}
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Professional Loading */}
              {isLoading && (
                <div className="flex justify-start animate-slide-up">
                  <div className="flex items-start space-x-4 max-w-4xl">
                    <div className="flex-shrink-0 w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
                      <Bot className="h-6 w-6 text-white" />
                    </div>
                    <div className="bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm p-4 rounded-2xl border border-slate-200/50 dark:border-slate-700/50 shadow-lg">
                      <div className="flex items-center space-x-3">
                        <div className="animate-typing-dots flex space-x-1">
                          <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                          <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
                          <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                        </div>
                        <span className="text-slate-600 dark:text-slate-300 font-medium">
                          AI obrađuje vaše pitanje...
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* HOME PAGE STYLE Input Section */}
      <div className="relative backdrop-blur-xl bg-white/90 dark:bg-gray-900/90 border-t border-gray-200/20 dark:border-gray-700/20">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-end space-x-4">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Postavite pitanje o Zakonu o radu..."
                className="w-full px-6 py-4 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-2xl text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all"
                rows="1"
                disabled={isLoading}
                style={{ minHeight: '56px', maxHeight: '120px' }}
                onInput={(e) => {
                  e.target.style.height = 'auto';
                  e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
                }}
              />
            </div>
            
            {/* HOME PAGE STYLE Send Button */}
            <button
              onClick={() => handleSend()}
              disabled={!inputValue.trim() || isLoading}
              className="p-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-2xl hover:shadow-xl hover:shadow-blue-500/25 transition-all transform hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              <Send className="h-6 w-6" />
            </button>
          </div>
          
          {/* HOME PAGE STYLE Footer */}
          <div className="mt-4 text-center">
            <div className="flex items-center justify-center space-x-6 text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center space-x-2">
                <Zap className="h-4 w-4 text-blue-500" />
                <span>Enter za slanje</span>
              </div>
              <div className="flex items-center space-x-2">
                <Sparkles className="h-4 w-4 text-purple-500" />
                <span>Shift+Enter za novi red</span>
              </div>
              <div className="flex items-center space-x-2">
                <Crown className="h-4 w-4 text-yellow-500" />
                <span>AI Premium</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;