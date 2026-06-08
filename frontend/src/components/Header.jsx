import { Moon, Sun, MessageSquarePlus } from 'lucide-react';

export default function Header({ activeConversation, theme, onToggleTheme, onNewConversation }) {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-zinc-200 bg-white px-4 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="min-w-0">
        <h1 className="truncate text-sm font-semibold text-zinc-900 dark:text-zinc-100">
          {activeConversation?.title || 'AI Learning Coach'}
        </h1>
        <p className="text-xs text-zinc-500 dark:text-zinc-400">
          Wikipedia-basierter adaptiver Tutor
        </p>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={onNewConversation}
          className="rounded-xl p-2 text-zinc-600 transition hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800 md:hidden"
          title="Neuer Chat"
        >
          <MessageSquarePlus size={19} />
        </button>

        <button
          onClick={onToggleTheme}
          className="rounded-xl p-2 text-zinc-600 transition hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
          title="Theme wechseln"
        >
          {theme === 'dark' ? <Sun size={19} /> : <Moon size={19} />}
        </button>
      </div>
    </header>
  );
}
