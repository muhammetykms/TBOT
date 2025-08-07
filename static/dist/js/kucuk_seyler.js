// state tanımını tutacak değişken

// sadece pozitif tam sayıları kabul eden bir input alanı için JavaScript fonksiyonu:
// Sadece pozitif tam sayıları ve en fazla 3 haneli değeri kabul eden input
function allowOnlyPositiveIntegers(input) {
    // Rakam olmayan karakterleri temizle
    input.value = input.value.replace(/[^\d]/g, '');

    // Başındaki sıfır(ları) kaldır
    input.value = input.value.replace(/^0+/, '');

    // Maksimum 3 hane sınırı
    if (input.value.length > 3) {
        input.value = input.value.slice(0, 3);
    }
}









// remove state kapanis
function removeStateKapanis(button, blokId) {
    const kapanmaBlock = button.closest('.if_state_kapanma_sarti');
    if (!kapanmaBlock) return;

    // 1. Kapsayıcı olan IF veya süreç bloklarını bul
    let container = kapanmaBlock.closest('.if-blok, .inside-buy, .ic-ve-blok, .veya-blok, .pre-buy-bolumu');
    if (!container) {
        console.warn("Kapsayıcı blok bulunamadı, tüm dökümanda arama yapılıyor.");
        container = document;
    }

    // 2. Kapanma Şartı Ekle butonunu blok_id'ye göre bul
    const stateKapanmaAddBtn = container.querySelector(`.if_state_kapanma_sarti_btn[data-blok-id="${blokId}"]`);

    if (stateKapanmaAddBtn) {
        console.log("Bulunan kapanma ekle butonu:", stateKapanmaAddBtn);
        stateKapanmaAddBtn.classList.remove('d-none');  // class'ı kaldır
        stateKapanmaAddBtn.style.display = 'inline-block'; // istersen ekstra görünürlük garantisi için
    } else {
        console.warn("if_state_kapanma_sarti_btn bulunamadı. blok_id:", blokId);
    }

    // 3. Kapanma bloğunu kaldır
    kapanmaBlock.remove();
}


// remove proses blok
function removeProsesBlok(button, blokId) {
    const prosesBlok = button.closest('.proses-blok');
    if (!prosesBlok) return;

    // 1. Üst container (sureç veya genel blok) bulunur
    let container = prosesBlok.closest('.pre-buy-bolumu, .inside-buy, .after-sell, .surec-blok, .veya-blok, .ic-ve-blok');
    if (!container) {
        console.warn("Kapsayıcı blok bulunamadı, tüm dökümanda arama yapılıyor.");
        container = document;
    }

    // 2. Aynı blok_id'ye sahip proses ekle butonu bulunur (varsa)
    const prosesAddBtn = container.querySelector(`.proses_ekle_btn[data-blok-id="${blokId}"]`);

    if (prosesAddBtn) {
        console.log("Bulunan proses ekle butonu:", prosesAddBtn);
        prosesAddBtn.classList.remove('d-none');
        prosesAddBtn.style.display = 'inline-block';
    } else {
        console.warn("proses_ekle_btn bulunamadı. blok_id:", blokId);
    }

    // 3. Proses bloğu kaldırılır
    prosesBlok.remove();
}



// silme fonksiyonu

function removeBlock(button, parentId = null) {
    const block = button.closest('.ic-ve-blok, .veya-blok');
    if (!block) return;

    if (!parentId) {
        parentId = button.getAttribute('data-parent-id') || block.getAttribute('data-parent-id');
    }

    const btnClass = block.getAttribute('data-btn-class');

    console.log('parentId:', parentId, 'btnClass:', btnClass);

    const targetBtn = document.querySelector('.' + btnClass + '[data-blok-id="' + parentId + '"]');

    if (targetBtn) {
        targetBtn.classList.remove('d-none');
    } else {
        console.warn('Buton bulunamadı:', parentId, btnClass);
    }

    block.remove();
}


    


// aksiyon şeysi

document.addEventListener('htmx:beforeRequest', function (e) {
    const triggerEl = e.target;  // Buton elementi
    if (!triggerEl.matches('.inside_buy_btn')) return;

    const blokElement = triggerEl.closest('[data-target-container-id]');
    if (!blokElement) return;

    const targetId = blokElement.getAttribute('data-target-container-id');

    // İsteği yapacak elementin target'ını güncelle
    triggerEl.setAttribute('hx-target', `#${targetId}`);
});



