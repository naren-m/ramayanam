import React from 'react';
import { BookOpen, Github, Mail, Heart, ExternalLink } from 'lucide-react';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-white py-16">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* Brand */}
          <div className="md:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-blue-600 rounded-full flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold gradient-text">
                  Universal Sacred Text Platform
                </h3>
                <p className="text-gray-400 text-sm">AI-Powered Scripture Explorer</p>
              </div>
            </div>
            <p className="text-gray-300 leading-relaxed mb-6 max-w-md">
              Explore ancient wisdom through modern technology. Search, analyze, and discuss 
              sacred texts from the Hindu tradition with intelligent AI guidance.
            </p>
            <div className="flex items-center space-x-4">
              <a
                href="https://github.com/your-repo"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
                title="GitHub Repository"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="mailto:contact@example.com"
                className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
                title="Contact Us"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <a href="#demo" className="text-gray-300 hover:text-orange-400 transition-colors">
                  Search Demo
                </a>
              </li>
              <li>
                <a href="#chat-demo" className="text-gray-300 hover:text-orange-400 transition-colors">
                  Chat Demo
                </a>
              </li>
              <li>
                <a href="#api" className="text-gray-300 hover:text-orange-400 transition-colors">
                  API Documentation
                </a>
              </li>
              <li>
                <a href="#roadmap" className="text-gray-300 hover:text-orange-400 transition-colors">
                  Roadmap
                </a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Resources</h4>
            <ul className="space-y-2">
              <li>
                <a
                  href="http://localhost:5001"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-300 hover:text-orange-400 transition-colors flex items-center space-x-1"
                >
                  <span>Live Platform</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a
                  href="https://valmiki.iitk.ac.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-300 hover:text-orange-400 transition-colors flex items-center space-x-1"
                >
                  <span>Valmiki Ramayana</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-300 hover:text-orange-400 transition-colors">
                  User Guide
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-300 hover:text-orange-400 transition-colors">
                  FAQ
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 pt-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-2 text-gray-400 mb-4 md:mb-0">
              <span>© {currentYear} Universal Sacred Text Platform.</span>
              <span>Built with</span>
              <Heart className="w-4 h-4 text-red-500" />
              <span>and Claude AI</span>
            </div>
            <div className="flex items-center space-x-6 text-sm text-gray-400">
              <a href="#" className="hover:text-orange-400 transition-colors">
                Privacy Policy
              </a>
              <a href="#" className="hover:text-orange-400 transition-colors">
                Terms of Service
              </a>
              <a href="#" className="hover:text-orange-400 transition-colors">
                Open Source
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;