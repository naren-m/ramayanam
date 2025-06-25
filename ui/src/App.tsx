import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import SargaView from './components/SargaView';
import ErrorBoundary from './components/ErrorBoundary';
import { ThemeProvider } from './contexts/ThemeContext';
import { SearchProvider } from './contexts/SearchContext';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <SearchProvider>
          <Router>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/sarga/:source/:kanda/:sarga" element={<SargaView />} />
            </Routes>
          </Router>
        </SearchProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;