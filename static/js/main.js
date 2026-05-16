document.addEventListener("DOMContentLoaded", () => {
    if (window.lucide) window.lucide.createIcons();

    const nav = document.querySelector(".nav");
    const navToggle = document.querySelector(".nav-toggle");
    navToggle?.addEventListener("click", () => nav?.classList.toggle("open"));

    const fileInput = document.querySelector("#resumes");
    const dropZone = document.querySelector(".drop-zone");
    const count = document.querySelector("[data-file-count]");
    const updateCount = () => {
        if (!fileInput || !count) return;
        const total = fileInput.files.length;
        count.textContent = total ? `${total} file${total === 1 ? "" : "s"} selected` : "No files selected";
    };
    fileInput?.addEventListener("change", updateCount);
    ["dragenter", "dragover"].forEach((eventName) => {
        dropZone?.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropZone.classList.add("dragging");
        });
    });
    ["dragleave", "drop"].forEach((eventName) => {
        dropZone?.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropZone.classList.remove("dragging");
        });
    });
    dropZone?.addEventListener("drop", (event) => {
        if (fileInput && event.dataTransfer.files.length) {
            fileInput.files = event.dataTransfer.files;
            updateCount();
        }
    });

    const form = document.querySelector("[data-processing-form]");
    const overlay = document.querySelector("[data-processing-overlay]");
    const message = document.querySelector("[data-processing-message]");
    const messages = ["Extracting resume text", "Running NLP engine", "Calculating ATS score", "Ranking candidates"];
    form?.addEventListener("submit", () => {
        overlay?.classList.add("active");
        let index = 0;
        window.setInterval(() => {
            index = (index + 1) % messages.length;
            if (message) message.textContent = messages[index];
        }, 1200);
    });

    document.querySelectorAll("[data-table-search]").forEach((input) => {
        input.addEventListener("input", () => filterTable(input.dataset.tableSearch));
    });
    document.querySelectorAll("[data-status-filter]").forEach((select) => {
        select.addEventListener("change", () => filterTable(select.dataset.statusFilter));
    });

    function filterTable(tableId) {
        const table = document.getElementById(tableId);
        if (!table) return;
        const search = document.querySelector(`[data-table-search="${tableId}"]`)?.value.toLowerCase() || "";
        const status = document.querySelector(`[data-status-filter="${tableId}"]`)?.value || "";
        table.querySelectorAll("tbody tr").forEach((row) => {
            const matchesSearch = row.textContent.toLowerCase().includes(search);
            const matchesStatus = !status || row.dataset.status === status;
            row.style.display = matchesSearch && matchesStatus ? "" : "none";
        });
    }

    const canvas = document.getElementById("heroScene");
    if (canvas) {
        const ctx = canvas.getContext("2d");
        let width, height, t = 0;
        const resize = () => {
            width = canvas.width = canvas.offsetWidth * devicePixelRatio;
            height = canvas.height = canvas.offsetHeight * devicePixelRatio;
        };
        resize();
        window.addEventListener("resize", resize);
        const draw = () => {
            t += 0.006;
            ctx.clearRect(0, 0, width, height);
            ctx.globalAlpha = 0.45;
            for (let x = 0; x < width; x += 52 * devicePixelRatio) {
                for (let y = 0; y < height; y += 52 * devicePixelRatio) {
                    const pulse = Math.sin(x * 0.004 + y * 0.003 + t * 4);
                    ctx.fillStyle = pulse > 0.82 ? "rgba(47,228,189,.42)" : "rgba(78,163,255,.08)";
                    ctx.fillRect(x, y, 1.4 * devicePixelRatio, 1.4 * devicePixelRatio);
                }
            }
            requestAnimationFrame(draw);
        };
        draw();
    }
});

