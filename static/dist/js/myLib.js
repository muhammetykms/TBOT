class MyLib {
    constructor() {
        this.log("Kütüphane başlatıldı.");
    }

    log(mesaj) {
        console.log("[MyLib]: " + mesaj);
    }

    toggle(selector) {
        $(selector).toggle();
    }

    gizle(selector) {
        $(selector).hide();
    }

    goster(selector) {
        $(selector).show();
    }

    mesaj(metin) {
        alert(metin);
    }
}
MyLib.prototype.dragDropEtkinlestir = function(dragSelector, dropSelector, onDropCallback = null) {
    const dragEl = document.querySelector(dragSelector);
    const dropEl = document.querySelector(dropSelector);

    if (!dragEl || !dropEl) {
        this.log("Drag veya drop elementi bulunamadı.");
        return;
    }

    dragEl.setAttribute("draggable", true);

    dragEl.addEventListener("dragstart", function(e) {
        e.dataTransfer.setData("text/plain", dragEl.id);
    });

    dropEl.addEventListener("dragover", function(e) {
        e.preventDefault(); // Drop'a izin vermek için
    });

    dropEl.addEventListener("drop", function(e) {
        e.preventDefault();
        const data = e.dataTransfer.getData("text/plain");
        const dragged = document.getElementById(data);
        dropEl.appendChild(dragged);

        if (typeof onDropCallback === "function") {
            onDropCallback(dragged, dropEl);
        }
    });
};
