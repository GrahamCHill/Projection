import { useState, useEffect } from "react";
import reactLogo from './assets/react.svg';
import viteLogo from '/vite.svg';
import './App.css';
import { sendJsonToBackend } from './backend-funcs/json-send';
import { loadJsonFromBackend } from './backend-funcs/json-load';

function App() {
    const [count, setCount] = useState(0);
    const [saveFilename, setSaveFilename] = useState("");
    const [loadFilename, setLoadFilename] = useState("");
    const [availableFiles, setAvailableFiles] = useState<string[]>([]);
    const [loadedData, setLoadedData] = useState<never>();

    // Fetch available JSON files from backend
    useEffect(() => {
        fetch("http://localhost:8000/list-json")
            .then(res => res.json())
            .then(data => setAvailableFiles(data.files || []))
            .catch(console.error);
    }, []);

    const handleSave = async () => {
        if (!saveFilename.trim()) {
            alert("Please enter a filename to save.");
            return;
        }
        const data = {
            name: "Test from React",
            count,
            timestamp: new Date().toISOString(),
        };
        try {
            const saveResponse = await sendJsonToBackend(saveFilename.trim(), data);
            console.log("✅ Saved:", saveResponse);
            alert(`Saved as ${saveFilename}.json`);
            // Refresh file list
            fetch("http://localhost:8000/list-json")
                .then(res => res.json())
                .then(data => setAvailableFiles(data.files || []))
                .catch(console.error);
        } catch (err) {
            console.error("❌ Save error:", err);
            alert("Failed to save JSON");
        }
    };

    const handleLoad = async () => {
        if (!loadFilename) {
            alert("Please select a filename to load.");
            return;
        }
        try {
            const data = await loadJsonFromBackend(loadFilename);
            setLoadedData(data);
            console.log("📥 Loaded:", data);
        } catch (err) {
            console.error("❌ Load error:", err);
            alert("Failed to load JSON");
        }
    };

    const handleJsonTest = async () => {
        // Original simple test, just saves/loads "sample"
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
            setLoadedData(loadResponse);
        } catch (err) {
            console.error("❌ Error:", err);
        }
    };

    return (
        <>
            <div>
                <a href="https://vite.dev" target="_blank" rel="noreferrer">
                    <img src={viteLogo} className="logo" alt="Vite logo" />
                </a>
                <a href="https://react.dev" target="_blank" rel="noreferrer">
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

                <hr />

                <div style={{ marginBottom: "1rem" }}>
                    <h2>Save JSON File</h2>
                    <input
                        type="text"
                        placeholder="Enter filename (without .json)"
                        value={saveFilename}
                        onChange={(e) => setSaveFilename(e.target.value)}
                    />
                    <button onClick={handleSave} style={{ marginLeft: "0.5rem" }}>
                        Save JSON
                    </button>
                </div>

                <div style={{ marginBottom: "1rem" }}>
                    <h2>Load JSON File</h2>
                    <select
                        value={loadFilename}
                        onChange={(e) => setLoadFilename(e.target.value)}
                    >
                        <option value="">-- Select a file --</option>
                        {availableFiles.map((file) => (
                            <option key={file} value={file.replace(/\.json$/, "")}>
                                {file}
                            </option>
                        ))}
                    </select>
                    <button onClick={handleLoad} style={{ marginLeft: "0.5rem" }}>
                        Load JSON
                    </button>
                </div>

                {loadedData && (
                    <div>
                        <h3>Loaded JSON Content:</h3>
                        <pre>{JSON.stringify(loadedData, null, 2)}</pre>
                    </div>
                )}

                <hr />

                <button onClick={handleJsonTest}>Save & Load JSON (Sample)</button>
            </div>

            <p className="read-the-docs">
                Click on the Vite and React logos to learn more
            </p>
        </>
    );
}

export default App;
