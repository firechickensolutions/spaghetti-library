const assert = require('node:assert/strict');
const { createRequire } = require('node:module');
const { test } = require('node:test');

const requireFromJestConfig = createRequire(require.resolve('jest-config/package.json'));
const merge = requireFromJestConfig('deepmerge');

test('merges Jest globals without changing either input', () => {
    const preset = { globals: { flags: ['a'], enabled: false, retained: 3 } };
    const config = { globals: { flags: ['b'], enabled: true } };

    assert.deepEqual(merge(preset, config), {
        globals: { flags: ['a', 'b'], enabled: true, retained: 3 }
    });
    assert.deepEqual(preset, { globals: { flags: ['a'], enabled: false, retained: 3 } });
    assert.deepEqual(config, { globals: { flags: ['b'], enabled: true } });
});

test('ignores reserved prototype keys before reading either input', () => {
    const reservedKey = '__proto__';
    const record = {};
    Object.defineProperty(record, reservedKey, {
        enumerable: true,
        get() {
            assert.fail('The merge read a reserved key');
        }
    });

    const cases = [
        [record, {}],
        [Object.create(null), record],
        [{ globals: record }, { globals: {} }],
        [{ globals: null }, { globals: record }]
    ];

    for (const [target, source] of cases) {
        const result = merge(target, source);
        assert.equal(Object.getPrototypeOf(result), Object.prototype);
        assert.equal(Object.hasOwn(result, reservedKey), false);
        if (result.globals) {
            assert.equal(Object.getPrototypeOf(result.globals), Object.prototype);
            assert.equal(Object.hasOwn(result.globals, reservedKey), false);
        }
    }
});
