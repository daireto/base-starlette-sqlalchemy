async function renderBgImage(imageUrl, elementId, clearInnerHTML = false) {
    /*
        Example usage:
        renderBgImage('https://example.com/image.png', 'myDiv');
    */
    console.log("Fetching and rendering image...");
    try {
        const response = await fetch(imageUrl);
        if (!response.ok) {
            throw new Error(`Failed to fetch image: ${response.statusText}`);
        }

        const blob = await response.blob();

        const base64 = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });

        const element = document.getElementById(elementId);
        if (element) {
            element.style.backgroundImage = `url('${base64}')`;
            if (clearInnerHTML) element.innerHTML = "";
        } else {
            console.error(`Element with ID "${elementId}" not found.`);
        }
    } catch (error) {
        console.error("Error fetching and rendering image:", error);
    }
}
