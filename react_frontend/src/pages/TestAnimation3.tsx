import React from 'react';
import { Link } from 'react-router-dom';

const TestAnimation3: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Animation Test Page 3</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-green-100 p-6 rounded-lg border border-green-300 shadow-sm">
          <h2 className="text-xl font-semibold mb-3">Test Page 3</h2>
          <p className="mb-4">
            This is the third and deepest test page. The animation when navigating here
            should slide in from the right, and when going back it should slide from the left.
          </p>
          <div className="flex space-x-4">
            <Link 
              to="/test2" 
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
            >
              Back to Test Page 2
            </Link>
            <Link 
              to="/" 
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition"
            >
              Home
            </Link>
          </div>
        </div>
        
        <div className="bg-indigo-100 p-6 rounded-lg border border-indigo-300 shadow-sm">
          <h2 className="text-xl font-semibold mb-3">Deep Navigation</h2>
          <p>
            This page demonstrates the deepest level of our test navigation. The animation
            system should correctly identify this as a deep route and apply the appropriate
            transition effects.
          </p>
        </div>
      </div>
      
      <div className="bg-pink-100 p-6 rounded-lg border border-pink-300">
        <h2 className="text-xl font-semibold mb-3">Animation Performance</h2>
        <p className="mb-4">
          The animations should be smooth and performant, even when rapidly navigating
          between pages. The system uses CSS animations with hardware acceleration
          for optimal performance.
        </p>
        <p>
          Try navigating quickly between pages to test the animation system's
          ability to handle rapid transitions.
        </p>
      </div>
    </div>
  );
};

export default TestAnimation3;