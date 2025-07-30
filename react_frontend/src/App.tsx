import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Header from './components/header';
import Footer from './components/footer';
import Home from './pages/Home';

function App() {
    return (
        <Router>
            <Header />
            <main className="p-4">
                <Routes>
                    <Route path="/" element={<Home />} />
                    {/* Add more routes like:
          <Route path="/settings" element={<Settings />} />
          */}
                </Routes>
            </main>
            <Footer />
        </Router>
    );
}

export default App;
