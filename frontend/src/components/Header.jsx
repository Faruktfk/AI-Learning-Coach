import { MessageSquarePlus } from 'lucide-react';

export default function Header({ activeConversation, onNewConversation }) {
  return (
    <header className="flex h-11 shrink-0 items-center justify-between border-b border-zinc-200 bg-white px-3 dark:border-zinc-950 dark:bg-black">
      <div className="min-w-0">
        <h1 className="truncate text-sm font-medium text-zinc-900 dark:text-zinc-100">
          {activeConversation?.title || 'AI Learning Coach'}
        </h1>
      </div>

      <button
        onClick={onNewConversation}
        className="rounded-xl p-2 text-zinc-600 transition hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-900 md:hidden"
        title="Neuer Chat"
      >
        <MessageSquarePlus size={18} />
      </button>
    </header>
  );
}
