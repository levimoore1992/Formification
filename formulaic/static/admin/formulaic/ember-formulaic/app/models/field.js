import DS from 'ember-data';
import BaseField from './basefield';

export default BaseField.extend({
    textfield: DS.belongsTo('textfield', {async: false}),
    choicefield: DS.belongsTo('choicefield', {async: false}),
    booleanfield: DS.belongsTo('booleanfield', {async: false}),
    hiddenfield: DS.belongsTo('hiddenfield', {async: false}),
    captchafield: DS.belongsTo('captchafield', {async: false}),
    content_type: DS.attr('number')
});
