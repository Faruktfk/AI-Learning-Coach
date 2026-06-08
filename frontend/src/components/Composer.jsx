import { SendHorizonal } from 'lucide-react';
import { useState } from 'react';

export default function Composer({ disabled, placeholder, onSubmit }) {
  const [value, setValue] = useState('');

  function submit() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;

    setValue('');
    onSubmit(trimmed);
  }

  return (
    <div className="border-t border-zinc-200 bg-white px-4 py-4 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="mx-auto flex max-w-3xl items-end gap-2 rounded-2xl border border-zinc-300 bg-white p-2 shadow-sm dark:border-zinc-700 dark:bg-zinc-800">
        <textarea
          value={value}
          disabled={disabled}
          placeholder={placeholder}
          rows={1}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault();
              submit();
            }
          }}
          className="max-h-36 min-h-[44px] flex-1 resize-none bg-transparent px-3 py-3 text-sm text-zinc-950 outline-none placeholder:text-zinc-500 disabled:opacity-50 dark:text-zinc-100"
        />

        <button
          disabled={disabled || !value.trim()}
          onClick={submit}
          className="mb-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-zinc-900 text-white transition hover:bg-zinc-700 disabled:cursor-not-allowed disabled:bg-zinc-300 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-white dark:disabled:bg-zinc-700 dark:disabled:text-zinc-400"
        >
          <SendHorizonal size={18} />
        </button>
      </div>
    </div>
  );
}
