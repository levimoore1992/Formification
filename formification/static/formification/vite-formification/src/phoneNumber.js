/*********** Phone Number Widget ***********/
import intlTelInput from 'intl-tel-input';

export function initializePhoneInputs(formElement) {
    const phoneElements = formElement.querySelectorAll('input[data-formification-phone]');
    for (const phoneElement of phoneElements) {
        if (intlTelInput.getInstance(phoneElement)) continue;
        let iti = intlTelInput(phoneElement, {
            loadUtils: () => import('intl-tel-input/utils'),
            hiddenInputs: () => ({
                phone: phoneElement.getAttribute("name") + phoneElement.getAttribute("fullSuffix"),
            }),
            countryOrder: ["us"],
            initialCountry: "us",
            countrySelectorMode: "DROPDOWN",
            dropdownParent: null,
            countrySearch: false,
            allowNumberExtensions: true,
            customPlaceholder: function(selectedCountryPlaceholder, selectedCountryData) {
                return selectedCountryPlaceholder + " ext. 4";
            },
        })

        // On clicking away, try and reformat the number.
         phoneElement.addEventListener('blur', function() {
            // If blank, return early.
            if (phoneElement.value.trim().length === 0) return;


             if (iti.isValidNumber()) {
                 let extension = iti.getExtension()
                 if (extension){
                     let formattedNumber = iti.getNumber() + phoneElement.getAttribute("extensionPrefix") + iti.getExtension();
                     iti.setNumber(formattedNumber);
                 }
                 else {
                     iti.setNumber(iti.getNumber());
                 }
             }
        });
    }
}
