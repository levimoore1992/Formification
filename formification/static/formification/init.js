import { forms, initializePhoneInputs } from './dist/form.js';

const initializedForms = new WeakSet();

export function initializeForm({ instanceId, rules }) {
    const element = document.getElementById(instanceId);
    if (!element || initializedForms.has(element)) return;

    element.classList.add("formification-form");
    initializePhoneInputs(element);
    forms.add(instanceId, rules || []);
    initializedForms.add(element);
    const container = element.closest('.formification-form') || element;
    container.querySelector('.form-errors-summary')?.scrollIntoView();
}
