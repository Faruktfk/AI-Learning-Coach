import {
  ChevronLeft,
  ChevronRight,
  MessageSquare,
  Moon,
  SquarePen,
  Sun,
  Trash2,
} from 'lucide-react';

function conversationButtonClass(isActive) {
  const base =
    'group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm transition';

  if (isActive) {
    return `${base} bg-zinc-200 text-zinc-950 dark:bg-zinc-900 dark:text-white`;
  }

  return `${base} text-zinc-700 hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-900`;
}

export default function Sidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onCreateConversation,
  onDeleteConversation,
  collapsed,
  onToggleCollapsed,
  theme,
  onToggleTheme,
}) {
  const faviconSrc = theme === 'dark' ? '/favicon_dark.png' : '/favicon_light.png';

  if (collapsed) {
    return (
      <aside className="flex h-screen w-[56px] shrink-0 flex-col items-center border-r border-zinc-200 bg-zinc-50 px-2 py-3 dark:border-zinc-800 dark:bg-black">
        {/* Logo / Expand Button */}
        <button
          onClick={onToggleCollapsed}
          className="group flex h-10 w-10 items-center justify-center rounded-xl transition hover:bg-zinc-200 dark:hover:bg-zinc-900"
          title="Sidebar öffnen"
        >
          <img
            src={faviconSrc}
            alt="AI Learning Coach"
            className="h-7 w-7 object-contain transition group-hover:hidden"
          />

          <ChevronRight
            size={20}
            className="hidden text-zinc-700 group-hover:block dark:text-zinc-200"
          />
        </button>

        {/* New Chat */}
        <button
          onClick={onCreateConversation}
          className="mt-5 flex h-10 w-10 items-center justify-center rounded-xl text-zinc-700 transition hover:bg-zinc-200 dark:text-zinc-200 dark:hover:bg-zinc-900"
          title="Neuer Chat"
        >
          <SquarePen size={20} />
        </button>

        {/* Collapsed Conversations */}
        <div className="mt-5 flex min-h-0 flex-1 flex-col items-center gap-1 overflow-y-auto">
          {conversations.map((conversation) => {
            const isActive = conversation.id === activeConversationId;

            return (
              <button
                key={conversation.id}
                onClick={() => onSelectConversation(conversation.id)}
                title={conversation.title || 'Neuer Chat'}
                className={
                  isActive
                    ? 'flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-200 text-zinc-950 transition dark:bg-zinc-900 dark:text-white'
                    : 'flex h-10 w-10 items-center justify-center rounded-xl text-zinc-600 transition hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-900'
                }
              >
                <MessageSquare size={18} />
              </button>
            );
          })}
        </div>

        {/* Theme Toggle fixed bottom */}
        <button
          onClick={onToggleTheme}
          className="flex h-10 w-10 items-center justify-center rounded-xl text-zinc-700 transition hover:bg-zinc-200 dark:text-zinc-200 dark:hover:bg-zinc-900"
          title="Theme wechseln"
        >
          {theme === 'dark' ? <Sun size={19} /> : <Moon size={19} />}
        </button>
      </aside>
    );
  }

  return (
    <aside className="flex h-screen w-[290px] shrink-0 flex-col border-r border-zinc-200 bg-zinc-50 px-3 py-3 dark:border-zinc-800 dark:bg-black">
      {/* Top Brand Row */}
      <div className="flex items-center justify-between px-2 py-1">
        <div className="flex min-w-0 items-center">
        <h1 className="truncate font-serif text-[22px] font-semibold tracking-tight text-zinc-950 dark:text-white">
          AI Learning Coach
        </h1>
      </div>

        <button
          onClick={onToggleCollapsed}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-zinc-600 transition hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-900"
          title="Sidebar zuklappen"
        >
          <ChevronLeft size={20} />
        </button>
      </div>

      {/* New Chat Section */}
      <div className="mt-6 px-1">
        <button
          onClick={onCreateConversation}
          className="flex w-full items-center justify-center gap-2 rounded-2xl border border-zinc-300 bg-white px-4 py-3 text-sm font-semibold text-zinc-900 shadow-sm transition hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-950 dark:text-white dark:hover:bg-zinc-900"
        >
          <SquarePen size={18} />
          Neuer Chat
        </button>
      </div>

      {/* Conversations */}
      <div className="mt-7 flex min-h-0 flex-1 flex-col">
        <div className="mb-2 flex items-center justify-between px-2">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-500 dark:text-zinc-500">
            Lernverläufe
          </p>
        </div>

        <div className="min-h-0 flex-1 space-y-1 overflow-y-auto pr-1">
          {conversations.length === 0 ? (
            <p className="px-2 py-3 text-sm text-zinc-500 dark:text-zinc-500">
              Noch keine Lernverläufe.
            </p>
          ) : (
            conversations.map((conversation) => {
              const isActive = conversation.id === activeConversationId;

              return (
                <div
                  key={conversation.id}
                  className={
                    isActive
                      ? 'group flex w-full items-center gap-2 rounded-xl bg-zinc-200 px-3 py-2.5 text-zinc-950 dark:bg-zinc-900 dark:text-white'
                      : 'group flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-zinc-700 transition hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-900'
                  }
                >
                  <button
                    onClick={() => onSelectConversation(conversation.id)}
                    className="flex min-w-0 flex-1 items-center gap-3 text-left text-sm"
                    title={conversation.title || 'Neuer Chat'}
                  >
                    <MessageSquare
                      size={17}
                      className="shrink-0 text-zinc-500 dark:text-zinc-500"
                    />

                    <span className="min-w-0 flex-1 truncate">
                      {conversation.title || 'Neuer Chat'}
                    </span>
                  </button>

                  <button
                    onClick={(event) => {
                      event.stopPropagation();

                      const shouldDelete = window.confirm(
                        `Konversation "${conversation.title || 'Neuer Chat'}" wirklich löschen?`,
                      );

                      if (shouldDelete) {
                        onDeleteConversation(conversation.id);
                      }
                    }}
                    className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-zinc-500 opacity-0 transition hover:bg-red-100 hover:text-red-600 group-hover:opacity-100 dark:text-zinc-500 dark:hover:bg-red-950/40 dark:hover:text-red-400"
                    title="Konversation löschen"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Bottom Theme Toggle */}
      <div className="mt-3 border-t border-zinc-200 pt-3 dark:border-zinc-900">
        <button
          onClick={onToggleTheme}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-zinc-700 transition hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-900"
          title="Theme wechseln"
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}

          <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
        </button>
      </div>
    </aside>
  );
}