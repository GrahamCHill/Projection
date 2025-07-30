import React from 'react';

const About: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">About This Application</h1>
      <p className="mb-4">
        This is a test page to verify that our route transition solution works correctly.
        The page should load with a smooth transition without any flash of unstyled content.
      </p>
      <div className="bg-blue-100 p-4 rounded-lg border border-blue-300">
        <h2 className="text-xl font-semibold mb-2">Features</h2>
        <ul className="list-disc pl-5">
          <li>Smooth page transitions</li>
          <li>No flash of unstyled content</li>
          <li>Consistent user experience</li>
        </ul>
      </div>
    </div>
  );
};

export default About;