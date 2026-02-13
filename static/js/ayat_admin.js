document.addEventListener("DOMContentLoaded", function () {

    const surahSelect = document.getElementById("id_surah");
    const ayatSelect = document.getElementById("id_ayat_number");
    const textBox = document.getElementById("id_text");

    const saveBtn = document.querySelector('input[name="_save"]');
    const saveAddBtn = document.querySelector('input[name="_addanother"]');


    if (!surahSelect || !ayatSelect || !textBox) {
        return; // Safety check
    }


    // -----------------------
    // Load Ayats by Surah
    // -----------------------
    function loadAyats(surah, selectedAyat = null) {

        ayatSelect.innerHTML = "";
        ayatSelect.appendChild(new Option("Select Ayat", ""));

        if (!window.QURAN_DATA) return;

        const count = QURAN_DATA[surah];

        for (let i = 1; i <= count; i++) {

            const option = new Option("Ayat " + i, i);

            if (selectedAyat && i == selectedAyat) {
                option.selected = true;
            }

            ayatSelect.appendChild(option);
        }
    }


    // -----------------------
    // Surah change
    // -----------------------
    surahSelect.addEventListener("change", function () {

        const selectedSurah = this.value;

        if (!selectedSurah) return;

        loadAyats(selectedSurah);

        if (textBox.tagName === "TEXTAREA") {
            textBox.value = "";
        }
    });


    // -----------------------
    // Ayat change
    // -----------------------
    ayatSelect.addEventListener("change", function () {

        if (!this.value) {
            textBox.value = "";
            return;
        }

        fetch(`/quran/get-ayat/?surah=${surahSelect.value}&ayat=${this.value}`)
            .then(res => res.json())
            .then(data => {

                if (data.text && textBox) {
                    textBox.value = data.text;
                }
            })
            .catch(err => console.log("Error:", err));
    });


    // -----------------------
    // Edit Mode
    // -----------------------
    if (surahSelect.value) {

        const currentAyat = ayatSelect.dataset.current;

        loadAyats(
            surahSelect.value,
            currentAyat ? parseInt(currentAyat) : null
        );
    }


    // -----------------------
    // Enable buttons safely
    // -----------------------
    if (saveBtn) saveBtn.disabled = false;
    if (saveAddBtn) saveAddBtn.disabled = false;

});
