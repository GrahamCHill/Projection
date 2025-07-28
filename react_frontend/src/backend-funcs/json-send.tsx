export async function sendJsonToBackend(filename: string, data: any) {
    const res = await fetch(`http://localhost:8000/save-json/${filename}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });

    if (!res.ok) throw new Error("Failed to save JSON");
    return await res.json();
}
