import { MessageSquarePlus, GraduationCap, Trash2 } from 'lucide-react';

export default function Sidebar({
  conversations,
  activeConversationId,
  onNewConversation,
  onSelectConversation,
  onDeleteConversation,
}) {
  return (
    <aside className="hidden w-72 shrink-0 border-r border-zinc-200 bg-zinc-50 p-3 dark:border-zinc-800 dark:bg-zinc-950 md:flex md:flex-col">
      <button
        onClick={onNewConversation}
        className="mb-4 flex w-full items-center gap-2 rounded-xl border border-zinc-300 bg-white px-3 py-2 text-left text-sm font-medium text-zinc-900 transition hover:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:bg-zinc-800"
      >
        <MessageSquarePlus size={18} />
        Neuer Lern-Chat
      </button>

      <div className="mb-2 flex items-center gap-2 px-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">
        <GraduationCap size={15} />
        Lernverläufe
      </div>

      <div className="scrollbar-thin flex-1 space-y-1 overflow-y-auto pr-1">
        {conversations.map((conversation) => {
          const active = conversation.id === activeConversationId;

          return (
            <div
              key={conversation.id}
              className={`group flex items-center rounded-xl text-sm transition ${
                active
                  ? 'bg-zinc-200 text-zinc-950 dark:bg-zinc-800 dark:text-white'
                  : 'text-zinc-700 hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-900'
              }`}
            >
              <button
                onClick={() => onSelectConversation(conversation.id)}
                className="min-w-0 flex-1 truncate px-3 py-2 text-left"
                title={conversation.title}
              >
                {conversation.title}
              </button>

              <button
                onClick={() => onDeleteConversation(conversation.id)}
                className="mr-1 rounded-lg p-1 text-zinc-500 opacity-0 transition hover:bg-zinc-300 hover:text-red-600 group-hover:opacity-100 dark:hover:bg-zinc-700"
                title="Chat löschen"
              >
                <Trash2 size={15} />
              </button>
            </div>
          );
        })}
      </div>
    </aside>
  );
}
