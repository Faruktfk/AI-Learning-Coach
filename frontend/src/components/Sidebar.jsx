import { BookOpen, MessageSquarePlus, Trash2 } from 'lucide-react';

function shortSessionTitle(session) {
  if (session.article_title) return session.article_title;
  if (session.current_state === 'FETCH') return 'Neue Lerneinheit';
  return `Session ${session.session_id.slice(0, 8)}`;
}

export default function Sidebar({ sessions, activeSessionId, onNewSession, onSelectSession, onDeleteSession }) {
  return (
    <aside className="hidden h-screen w-72 shrink-0 flex-col border-r border-gray-200 bg-gray-50 md:flex">
      <div className="flex h-16 items-center gap-3 px-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gray-900 text-white">
          <BookOpen size={18} />
        </div>
        <div>
          <div className="text-sm font-semibold text-gray-900">AI Learning Coach</div>
          <div className="text-xs text-gray-500">Wikipedia Tutor</div>
        </div>
      </div>

      <div className="px-3">
        <button
          onClick={onNewSession}
          className="flex w-full items-center gap-2 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-800 shadow-sm transition hover:bg-gray-100"
        >
          <MessageSquarePlus size={17} />
          Neue Lerneinheit
        </button>
      </div>

      <div className="mt-4 flex-1 overflow-y-auto px-3 pb-4">
        <div className="mb-2 px-2 text-xs font-medium uppercase tracking-wide text-gray-500">
          Sessions
        </div>

        <div className="space-y-1">
          {sessions.length === 0 && (
            <div className="px-2 py-3 text-sm text-gray-500">Noch keine Sessions.</div>
          )}

          {sessions.map((session) => {
            const isActive = session.session_id === activeSessionId;

            return (
              <div
                key={session.session_id}
                className={`group flex items-center gap-2 rounded-xl px-2 py-2 transition ${
                  isActive ? 'bg-gray-200' : 'hover:bg-gray-100'
                }`}
              >
                <button
                  onClick={() => onSelectSession(session.session_id)}
                  className="min-w-0 flex-1 text-left"
                >
                  <div className="truncate text-sm text-gray-900">{shortSessionTitle(session)}</div>
                  <div className="truncate text-xs text-gray-500">
                    {session.current_state}
                    {session.chunk_count ? ` · ${session.current_chunk_index + 1}/${session.chunk_count}` : ''}
                  </div>
                </button>

                <button
                  onClick={() => onDeleteSession(session.session_id)}
                  className="rounded-lg p-1 text-gray-400 opacity-0 transition hover:bg-gray-200 hover:text-gray-700 group-hover:opacity-100"
                  aria-label="Session löschen"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            );
          })}
        </div>
      </div>

      <div className="border-t border-gray-200 p-4 text-xs leading-relaxed text-gray-500">
        REST API: <span className="font-mono">localhost:8000</span>
        <br />
        Frontend: <span className="font-mono">localhost:5173</span>
      </div>
    </aside>
  );
}
