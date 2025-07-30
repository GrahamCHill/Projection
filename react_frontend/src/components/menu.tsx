import React, { useState } from 'react';
import { Link } from 'react-router-dom';

type MenuItem = {
    title: string;
    href: string;
};

const menuItems: MenuItem[] = [
    { title: 'Home', href: '/' },
    { title: 'About', href: '/about' },
    // Add more here...
    { title: 'Departments', href: '/departments' },
    { title: 'Employee Contracts', href: '/contracts' },
];

const Menu: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className="relative ml-auto">
            {/* Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="p-2 text-white hover:text-gray-300 focus:outline-none"
                aria-label="Toggle menu"
            >
        <span className="text-xl font-bold">
          {isOpen ? '✖' : '☰'}
        </span>
            </button>

            {/* Dropdown */}
            {isOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white shadow-lg rounded-md overflow-hidden z-50 border border-gray-200">
                    {menuItems.map(({ title, href }) => (
                        <Link
                            key={href}
                            to={href}
                            className="block px-4 py-3 text-sm text-gray-800 hover:bg-gray-100 transition"
                            onClick={() => setIsOpen(false)}
                        >
                            {title}
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Menu;
