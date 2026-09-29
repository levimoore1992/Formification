import './dist/form.js';

const initializedForms = new WeakSet();

export function initializeForm({ instanceId, rules }) {
    const element = document.getElementById(instanceId);
    if (!element || initializedForms.has(element)) return;

    window.Formification.forms.add(instanceId, rules);
    initializedForms.add(element);
    const container = element.closest('.bootstrap-form') || element;
    container.querySelector('.form-errors-summary')?.scrollIntoView();
}
