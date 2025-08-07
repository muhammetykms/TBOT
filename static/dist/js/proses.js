

document.body.addEventListener('htmx:afterSwap', function(evt) {
    updateStateDropdowns(); // yeni gelen dropdown'lar da doldurulsun
});


function handleDropdownChange(event) {
    const dropdown = event.target;
    const selectedNames = $(dropdown).val();  // ['RSI_KIRILDI', 'MAC_ALTINDA']
    const takipStateIdList = [];

    // stateMap'i tarayıp isim eşleşenleri bul
    Object.values(window.stateMap).forEach(state => {
        if (selectedNames.includes(state.state_name)) {
            takipStateIdList.push(state.blok_id);  // ← artık blok_id'leri alıyoruz
        }
    });

    const prosesBlok = dropdown.closest('.proses-blok');
    if (prosesBlok) {
        prosesBlok.dataset.takipStateId = JSON.stringify(takipStateIdList);
        console.log("📌 Takip edilen state blok ID'leri:", takipStateIdList);
    }
}




// Sayfa yüklendiğinde dinleme başlasın
document.addEventListener("DOMContentLoaded", function () {
    document.body.addEventListener('change', function (e) {
        if (e.target.matches('.state-dropdown')) {
            handleDropdownChange(e);
        }
    });
});
