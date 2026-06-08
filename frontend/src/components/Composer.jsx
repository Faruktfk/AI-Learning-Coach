import { SendHorizontal } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

export default function Composer({ mode, disabled, onSubmitText }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (mode.type === 'text') {
      textareaRef.current?.focus();
    }
  }, [mode.type]);

  if (mode.type !== 'text') return null;

  function submit() {
    const value = text.trim();
    if (!value || disabled) return;
    setText('');
    onSubmitText(value);
  }

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-4">
      <div className="mx-auto max-w-3xl">
        <div className="flex items-end gap-2 rounded-3xl border border-gray-300 bg-white px-4 py-3 shadow-sm focus-within:border-gray-400">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(event) => setText(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                submit();
              }
            }}
            rows={1}
            disabled={disabled}
            placeholder={mode.placeholder || 'Nachricht eingeben...'}
            className="max-h-40 min-h-7 flex-1 resize-none border-0 bg-transparent text-[15px] leading-7 text-gray-900 outline-none placeholder:text-gray-400 disabled:opacity-60"
          />

          <button
            onClick={submit}
            disabled={disabled || !text.trim()}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gray-900 text-white transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:bg-gray-300"
            aria-label="Senden"
          >
            <SendHorizontal size={17} />
          </button>
        </div>

        <div className="mt-2 text-center text-xs text-gray-400">
          Enter zum Senden · Shift+Enter für neue Zeile
        </div>
      </div>
    </div>
  );
}
