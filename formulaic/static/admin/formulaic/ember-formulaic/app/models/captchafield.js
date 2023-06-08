import DS from 'ember-data';
import BaseField from './basefield';
import CaptchaFieldValidator from '../validators/fields/captchafield';

export default BaseField.extend({
    field: DS.belongsTo('field'),

    init() {
        this._super(...arguments);
        this.validator = CaptchaFieldValidator.create({field: this});
    }
});
