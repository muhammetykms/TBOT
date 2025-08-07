window.stateMap = {};

function updateStateHolder(input, ifBlokId, stateId) {
    const stateAdi = input.value.trim();

    if (!stateAdi) {
        console.log("❌ STATE adı boş. Lütfen bir isim girin.");
        return;
    }

    // Aynı isim başka blokta tanımlanmış mı kontrol et
    const zatenVar = Object.entries(window.stateMap).some(
        ([key, val]) => val.state_name === stateAdi && key !== stateId
    );


    if (zatenVar) {
        console.log(`⚠️ STATE zaten başka blokta tanımlı: "${stateAdi}"`);
        return;
    }

    // Map'e ekle veya güncelle
    window.stateMap[stateId] = {
        state_name: stateAdi,
        if_blok_id: ifBlokId,
        blok_id: stateId
    };

    console.log(`✅ STATE güncellendi: "${stateAdi}"`);
    console.log("🧠 stateMap:", window.stateMap);

    updateStateDropdowns();
    updateProsesBlokButon(); // ✅ Buraya ekledik
}



// dropdown'ları güncelleyen fonksiyon
function updateStateDropdowns() {
    const stateList = Object.values(window.stateMap);
    const dropdowns = document.querySelectorAll(".state-dropdown");

    dropdowns.forEach(dropdown => {
        const selectedValues = Array.from(dropdown.selectedOptions).map(opt => opt.value);

        // Temizle
        dropdown.innerHTML = '';

        // Seçenekleri yeniden oluştur
        stateList.forEach(state => {
            const opt = document.createElement("option");
            opt.value = state.state_name;
            opt.textContent = state.state_name;

            if (selectedValues.includes(state.state_name)) {
                opt.selected = true;
            }

            dropdown.appendChild(opt);
        });

        // Select2'yi yeniden başlat (önce varsa destroy et)
        if ($(dropdown).hasClass("select2-hidden-accessible")) {
            $(dropdown).select2("destroy");
        }

        $(dropdown).select2({
            placeholder: "State seçin",
            width: '100%',
            allowClear: true
        }).on('change', handleDropdownChange); ;

        $(dropdown).val(selectedValues).trigger("change");
    });

    console.log("🔄 Select2 state dropdown'ları güncellendi.");
}


// remove state// Bu fonksiyon, state bloğunu kaldırır ve ilgili state_add_btn butonunu görünür hale getirir.
function removeState(button, blokId) {
    const stateBlock = button.closest('.state-tanim');
    if (!stateBlock) return;

    // 1. STATE ID'yi al (data-blok-id varsa)
    const stateId = stateBlock.dataset.blokId;
    if (stateId && window.stateMap[stateId]) {
        delete window.stateMap[stateId];
        console.log(`🗑️ STATE silindi: ${stateId}`);
        console.log("🧠 Güncel stateMap:", window.stateMap);
    }

    // 2. Kapsayıcı olan IF bloğunu bul
    let container = stateBlock.closest('.if-blok, .inside-buy, .ic-ve-blok, .veya-blok, .pre-buy-bolumu');
    if (!container) {
        console.warn("Kapsayıcı blok bulunamadı, tüm dökümanda arama yapılıyor.");
        container = document;
    }

    // 3. Sadece bu kapsayıcı içinde, state_add_btn butonunu blok_id'ye göre bul
    const stateAddBtn = container.querySelector('.state_add_btn[data-blok-id="' + blokId + '"]');

    if (stateAddBtn) {
        console.log("🎯 Bulunan buton:", stateAddBtn);
        stateAddBtn.classList.remove('d-none');
    } else {
        console.warn("⚠️ state_add_btn bulunamadı. blok_id:", blokId);
    }

    // 4. DOM'dan kaldır
    stateBlock.remove();

    // 5. Dropdown'ları da güncelle
    updateStateDropdowns();
    updateProsesBlokButon(); // ✅ Buraya da ekledik
}


function updateProsesBlokButon() {
    const stateCount = Object.keys(window.stateMap).length;

    // En az bir state varsa, tüm .proses_ekle_btn butonlarını göster
    const prosesBtns = document.querySelectorAll('.proses_ekle_btn');

    prosesBtns.forEach(btn => {
        if (stateCount > 0) {
            btn.classList.remove('d-none');
        } else {
            btn.classList.add('d-none');
        }
    });
}
