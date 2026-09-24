window.Formification = (function($) {
    'use strict';

    /*********** Form ***********/
    var Form = function(instanceId, rulesData) {
        var fields = {};  // TODO: assuming order doesn't matter; create ordered_fields array if necessary

        // get form element
        this.$element = $('#' + instanceId);

        // init fields
        this.$element.find('.field-wrapper').each(function() {
            var $fieldWrapper = $(this);

            var $fieldElement = $fieldWrapper.find('input[type!="hidden"],select,textarea');
            var id = $fieldElement.data('id');

            fields[id] = new Field(id, $fieldWrapper, $fieldElement);
        });
        this.fields = fields;

        if ($.isEmptyObject(this.fields)) return;

        // init rules
        this.rules = [];
        for (var i = 0; i < rulesData.length; i++) {
            var ruleData = rulesData[i];

            this.rules.push(new Rule(this, ruleData));
        }

        // rules ready; init change listeners and evaluate rules
        this.initFieldChangeListeners();
        this.evaluateFields();
    };

    Form.prototype.evaluateFields = function() {
        // cycle through this.fields and eval rules
        for (var key in this.fields) {
            this.fields[key].evaluateObservedRules();
        }
    };

    Form.prototype.initFieldChangeListeners = function() {
        // TODO: only init listeners on Fields with subscriberRules
        for (var key in this.fields) {
            this.fields[key].initChangeListener();
        }
    };


    /*********** Rule Condition ***********/
    var RuleCondition = function(rule, conditionData) {
        this.rule = rule;

        this.field_id = conditionData.field_id;
        this.operator = conditionData.operator;
        this.value = conditionData.value;

        this.field = this.rule.form.fields[this.field_id];
        this.field && this.field.addSubscriberRule(this.rule);
    };

    RuleCondition.prototype.isMet = function() {
        if (!this.field) return false;
        var field = this.field;
        var actual = field.getValue();
        var expected = this.value;
        switch (this.operator) {
            case 'is': return field.hasValue(expected);
            case 'is_not': return !field.hasValue(expected);
            case 'any_selected':
            case 'all_selected':
                var values = Array.isArray(expected) ? expected : [expected];
                var matches = function(value) { return field.hasValue(value); };
                return this.operator === 'any_selected' ? values.some(matches) : values.every(matches);
            case 'greater_than':
            case 'less_than':
                if (actual == null || String(actual).trim() === '' || expected == null || String(expected).trim() === '') return false;
                var left = Number(actual), right = Number(expected);
                if (!Number.isFinite(left) || !Number.isFinite(right)) return false;
                return this.operator === 'greater_than' ? left > right : left < right;
            case 'contains':
            case 'does_not_contain':
            case 'begins_with':
            case 'ends_with':
                if (actual == null || expected == null) return false;
                actual = String(actual);
                expected = String(expected);
                if (this.operator === 'contains') return actual.includes(expected);
                if (this.operator === 'does_not_contain') return !actual.includes(expected);
                if (this.operator === 'begins_with') return actual.startsWith(expected);
                return actual.endsWith(expected);
            default: return false;
        }
    };


    /*********** Rule Result ***********/
    var RuleResult = function(rule, resultData) {
        this.rule = rule;

        this.action = resultData.action;
        this.field = this.rule.form.fields[resultData.field_id];
        this.field && this.field.addObserverRule(this.rule);

        if (this.action == RuleResult.ACTIONS.CHANGE_OPTION_GROUP) {
            if (!this.field.hasGroups()) {
                console.error('Invalid RuleResult action: ' + this.action + ' can\'t apply to this field');
            }

            this.optionGroupId = resultData.option_group_id;
        }
    };

    // constants
    RuleResult.ACTIONS = {
        SHOW: 'show',
        HIDE: 'hide',
        CHANGE_OPTION_GROUP: 'change-option-group'
    };

    RuleResult.prototype.updateResult = function(field, displayStatus) {
        if (this.field === field) {
            if (this.action == RuleResult.ACTIONS.SHOW) {
                displayStatus.setVisibility(true);
            } else if (this.action == RuleResult.ACTIONS.HIDE) {
                displayStatus.setVisibility(false);
            } else if (this.action == RuleResult.ACTIONS.CHANGE_OPTION_GROUP) {
                displayStatus.setSelectedOptionGroup(this.optionGroupId);
            } else {
                console.error('Invalid RuleResult action: ' + this.action);
            }
        }
    };

    /*********** Rule ***********/
    var Rule = function(form, ruleData) {
        this.form = form;

        this.operator = ruleData.operator;

        // init conditions
        this.conditions = [];
        for (var i = 0; i < ruleData.conditions.length; i++) {
            var conditionData = ruleData.conditions[i];

            this.conditions.push(new RuleCondition(this, conditionData));
        }

        // init results
        this.results = [];
        for (i = 0; i < ruleData.results.length; i++) {
            var resultData = ruleData.results[i];

            this.results.push(new RuleResult(this, resultData));
        }
    };

    Rule.OPERATORS = {
        AND: 'and',
        OR: 'or'
    };

    Rule.prototype.notifyObservingFields = function() {
        for (var i = 0; i < this.results.length; i++) {
            this.results[i].field.evaluateObservedRules();
        }
    };

    Rule.prototype.conditionsMet = function() {
        var requireAll = (this.operator == Rule.OPERATORS.AND);
        var allTrue = true;
        var anyTrue = false;

        for (var i = 0; i < this.conditions.length; i++) {
            if (this.conditions[i].isMet()) {
                anyTrue = true;
            } else {
                allTrue = false;
            }
        }

        if (allTrue) {
            return true;
        } else if (!requireAll && anyTrue) {
            return true;
        } else {
            return false;
        }
    };

    Rule.prototype.evaluate = function(field, displayStatus) {
        if (this.conditionsMet()) {
            for (var i = 0; i < this.results.length; i++) {
                this.results[i].updateResult(field, displayStatus);
            }
        }
    };


    /*********** FieldStatus ***********/
    var FieldStatus = function(displayParams) {
        // defaults
        this._visible = true;
        this._selected_option_group = null;

        // override defaults
        if ('visible' in displayParams) {
            this.setVisibility(displayParams['visible']);
        }
    };

    FieldStatus.prototype.setVisibility = function(visible) {
        if (visible !== null) {
            this._visible = visible;
        }
    };

    FieldStatus.prototype.isVisible = function() {
        return this._visible;
    };

    FieldStatus.prototype.setSelectedOptionGroup = function(groupId) {
        this._selected_option_group = groupId;
    };

    FieldStatus.prototype.selectedOptionGroup = function() {
        return this._selected_option_group;
    };


    /*********** Field ***********/
    var Field = function(id, $wrapper, $element) {
        this.id = id;
        this.$wrapper = $wrapper;
        this.$element = $element;

        this.subscriberRules = [];
        this.observedRules = [];

        var isGrouped = this.$element.data('group-id');
        if (typeof isGrouped !== "undefined") {
            // Setup GroupedChoiceFields
            this.$groupHiddenElement = this.$wrapper.find('input[type="hidden"]');
            this.$groupFieldWrapperElements = this.$wrapper.find('select,ul');

            this.setupSync();
            this.setOptionGroup(null);
        }
    };

    Field.prototype.addSubscriberRule = function(rule) {
        this.subscriberRules.push(rule);
    };

    Field.prototype.addObserverRule = function(rule) {
        this.observedRules.push(rule);
    };

    Field.prototype.initChangeListener = function() {
        var thisObj = this;
        this.$element.on('change.formification', function() {
            thisObj.notifySubscriberRules();
        });
    };

    Field.prototype.evaluateObservedRules = function() {
        var newFieldStatus = new FieldStatus({});
        for (var i = 0; i < this.observedRules.length; i++) {
            this.observedRules[i].evaluate(this, newFieldStatus);
        }

        // apply field status
        this.setVisibility(newFieldStatus.isVisible());
        this.setOptionGroup(newFieldStatus.selectedOptionGroup());
    };

    Field.prototype.notifySubscriberRules = function() {
        for (var i = 0; i < this.subscriberRules.length; i++) {
            this.subscriberRules[i].notifyObservingFields();
        }
    };

    Field.prototype.setVisibility = function(visible) {
        if (visible) {
            this.$wrapper.show();
            this.$element.removeAttr("disabled");
            this.$element.data("required") && this.$element.prop("required", true);
        } else {
            // Clear out any selections or text when field is hidden
            this.resetValue();
            this.$wrapper.hide();
            this.$element.attr("disabled", "disabled");
            this.$element.prop("required", false);
        }
    };

    Field.prototype.resetValue = function() {
        if (this.hasGroups()) {
            this.selectedValues = [];
        } else if (this.$element.attr("type") == "checkbox") {
            /*
            TODO: consider resetting to default checked value.  I hesitate to do it
            now because re-checking an un-checked box seems unintuitive if it was
            temporarily hidden for some reason.
            DO NOT ALLOW CHECKBOXES IN ELSE, THOUGH!
            */
        } else {
            this.$element.val("");
        }
    };

    Field.prototype.hasValue = function(value) {
        if (this.hasFieldType('checkboxinput')) {
            return this.$element[0].checked;
        } else {
            var fieldValue = this.getValue();

            if (fieldValue instanceof Array) {
                return fieldValue.some(function(item) { return String(item) === String(value); });
            } else {
                return fieldValue == value;
            }
        }
    };

    Field.prototype.hasFieldType = function(fieldType) {
        return this.$wrapper.hasClass(fieldType);
    };

    Field.prototype.getCheckboxValue = function() {
        if (this.hasFieldType('checkboxinput')) {
            // standard single-field checkbox
            return this.$element.checked;

        } else if (this.hasFieldType('checkboxselectmultiple')) {
            // multi-checkbox
            var $currentElement;
            if (this.hasGroups()) {
                $currentElement = this.$currentGroupFieldElement;
            } else {
                $currentElement = this.$element;
            }

            var values = [];
            $currentElement.each(function() {
                if (this.checked) {
                    values.push($(this).val());
                }
            });

            return values;

        } else {
            console.error('Invalid checkbox type');
            return null;
        }
    };

    Field.prototype.getRadioSelectValue = function() {
        var wrapper;
        if (this.hasGroups()) {
            wrapper = this.$currentGroupFieldWrapper;
        } else {
            wrapper = this.$wrapper;
        }
        return wrapper.find('input:radio:checked').val();
    };

    Field.prototype.getSelectValue = function() {
        var $fieldElement;
        if (this.hasGroups()) {
            $fieldElement = this.$currentGroupFieldElement;
        } else {
            $fieldElement = this.$element;
        }

        return $fieldElement.val();
    };

    Field.prototype.getValue = function() {
        var inputType = this.$element.attr('type');
        if (inputType == 'checkbox') {
            return this.getCheckboxValue();
        } else if (inputType == 'radio') {
            return this.getRadioSelectValue();
        } else if (this.hasFieldType('select', 'selectmultiple')) {
            return this.getSelectValue();
        } else {
            return this.$element.val();
        }
    };

    Field.prototype.hasGroups = function() {
        return (typeof this.$groupFieldWrapperElements !== 'undefined');
    };

    Field.prototype.setOptionGroup = function(newGroupId) {
        if (this.hasGroups()) {
            var thisField = this;
            this.$groupHiddenElement.val(newGroupId);

            this.$groupFieldWrapperElements.each(function() {
                var groupId = $(this).data('group-id');
                if (typeof groupId === 'undefined') {
                    groupId = $(this).find('input').data('group-id');
                }

                if (groupId == newGroupId) {
                    $(this).show();
                    $(this).data("required") && $(this).prop("required", true);
                    thisField.$currentGroupFieldWrapper = $(this);
                    if (thisField.$currentGroupFieldWrapper.prop('tagName').toLowerCase() == "select") {
                        thisField.$currentGroupFieldElement = thisField.$currentGroupFieldWrapper;
                    } else {
                        thisField.$currentGroupFieldElement = $(this).find('input');
                    }

                    if (this.nodeName == 'SELECT') {
                        // Selects
                        $(this).val(thisField.selectedValues);

                        if ($(this).find("option:selected").length < 1) {
                            // No options selected; select ""
                            $(this).val("");
                        }

                    } else {
                        // Checkboxes / Radio Buttons
                        $(this).find('input').each(function() {
                            $(this).prop('checked', ($.inArray($(this).val(), thisField.selectedValues) > -1));
                        });
                    }
                } else {
                    $(this).hide();
                    $(this).prop('required', false);
                }
            });
        }
    };

    /**
     * Setup process to keep grouped field values synced
     */
    Field.prototype.setupSync = function() {
        var thisField = this;
        thisField.selectedValues = thisField.$groupHiddenElement.data('initial') || [];
        if (!(thisField.selectedValues instanceof Array)) {
            /*
                1. Convert numbers to string
                2. Add that string to an array
             */
            thisField.selectedValues = [thisField.selectedValues.toString()];
        }
        this.$groupFieldWrapperElements.each(function() {
            if (this.nodeName == 'SELECT') {
                // Selects

                // After validation, a step is needed to collect values before reset
                $(this).find('option:selected').each(function() {
                    if ($(this).val()) {
                        thisField.selectedValues.push($(this).val());
                    }
                });

                $(this).change(function() {
                    // clear array
                    thisField.selectedValues.length = 0;

                    // append all values
                    if ($(this).val() instanceof Array) {
                        thisField.selectedValues.push.apply(thisField.selectedValues, $(this).val());
                    } else {
                        thisField.selectedValues.push($(this).val());
                    }
                });
            } else {
                // Checkboxes / Radio Buttons
                $(this).find('input').change(function() {
                    var checked = this.checked;
                    var valueExistsAt = $.inArray($(this).val(), thisField.selectedValues);

                    if (checked && valueExistsAt < 0) {
                        thisField.selectedValues.push($(this).val());
                    } else if (!checked && valueExistsAt > -1) {
                        thisField.selectedValues.splice(valueExistsAt, 1);
                    }
                });
            }
        });
    };


    /****************************************/
    /*********** module functions ***********/
    /****************************************/
    var _forms = {};
    var forms = {};

    /**
     * Initialize a form and retain it
     * @param instanceId unique identifier of form in Formification JS and HTML
     * @param rulesData dictionary of serialized Rules
     */
    forms.add = function(instanceId, rulesData) {
        _forms[instanceId] = new Form(instanceId, rulesData);
    };

    return { forms: forms };
})($);
