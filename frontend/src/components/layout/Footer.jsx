import React from 'react';
import { Scale, Github, Mail, Heart } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <Scale className="h-6 w-6 text-blue-400" />
              <h1 className="text-xl font-bold">Pravni Asistent</h1>
            </div>
            <p className="text-gray-400 mb-6">
              AI pravni asistent za Zakon o radu Federacije BiH
            </p>
          </div>
          
          <div className="text-right">
            <p className="text-gray-400 text-sm">
              © 2025 Nejra Smajlović - Univerzitet u Zenici
            </p>
            <div className="flex items-center justify-end mt-2">
              <span className="text-gray-400 text-sm">Napravljeno sa</span>
              <Heart className="h-4 w-4 mx-1 text-red-500" fill="currentColor" />
              <span className="text-gray-400 text-sm">u Zenici, BiH</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;