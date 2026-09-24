/*********** Phone Number Widget ***********/
import intlTelInput from 'intl-tel-input';

$(document).ready(function () {
    // https://github.com/jackocnr/intl-tel-input
    let phoneElements = document.querySelectorAll("input[autocomplete='tel'][type='text']")
    for (let i = 0; i < phoneElements.length; ++i){
        let phoneElement = phoneElements[i]
        let iti = intlTelInput(phoneElement, {
            loadUtils: () => import('intl-tel-input/utils'),
            hiddenInputs: () => ({
                phone: phoneElement.getAttribute("name") + phoneElement.getAttribute("fullSuffix"),
            }),
            countryOrder: ["us"],
            countrySearch: false,
            allowNumberExtensions: true,
            customPlaceholder: function(selectedCountryPlaceholder, selectedCountryData) {
                return selectedCountryPlaceholder + " ext. 4";
            },
        })

        // If intl-tel-input can't determine the country for the number, then
        // it does not send the country code. This makes it very hard to retain
        // what country was selected if there is an error. Instead of resorting
        // to heroics, set the country code to the US. This should either be
        // outright fixed in the future, or at least have the default country
        // be configurable.
        if (!iti.getSelectedCountry()) {
            iti.setSelectedCountry("us");
        }

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
});