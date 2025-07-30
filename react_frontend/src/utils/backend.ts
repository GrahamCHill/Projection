export async function fetchAvailableJsonFiles(): Promise<string[]> {
    const res = await fetch("http://localhost:8000/list-json");
    const data = await res.json();
    return data.files || [];
}

export async function sendJsonToBackend(filename: string, jsonData: any) {
    const res = await fetch(`http://localhost:8000/save-json/${filename}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(jsonData),
    });
    return res.json();
}

export async function loadJsonFromBackend(filename: string) {
    const res = await fetch(`http://localhost:8000/load-json/${filename}`);
    return res.json();
}
