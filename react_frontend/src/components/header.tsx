import React from 'react';
import { Link } from 'react-router-dom';
import MenuComponent from './menu';

const Header: React.FC = () => {
    return (
        <>
            {/* Header with Main site title and menu */}
            <header className="bg-blue-600 text-white px-6 shadow-md left-0 right-0 z-50 flex items-center gap-8"
             style={{ position: 'fixed', top: 0, width: '100vw', display: 'flex', justifyContent: 'space-between', alignItems: 'center'
            }}>
                <h1 className="text-xl font-bold" style={{paddingLeft: '1.5rem'}}><Link to="/"> Projection</Link></h1>
                <MenuComponent  />
            </header>

        </>
    );
};

export default Header;
