import React from 'react';
import { Link } from 'react-router-dom';

const TestAnimation: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Animation Test Page</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-blue-100 p-6 rounded-lg border border-blue-300 shadow-sm">
          <h2 className="text-xl font-semibold mb-3">Test Page 1</h2>
          <p className="mb-4">
            This page is used to test the animation transitions between routes.
            Navigate between these test pages to see different animation directions.
          </p>
          <div className="flex space-x-4">
            <Link 
              to="/test2" 
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
            >
              Go to Test Page 2
            </Link>
            <Link 
              to="/" 
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition"
            >
              Back to Home
            </Link>
          </div>
        </div>
        
        <div className="bg-purple-100 p-6 rounded-lg border border-purple-300 shadow-sm">
          <h2 className="text-xl font-semibold mb-3">Animation Features</h2>
          <ul className="list-disc pl-5 space-y-2">
            <li>Direction-aware transitions</li>
            <li>Smooth fade effects</li>
            <li>Hardware-accelerated animations</li>
            <li>Optimized performance with keyframes</li>
          </ul>
        </div>
      </div>
      
      <div className="bg-green-100 p-6 rounded-lg border border-green-300">
        <h2 className="text-xl font-semibold mb-3">How It Works</h2>
        <p>
          The animation system detects navigation patterns and applies appropriate
          transitions based on the navigation direction. Going deeper into the site
          triggers a slide-from-right animation, while going back triggers a 
          slide-from-left animation.
        </p>
      </div>
    </div>
  );
};

export default TestAnimation;