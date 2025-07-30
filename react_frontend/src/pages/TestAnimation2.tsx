import React from 'react';
import { Link } from 'react-router-dom';

const TestAnimation2: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Animation Test Page 2</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-yellow-100 p-6 rounded-lg border border-yellow-300 shadow-sm">
          <h2 className="text-xl font-semibold mb-3">Test Page 2</h2>
          <p className="mb-4">
            This is the second test page. The animation when navigating here from
            Test Page 1 should be different from when navigating back.
          </p>
          <div className="flex space-x-4">
            <Link 
              to="/test" 
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
            >
              Back to Test Page 1
            </Link>
            <Link 
              to="/test3" 
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition"
            >
              Go to Test Page 3
            </Link>
          </div>
        </div>
        
        <div className="bg-red-100 p-6 rounded-lg border border-red-300 shadow-sm">
          <h2 className="text-xl font-semibold mb-3">Animation Direction</h2>
          <p>
            When navigating from a shallower route to a deeper route (like from /test to /test2),
            the content should slide in from the right. When navigating back, it should slide in
            from the left.
          </p>
        </div>
      </div>
      
      <div className="bg-blue-100 p-6 rounded-lg border border-blue-300">
        <h2 className="text-xl font-semibold mb-3">Testing Instructions</h2>
        <ol className="list-decimal pl-5 space-y-2">
          <li>Navigate between pages using the links</li>
          <li>Observe the direction and smoothness of animations</li>
          <li>Try using browser back/forward buttons</li>
          <li>Check that there's no flash of unstyled content</li>
        </ol>
      </div>
    </div>
  );
};

export default TestAnimation2;