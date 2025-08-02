import React from 'react';
import { Link } from 'react-router-dom';
import MenuComponent from './menu';

const Header: React.FC = () => {
    return (
        <>
            {/* Header with Main site title and menu */}
            <header className="bg-blue-600 text-white py-4 px-6 shadow-md">
                <h1 className="text-xl font-bold"><Link to="/"> Projection</Link></h1>
            </header>
            <MenuComponent />
        </>
    );
};

export default Header;
