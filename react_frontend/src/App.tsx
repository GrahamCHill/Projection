import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Header from './components/header';
import Footer from './components/footer';
import RouteTransition from './components/RouteTransition';
import Home from './pages/Home';
import About from './pages/About';
import TestAnimation from './pages/TestAnimation';
import TestAnimation2 from './pages/TestAnimation2';
import TestAnimation3 from './pages/TestAnimation3';

function App() {
    return (
        <Router>
            <Header />
            <main className="p-4">
                <RouteTransition>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/about" element={<About />} />
                        <Route path="/test" element={<TestAnimation />} />
                        <Route path="/test2" element={<TestAnimation2 />} />
                        <Route path="/test3" element={<TestAnimation3 />} />
                    </Routes>
                </RouteTransition>
            </main>
            <Footer />
        </Router>
    );
}

export default App;
