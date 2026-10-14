import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import postcss from 'postcss';

test('every distributed widget CSS selector stays inside the form', () => {
  const css = readFileSync(new URL('../../dist/form.css', import.meta.url), 'utf8');
  assert.ok(!css.includes('Bootstrap'));
  postcss.parse(css).walkRules(rule => {
    if (rule.parent.type === 'atrule' && /keyframes$/.test(rule.parent.name)) return;
    for (const selector of rule.selectors) assert.ok(selector.startsWith('.formification-form'), selector);
  });
});

test('the optional theme contains no global selectors or remote imports', () => {
  const css = readFileSync(new URL('../../css/form-theme.css', import.meta.url), 'utf8');
  const root = postcss.parse(css);
  root.walkAtRules('import', () => assert.fail('Theme must be self contained'));
  root.walkRules(rule => {
    for (const selector of rule.selectors) assert.ok(selector.startsWith('.formification-form'), selector);
  });
});
