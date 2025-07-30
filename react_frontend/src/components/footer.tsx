import React from 'react';

const Footer: React.FC = () => {
    return (
        <footer className="bg-gray-800 text-white text-center py-4 mt-auto">
            <p>&copy; {new Date().getFullYear()} My React App. All rights reserved.</p>
        </footer>
    );
};

export default Footer;
