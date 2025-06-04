// src/services/api.js - POJEDNOSTAVLJENA VERZIJA - SAMO /api/chat

const getBaseURL = () => {
  let url = process.env.REACT_APP_API_URL || 'http://localhost:5000';
  
  if (url.endsWith('/api')) {
    url = url.slice(0, -4);
  }
  
  return url;
};

const API_BASE_URL = getBaseURL();

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.timeout = 60000;
    
    console.log('✅ ApiService inicijalizovan:');
    console.log('📍 Original REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
    console.log('📍 Cleaned baseURL:', this.baseURL);
  }

  async sendMessage(query) {
    try {
      const fullURL = `${this.baseURL}/api/chat`;
      
      console.log('🚀 Šalje poruku na:', fullURL);
      console.log('📝 Query:', query);
      
      const response = await fetch(fullURL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query
        }),
        signal: AbortSignal.timeout(this.timeout),
      });

      console.log('📡 Response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('✅ Chat response:', result);
      
      return result;

    } catch (error) {
      console.error('❌ Chat error:', error);
      
      if (error.name === 'TimeoutError') {
        throw new Error('Chat zahtev je trajao predugo. Pokušajte ponovo.');
      }
      
      if (error.message.includes('fetch')) {
        throw new Error('Greška u komunikaciji sa serverom. Proverite konekciju.');
      }
      
      throw error;
    }
  }

  async analyzeDocument(file, onProgress) {
    try {
      console.log('🚀 Pokretanje analize dokumenta:', file.name);
      
      this.validateFile(file);
      
      const formData = new FormData();
      formData.append('document', file);

      const startTime = Date.now();
      let progressInterval;
      
      if (onProgress) {
        let progress = 0;
        progressInterval = setInterval(() => {
          const elapsed = (Date.now() - startTime) / 1000;
          
          if (elapsed < 5) {
            progress = Math.min(20, elapsed * 4);
          } else if (elapsed < 15) {
            progress = 20 + Math.min(40, (elapsed - 5) * 4);
          } else if (elapsed < 25) {
            progress = 60 + Math.min(30, (elapsed - 15) * 3);
          } else {
            progress = Math.min(95, 90 + (elapsed - 25));
          }
          
          onProgress({
            progress,
            phase: this.getAnalysisPhase(elapsed),
            elapsed: Math.round(elapsed)
          });
        }, 500);
      }

      const response = await fetch(`${this.baseURL}/api/analyze_document`, {
        method: 'POST',
        body: formData,
        signal: AbortSignal.timeout(this.timeout),
      });

      if (progressInterval) {
        clearInterval(progressInterval);
        if (onProgress) onProgress({ progress: 100, phase: 'Završeno!' });
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      
      const totalTime = (Date.now() - startTime) / 1000;
      console.log(`✅ Analiza završena za ${totalTime.toFixed(2)}s`);
      
      return result;

    } catch (error) {
      console.error('❌ Analiza greška:', error);
      
      if (error.name === 'TimeoutError') {
        throw new Error('Analiza je trajala predugo. Pokušajte sa manjim fajlom.');
      }
      
      if (error.message.includes('fetch')) {
        throw new Error('Greška u komunikaciji sa serverom. Proverite konekciju.');
      }
      
      throw error;
    }
  }

  async checkHealth() {
    try {
      console.log('🏥 Health check...');
      
      const response = await fetch(`${this.baseURL}/api/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000),
      });

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('✅ Health check:', result);
      
      return result;
    } catch (error) {
      console.error('❌ Health check error:', error);
      throw error;
    }
  }

  async processPdf() {
    try {
      console.log('📚 Processing PDF for knowledge base...');
      
      const response = await fetch(`${this.baseURL}/process_pdf`, {
        method: 'GET',
        signal: AbortSignal.timeout(120000),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `PDF processing greška: ${response.status}`);
      }

      const result = await response.json();
      console.log('✅ PDF processed:', result);
      
      return result;
    } catch (error) {
      console.error('❌ PDF processing error:', error);
      throw error;
    }
  }

  async clearSession() {
    try {
      console.log('🗑️ Clearing session...');
      
      const response = await fetch(`${this.baseURL}/api/clear_session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(5000),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Clear session greška: ${response.status}`);
      }

      const result = await response.json();
      console.log('✅ Session cleared:', result);
      
      return result;
    } catch (error) {
      console.error('❌ Clear session error:', error);
      throw error;
    }
  }

  getAnalysisPhase(elapsed) {
    if (elapsed < 5) return '🔍 OCR - Čitanje dokumenta...';
    if (elapsed < 10) return '📋 Strukturiranje podataka...';
    if (elapsed < 20) return '⚖️ Analiza usklađenosti...';
    if (elapsed < 25) return '📊 Generiranje preporuka...';
    return '✨ Završne optimizacije...';
  }

  validateFile(file) {
    const maxSize = 10 * 1024 * 1024;
    const allowedTypes = [
      'application/pdf',
      'image/jpeg',
      'image/jpg', 
      'image/png',
      'image/webp',
      'image/gif'
    ];

    if (!file) {
      throw new Error('Fajl nije odabran');
    }

    if (file.size > maxSize) {
      throw new Error(`Fajl je prevelik. Maksimalna veličina je ${this.formatFileSize(maxSize)}`);
    }

    if (!allowedTypes.includes(file.type)) {
      throw new Error(`Nepodržan format: ${file.type}. Podržani: PDF, JPG, PNG, WEBP, GIF`);
    }

    return true;
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  async testConnection() {
    try {
      console.log('🧪 Testing connection...');
      
      const response = await fetch(`${this.baseURL}/`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000),
      });

      if (!response.ok) {
        throw new Error(`Connection test failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('✅ Connection test passed:', result);
      
      return result;
    } catch (error) {
      console.error('❌ Connection test failed:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export klase za advanced usage
export { ApiService };

// DEBUG: Dodajte ovo za testiranje u browser konzoli
if (process.env.NODE_ENV === 'development') {
  window.apiService = apiService;
  
  window.testAPI = async () => {
    try {
      console.log('🧪 Testing API connection...');
      const health = await apiService.checkHealth();
      console.log('✅ API is healthy:', health);
      
      const info = await apiService.testConnection();
      console.log('✅ API info:', info);
      
      return { health, info };
    } catch (error) {
      console.error('❌ API test failed:', error);
      throw error;
    }
  };
}

export default apiService;