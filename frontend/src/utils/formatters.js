// frontend/src/utils/formatters.js — Number and currency formatters

export const fmt = {
  currency: (n) =>
    typeof n === 'number'
      ? '$' + n.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })
      : '—',
  number: (n) => (typeof n === 'number' ? n.toLocaleString('en-US') : '—'),
  pct: (n) => (typeof n === 'number' ? n.toFixed(1) + '%' : '—'),
}