// buton gizle 

    document.addEventListener('click', function (e) {
        // Aksiyon Ekle butonu tıklaması
        const aksiyonBtn = e.target.closest('.aksiyon_ekle_btn');
        if (aksiyonBtn) {
            e.preventDefault();
            const parentId = aksiyonBtn.getAttribute('data-blok-id');
            const selector = [
                `.aksiyon_ekle_btn[data-blok-id="${parentId}"]`,
                `.if_ekle_btn[data-blok-id="${parentId}"]`,
                `.ic_veya_ekle_btn[data-blok-id="${parentId}"]`,
                `.proses_ekle_btn[data-blok-id="${parentId}"]`
            ].join(',');
            document.querySelectorAll(selector).forEach(btn => btn.style.display = 'none');
            return;
        }
    
        // İç Veya Grubu Ekle butonu tıklaması
        const icVeyaBtn = e.target.closest('.ic_veya_ekle_btn');
        if (icVeyaBtn) {
            e.preventDefault();
            const parentId = icVeyaBtn.getAttribute('data-blok-id');
            const selector = [
                `.aksiyon_ekle_btn[data-blok-id="${parentId}"]`,
                `.if_ekle_btn[data-blok-id="${parentId}"]`,
                `.ic_veya_ekle_btn[data-blok-id="${parentId}"]`,
                `.proses_ekle_btn[data-blok-id="${parentId}"]`
            ].join(',');
            document.querySelectorAll(selector).forEach(btn => btn.style.display = 'none');
            return;
        }
    });

    
// aksiyon kapatılınca aksiyon ekle butonunu göster 

    document.addEventListener('click', function (e) {
        // Hem aksiyon iptal hem de ic veya iptal butonuna tıklama kontrolü
        if (e.target.matches('.aksiyon_iptal, .veya_iptal')) {
            // İlgili bloğu bul (aksiyon-blok ya da ic-veya-blok gibi)
            const iptalBlok = e.target.closest('.aksiyon-blok, .ic-veya-blok, .veya-blok');
            if (!iptalBlok) return;
    
            // Blok ID'yi al (data-parent-id zorunlu!)
            const parentBlokId = iptalBlok.getAttribute('data-parent-id');
            iptalBlok.remove();
    
            // Aynı parent'a sahip tüm ekleme butonlarını tekrar görünür yap
            const selector = [
                `.aksiyon_ekle_btn[data-blok-id="${parentBlokId}"]`,
                `.if_ekle_btn[data-blok-id="${parentBlokId}"]`,
                `.ic_veya_ekle_btn[data-blok-id="${parentBlokId}"]`,
                `.proses_ekle_btn[data-blok-id="${parentBlokId}"]`
            ].join(',');
    
            document.querySelectorAll(selector).forEach(btn => {
                btn.style.display = '';
            });
        }
    });

    
// if ekle

    document.body.addEventListener("htmx:configRequest", function(evt) {
        const btn = evt.target.closest(".ve_if_blogu_ekle_btn");
        if (btn) {
            evt.detail.parameters['blok_id'] = btn.dataset.blokId;
            evt.detail.parameters['grup_tipi'] = 've';
        }
    });


// select 

    document.body.addEventListener("htmx:afterSwap", function(evt) {
        const newSelects = evt.target.querySelectorAll('select.select2');

        newSelects.forEach(function(selectEl) {
            if ($(selectEl).hasClass("select2-hidden-accessible")) {
                $(selectEl).select2('destroy');
            }

            $(selectEl).select2({
                width: 'resolve'
            });

            // Sadece tek seçim kalması için event ekle
            $(selectEl).on('select2:select', function (e) {
                const selectedValue = e.params.data.id;

                // Tüm seçimleri kaldır
                $(this).val(null).trigger('change');

                // Sadece yeni seçimi ayarla
                $(this).val([selectedValue]).trigger('change');
            });
        });
    });


// deneme select2 dropdown select

    document.body.addEventListener("htmx:afterSwap", function(evt) {
    const newSelects = evt.target.querySelectorAll('select.select2');

    newSelects.forEach(function(selectEl) {
        if ($(selectEl).hasClass("select2-hidden-accessible")) {
            $(selectEl).select2('destroy');
        }

        $(selectEl).select2({
            width: 'resolve'
        });

        $(selectEl).on('select2:select', function (e) {
            const selectedValue = e.params.data.id;

            // Tek seçim zorlaması
            $(this).val([selectedValue]).trigger('change');

            // HTMX isteğini manuel tetikleyelim:
            this.dispatchEvent(new Event("change", { bubbles: true }));
        });
    });
});




 


// csrf

  document.body.addEventListener('htmx:configRequest', (event) => {
    const token = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    event.detail.headers['X-CSRFToken'] = token;
  });


// silme grup çarpı butonları

$(document).on('click', '.sil-btn', function(e) {
    e.preventDefault();

    // Hangi grubu sileceğiz? En yakın parent .ve-grubu
    var grup = $(this).closest('.ve-grubu, .veya-grubu');
    if (grup.length) {
        grup.remove();
    }

    // Eğer id güncellemek istiyorsan ana container'ı bul ve güncelle:
    var anaContainer = grup.closest('.pre-buy-bolumu, #inside_buy_container, #after_sell_container');
    if (anaContainer.length) {
        guncelleIfBlokIdleri('#' + anaContainer.attr('id'));
    }
});

