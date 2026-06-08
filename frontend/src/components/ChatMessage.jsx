import { useEffect, useMemo, useState } from 'react';
import { Bot, User } from 'lucide-react';

function useTypewriter(text, enabled, onDone) {
  const words = useMemo(() => String(text || '').split(/(\s+)/), [text]);
  const [visibleIndex, setVisibleIndex] = useState(enabled ? 0 : words.length);

  useEffect(() => {
    if (!enabled) {
      setVisibleIndex(words.length);
      return;
    }

    setVisibleIndex(0);
    let index = 0;

    const interval = window.setInterval(() => {
      index += 1;
      setVisibleIndex(index);

      if (index >= words.length) {
        window.clearInterval(interval);
        onDone?.();
      }
    }, 22);

    return () => window.clearInterval(interval);
  }, [enabled, words.length, text]);

  return words.slice(0, visibleIndex).join('');
}

export default function ChatMessage({ message, onAnimationDone}) {
  const isUser = message.role === 'user';
  const shouldType = message.role === 'assistant' && message.stream === true;
  const visibleContent = useTypewriter(message.content, shouldType, onAnimationDone);

  return (
    <div className={`group w-full ${isUser ? 'bg-transparent' : 'bg-white dark:bg-zinc-900'}`}>
      <div className="mx-auto flex w-full max-w-3xl gap-4 px-4 py-5">
        <div
          className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
            isUser
              ? 'bg-zinc-800 text-white dark:bg-zinc-200 dark:text-zinc-900'
              : 'bg-emerald-600 text-white'
          }`}
        >
          {isUser ? <User size={17} /> : <Bot size={17} />}
        </div>

        <div className="min-w-0 flex-1 whitespace-pre-wrap break-words text-[15px] leading-7 text-zinc-900 dark:text-zinc-100">
          {visibleContent}
          {shouldType && visibleContent.length < String(message.content || '').length ? (
            <span className="ml-0.5 inline-block h-4 w-1 animate-pulse rounded bg-zinc-700 align-middle dark:bg-zinc-200" />
          ) : null}

          {message.downloadUrl ? (
            <div className="mt-4">
              <a
                href={message.downloadUrl}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center rounded-xl bg-zinc-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-zinc-700 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-white"
              >
                Handout-PDF herunterladen
              </a>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
