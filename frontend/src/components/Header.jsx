import { MessageSquarePlus, PanelRightClose, PanelRightOpen } from 'lucide-react';

export default function Header({ activeConversation, onNewConversation, learningProgressOpen, onToggleLearningProgress }) {
  return (
    <header className="flex h-11 shrink-0 items-center justify-between border-b border-zinc-200 bg-white px-3 dark:border-zinc-800 dark:bg-black">
      <div className="min-w-0">
        <h1 className="truncate text-sm font-medium text-zinc-900 dark:text-zinc-100">
          {activeConversation?.title || 'AI Learning Coach'}
        </h1>
      </div>

      <button
        onClick={onToggleLearningProgress}
        className="flex h-9 w-9 items-center justify-center rounded-xl text-zinc-600 transition hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-900 hidden lg:block"
        title={
          learningProgressOpen
            ? 'Fortschritt ausblenden'
            : 'Fortschritt anzeigen'
        }
      >
        {learningProgressOpen ? (
          <PanelRightClose size={19} />
        ) : (
          <PanelRightOpen size={19} />
        )}
      </button>
      
    </header>
  );
}
