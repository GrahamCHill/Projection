import React, { useEffect, useState } from 'react';
import {
    fetchAvailableJsonFiles,
    sendJsonToBackend,
    loadJsonFromBackend
} from '../utils/backend';

const Home: React.FC = () => {
    const [count, setCount] = useState(0);
    const [saveFilename, setSaveFilename] = useState("");
    const [loadFilename, setLoadFilename] = useState("");
    const [availableFiles, setAvailableFiles] = useState<string[]>([]);
    const [loadedData, setLoadedData] = useState<never>();

    useEffect(() => {
        fetchAvailableJsonFiles()
            .then(setAvailableFiles)
            .catch(console.error);
    }, []);

    const handleSave = async () => {
        if (!saveFilename.trim()) {
            alert("Please enter a filename to save.");
            return;
        }

        const data = { name: "Test from React", count, timestamp: new Date().toISOString() };
        try {
            await sendJsonToBackend(saveFilename.trim(), data);
            alert(`Saved as ${saveFilename}.json`);
            const updatedFiles = await fetchAvailableJsonFiles();
            setAvailableFiles(updatedFiles);
        } catch (err) {
            console.error(err);
            alert("Save failed");
        }
    };

    const handleLoad = async () => {
        if (!loadFilename) {
            alert("Please select a filename.");
            return;
        }
        try {
            const data = await loadJsonFromBackend(loadFilename);
            setLoadedData(data);
        } catch (err) {
            console.error(err);
            alert("Load failed");
        }
    };

    return (
        <div className="card">
            <button onClick={() => setCount((c) => c + 1)}>count is {count}</button>

            <hr />
            <div>
                <h2>Save JSON</h2>
                <input
                    type="text"
                    placeholder="Enter filename"
                    value={saveFilename}
                    onChange={(e) => setSaveFilename(e.target.value)}
                />
                <button onClick={handleSave}>Save</button>
            </div>

            <div>
                <h2>Load JSON</h2>
                <select value={loadFilename} onChange={(e) => setLoadFilename(e.target.value)}>
                    <option value="">-- Select a file --</option>
                    {availableFiles.map((f) => (
                        <option key={f} value={f.replace(/\.json$/, "")}>{f}</option>
                    ))}
                </select>
                <button onClick={handleLoad}>Load</button>
            </div>

            {loadedData && (
                <div>
                    <h3>Loaded Content:</h3>
                    <pre>{JSON.stringify(loadedData, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

export default Home;
