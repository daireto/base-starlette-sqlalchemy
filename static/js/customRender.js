function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getReactionEmoji(reaction) {
    if (reaction == "LIKE") return "👍";
    if (reaction == "DISLIKE") return "👎";
    if (reaction == "LOVE") return "❤️";
    if (reaction == "LAUGH") return "😆";
    if (reaction == "SAD") return "😥";
    if (reaction == "HUSHED") return "😯";
    if (reaction == "ANGRY") return "😡";
    return "❓";
}

Object.assign(render, {
    tags: function render(data, type, _, _, _) {
        if (data == null) return null_column();
        if (data.length == 0) return empty_column();
        data = data.map((d) => escapeHtml(d));
        if (type != "display") return data.join(",");
        return `<div class="d-flex flex-row">${data
            .map(
                (tag) =>
                    `<span class="me-1 badge bg-purple-lt"><i class="fa fa-tag"></i> ${tag}</span>`
            )
            .join("")}</div>`;
    },
    reaction: function render(data, _, _, _, _) {
        if (data == null) return null_column();
        if (data.length == 0) return empty_column();
        data = escapeHtml(data);
        return `<span style="font-size: 25px;">${getReactionEmoji(data)}</span>`;
    },
});
