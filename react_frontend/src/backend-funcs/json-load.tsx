export async function loadJsonFromBackend(filename: string) {
    const res = await fetch(`http://localhost:8000/load-json/${filename}`);

    if (!res.ok) throw new Error("Failed to load JSON");
    return await res.json();
}
