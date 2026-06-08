export default function ChoiceButtons({ kind, disabled, onChoose }) {
  const options = kind === 'adapt_decision'
    ? [
        { label: 'Nochmal', value: 'nochmal' },
        { label: 'Skip', value: 'skip' },
      ]
    : [
        { label: 'Ja', value: 'ja' },
        { label: 'Nein', value: 'nein' },
      ];

  return (
    <div className="border-t border-zinc-200 bg-white px-4 py-4 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="mx-auto flex max-w-3xl flex-wrap gap-3">
        {options.map((option) => (
          <button
            key={option.value}
            disabled={disabled}
            onClick={() => onChoose(option.value)}
            className="rounded-2xl border border-zinc-300 bg-white px-5 py-3 text-sm font-medium text-zinc-900 transition hover:bg-zinc-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100 dark:hover:bg-zinc-700"
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}
