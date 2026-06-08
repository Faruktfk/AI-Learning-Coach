import { Bot, User } from 'lucide-react';

function renderText(text) {
  if (!text) return null;

  return text.split('\n').map((line, index) => (
    <span key={index}>
      {line}
      {index < text.split('\n').length - 1 && <br />}
    </span>
  ));
}

export default function ChatMessage({ message }) {
  const isAssistant = message.role === 'assistant';

  return (
    <div className={`flex w-full gap-4 px-4 py-6 ${isAssistant ? 'bg-white' : 'bg-gray-50'}`}>
      <div className="mx-auto flex w-full max-w-3xl gap-4">
        <div
          className={`mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
            isAssistant ? 'bg-gray-900 text-white' : 'bg-gray-200 text-gray-700'
          }`}
        >
          {isAssistant ? <Bot size={17} /> : <User size={17} />}
        </div>

        <div className="min-w-0 flex-1">
          {message.title && (
            <div className="mb-2 text-sm font-semibold text-gray-900">{message.title}</div>
          )}
          <div className="whitespace-pre-wrap text-[15px] leading-7 text-gray-900">
            {renderText(message.content)}
          </div>

          {message.meta?.results && (
            <div className="mt-4 space-y-2 rounded-2xl border border-gray-200 bg-gray-50 p-4">
              {message.meta.results.map((result) => (
                <div key={result.id} className="text-sm">
                  <div className="font-medium text-gray-900">
                    {result.answered_correctly ? '✅' : '❌'} {result.id}. {result.question}
                  </div>
                  <div className="mt-1 text-gray-600">Deine Antwort: {result.selected_option || '—'}</div>
                  {!result.answered_correctly && (
                    <div className="text-gray-600">Richtig: {result.correct_option}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
