import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { sendJsonToBackend } from './backend-funcs/json-send'
import { loadJsonFromBackend } from './backend-funcs/json-load'

function App() {
    const [count, setCount] = useState(0)

    const handleJsonTest = async () => {
        const filename = "sample";
        const data = {
            name: "Test from React",
            count,
            timestamp: new Date().toISOString(),
        };

        try {
            const saveResponse = await sendJsonToBackend(filename, data);
            console.log("✅ Saved:", saveResponse);

            const loadResponse = await loadJsonFromBackend(filename);
            console.log("📥 Loaded:", loadResponse);
        } catch (err) {
            console.error("❌ Error:", err);
        }
    }

    return (
        <>
            <div>
                <a href="https://vite.dev" target="_blank">
                    <img src={viteLogo} className="logo" alt="Vite logo" />
                </a>
                <a href="https://react.dev" target="_blank">
                    <img src={reactLogo} className="logo react" alt="React logo" />
                </a>
            </div>
            <h1>Vite + React</h1>
            <div className="card">
                <button onClick={() => setCount((count) => count + 1)}>
                    count is {count}
                </button>
                <p>
                    Edit <code>src/App.tsx</code> and save to test HMR
                </p>
                <button onClick={handleJsonTest}>
                    Save & Load JSON
                </button>
            </div>
            <p className="read-the-docs">
                Click on the Vite and React logos to learn more
            </p>
        </>
    )
}

export default App
