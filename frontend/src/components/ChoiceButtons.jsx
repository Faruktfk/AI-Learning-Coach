export default function ChoiceButtons({ mode, disabled, onChoose }) {
  if (mode.type !== 'buttons') return null;

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-4">
      <div className="mx-auto flex max-w-3xl flex-wrap justify-center gap-3">
        {mode.options.map((option) => (
          <button
            key={option.value}
            onClick={() => onChoose(option.value, option.label)}
            disabled={disabled}
            className="rounded-2xl border border-gray-300 bg-white px-5 py-3 text-sm font-medium text-gray-900 shadow-sm transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}
