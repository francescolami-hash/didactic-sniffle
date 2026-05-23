const chatRoot = document.querySelector(".ai-chat");

if (chatRoot) {
    const toggle = chatRoot.querySelector(".ai-chat-toggle");
    const panel = chatRoot.querySelector(".ai-chat-panel");
    const closeButton = chatRoot.querySelector(".ai-chat-close");
    const messages = chatRoot.querySelector(".ai-chat-messages");
    const form = chatRoot.querySelector(".ai-chat-form");
    const input = chatRoot.querySelector("#ai-chat-input");

    const setOpen = (isOpen) => {
        panel.hidden = !isOpen;
        toggle.setAttribute("aria-expanded", String(isOpen));

        if (isOpen) {
            input.focus();
        }
    };

    const addMessage = (text, sender) => {
        const message = document.createElement("div");
        message.className = `ai-chat-message ai-chat-message-${sender}`;
        message.textContent = text;
        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;
        return message;
    };

    toggle.addEventListener("click", () => {
        setOpen(panel.hidden);
    });

    closeButton.addEventListener("click", () => {
        setOpen(false);
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const userMessage = input.value.trim();

        if (!userMessage) {
            return;
        }

        addMessage(userMessage, "user");
        input.value = "";
        input.disabled = true;

        const loadingMessage = addMessage("Thinking...", "bot");

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: userMessage }),
            });
            const data = await response.json();

            loadingMessage.textContent = data.answer || data.error || "I could not answer right now.";
        } catch (error) {
            loadingMessage.textContent = "The chat is temporarily unavailable. Please try again later.";
        } finally {
            input.disabled = false;
            input.focus();
        }
    });
}
