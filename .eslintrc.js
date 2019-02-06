module.exports = {
  extends: [
    'airbnb-base',
  ],
  rules: {
    'curly': ['error', 'all'],
    'brace-style': ['error', '1tbs', { allowSingleLine: false }],
    'object-curly-newline': ['error', { multiline: true, consistent: true }],
    'no-param-reassign': 'off',
    'prefer-destructuring': 'off',
    'quote-props': ['error', 'consistent-as-needed', { keywords: false, unnecessary: true, numbers: false }],
  },
};
