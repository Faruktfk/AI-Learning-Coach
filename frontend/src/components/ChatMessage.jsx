import { useEffect, useMemo, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, User } from 'lucide-react';

function useTypewriter(text, enabled, onDone) {
  const words = useMemo(() => String(text || '').split(/(\s+)/), [text]);
  const [visibleIndex, setVisibleIndex] = useState(enabled ? 0 : words.length);
  const onDoneRef = useRef(onDone);

  useEffect(() => {
    onDoneRef.current = onDone;
  }, [onDone]);

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
        onDoneRef.current?.();
      }
    }, 22);

    return () => window.clearInterval(interval);
  }, [enabled, words.length, text]);

  return words.slice(0, visibleIndex).join('');
}

function MarkdownContent({ content }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => <h1 className="mb-3 mt-2 text-2xl font-semibold leading-tight">{children}</h1>,
        h2: ({ children }) => <h2 className="mb-2 mt-5 text-xl font-semibold leading-tight">{children}</h2>,
        h3: ({ children }) => <h3 className="mb-2 mt-4 text-lg font-semibold leading-tight">{children}</h3>,
        p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
        ul: ({ children }) => <ul className="mb-3 list-disc space-y-1 pl-6">{children}</ul>,
        ol: ({ children }) => <ol className="mb-3 list-decimal space-y-1 pl-6">{children}</ol>,
        li: ({ children }) => <li className="pl-1">{children}</li>,
        strong: ({ children }) => <strong className="font-semibold text-zinc-950 dark:text-white">{children}</strong>,
        em: ({ children }) => <em className="italic">{children}</em>,
        a: ({ href, children }) => (
          <a href={href} target="_blank" rel="noreferrer" className="underline decoration-zinc-400 underline-offset-4 hover:text-emerald-600">
            {children}
          </a>
        ),
        code: ({ inline, children }) =>
          inline ? (
            <code className="rounded bg-zinc-200 px-1 py-0.5 text-[0.9em] dark:bg-zinc-800">{children}</code>
          ) : (
            <code className="block overflow-x-auto rounded-2xl bg-zinc-100 p-4 text-sm dark:bg-zinc-900">{children}</code>
          ),
        pre: ({ children }) => <pre className="mb-3 overflow-x-auto rounded-2xl bg-zinc-100 dark:bg-zinc-900">{children}</pre>,
        blockquote: ({ children }) => (
          <blockquote className="mb-3 border-l-4 border-zinc-300 pl-4 text-zinc-700 dark:border-zinc-700 dark:text-zinc-300">
            {children}
          </blockquote>
        ),
        table: ({ children }) => (
          <div className="mb-3 overflow-x-auto">
            <table className="w-full border-collapse text-sm">{children}</table>
          </div>
        ),
        th: ({ children }) => <th className="border border-zinc-300 px-3 py-2 text-left dark:border-zinc-700">{children}</th>,
        td: ({ children }) => <td className="border border-zinc-300 px-3 py-2 dark:border-zinc-700">{children}</td>,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

export default function ChatMessage({ message, onAnimationDone }) {
  const isUser = message.role === 'user';
  const shouldType = message.role === 'assistant' && message.stream === true;
  const visibleContent = useTypewriter(message.content, shouldType, onAnimationDone);

  return (
    <div className={`group w-full ${isUser ? 'bg-transparent' : 'bg-white dark:bg-black'}`}>
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

        <div className="min-w-0 flex-1 break-words text-[15px] leading-7 text-zinc-900 dark:text-zinc-100">
          <MarkdownContent content={visibleContent} />

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
