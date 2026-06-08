import { Menu, RotateCcw } from 'lucide-react';

export default function Header({ session, isBusy, onNewSession }) {
  const title = session?.article_title || 'AI Learning Coach';
  const subtitle = session?.current_chunk_title
    ? `${session.current_state} · Abschnitt ${session.current_chunk_index + 1}/${session.chunk_count}: ${session.current_chunk_title}`
    : session?.current_state || 'Bereit';

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-gray-200 bg-white px-4">
      <div className="flex min-w-0 items-center gap-3">
        <button className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 md:hidden" aria-label="Menü">
          <Menu size={20} />
        </button>

        <div className="min-w-0">
          <div className="truncate text-sm font-semibold text-gray-900">{title}</div>
          <div className="truncate text-xs text-gray-500">{subtitle}</div>
        </div>
      </div>

      <button
        onClick={onNewSession}
        disabled={isBusy}
        className="inline-flex items-center gap-2 rounded-xl border border-gray-200 px-3 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-60"
      >
        <RotateCcw size={16} />
        Neu
      </button>
    </header>
  );
}
