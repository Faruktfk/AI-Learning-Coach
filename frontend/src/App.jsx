import { useCallback, useEffect, useRef, useState } from 'react';
import { createSession, deleteSession, listSessions, stepSession } from './api/learningApi.js';
import ChatMessage from './components/ChatMessage.jsx';
import ChoiceButtons from './components/ChoiceButtons.jsx';
import Composer from './components/Composer.jsx';
import EmptyState from './components/EmptyState.jsx';
import Header from './components/Header.jsx';
import QuizPanel from './components/QuizPanel.jsx';
import Sidebar from './components/Sidebar.jsx';
import { extractAssistantTitle, getInputMode, shouldAutoContinue } from './utils/responseHelpers.js';

function createAssistantMessage(response) {
  return {
    id: crypto.randomUUID(),
    role: 'assistant',
    title: extractAssistantTitle(response),
    content: response.message || '',
    meta: response.data || {},
  };
}

function createUserMessage(content) {
  return {
    id: crypto.randomUUID(),
    role: 'user',
    content,
  };
}

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [lastResponse, setLastResponse] = useState(null);
  const [isBusy, setIsBusy] = useState(false);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);
  const autoContinueLockRef = useRef(false);

  const inputMode = getInputMode(lastResponse);
  const quizQuestions = lastResponse?.input_kind === 'quiz_answers' ? lastResponse?.data?.questions || [] : [];

  const refreshSessions = useCallback(async () => {
    const data = await listSessions();
    setSessions(data.sessions || []);
  }, []);

  const appendAssistantResponse = useCallback((response) => {
    setMessages((current) => [...current, createAssistantMessage(response)]);
    setLastResponse(response);
    setActiveSession(response.session);
  }, []);

  const executeStep = useCallback(
    async (payload = {}, options = {}) => {
      if (!activeSessionId) return null;

      const { showUserMessage } = options;
      setError(null);
      setIsBusy(true);

      if (showUserMessage) {
        setMessages((current) => [...current, createUserMessage(showUserMessage)]);
      }

      try {
        const response = await stepSession(activeSessionId, payload);
        appendAssistantResponse(response);
        await refreshSessions();
        return response;
      } catch (err) {
        setError(err.message || 'Unbekannter Fehler');
        return null;
      } finally {
        setIsBusy(false);
      }
    },
    [activeSessionId, appendAssistantResponse, refreshSessions]
  );

  const startNewSession = useCallback(async () => {
    setError(null);
    setIsBusy(true);
    autoContinueLockRef.current = false;

    try {
      const created = await createSession();
      setActiveSessionId(created.session_id);
      setActiveSession(created.session);
      setMessages([]);
      setLastResponse(null);
      await refreshSessions();

      const firstResponse = await stepSession(created.session_id, {});
      appendAssistantResponse(firstResponse);
      await refreshSessions();
    } catch (err) {
      setError(err.message || 'Session konnte nicht erstellt werden');
    } finally {
      setIsBusy(false);
    }
  }, [appendAssistantResponse, refreshSessions]);

  useEffect(() => {
    startNewSession();
  }, [startNewSession]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isBusy]);

  useEffect(() => {
    if (!lastResponse || !activeSessionId) return;
    if (!shouldAutoContinue(lastResponse)) return;
    if (autoContinueLockRef.current) return;

    autoContinueLockRef.current = true;

    const timerId = window.setTimeout(async () => {
      await executeStep({});
      autoContinueLockRef.current = false;
    }, 350);

    return () => {
      window.clearTimeout(timerId);
      autoContinueLockRef.current = false;
    };
  }, [lastResponse, activeSessionId, executeStep]);

  async function handleSubmitText(text) {
    await executeStep({ message: text }, { showUserMessage: text });
  }

  async function handleChoose(value, label) {
    await executeStep({ message: value }, { showUserMessage: label });
  }

  async function handleSubmitAnswers(answers) {
    const humanReadable = answers.map((answer, index) => `${index + 1}. ${answer}`).join('\n');
    await executeStep({ answers }, { showUserMessage: humanReadable });
  }

  async function handleSelectSession(sessionId) {
    // The API stores session state, but not chat history. For this MVP frontend,
    // selecting a session restores the state snapshot and asks the API for the next expected action.
    setActiveSessionId(sessionId);
    setMessages([]);
    setLastResponse(null);
    setError(null);
    setIsBusy(true);

    try {
      const response = await stepSession(sessionId, {});
      appendAssistantResponse(response);
      await refreshSessions();
    } catch (err) {
      setError(err.message || 'Session konnte nicht geladen werden');
    } finally {
      setIsBusy(false);
    }
  }

  async function handleDeleteSession(sessionId) {
    await deleteSession(sessionId);
    await refreshSessions();

    if (sessionId === activeSessionId) {
      await startNewSession();
    }
  }

  const showEmptyState = messages.length === 0 && !isBusy;

  return (
    <div className="flex h-screen overflow-hidden bg-white text-gray-900">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onNewSession={startNewSession}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
      />

      <main className="flex min-w-0 flex-1 flex-col">
        <Header session={activeSession} isBusy={isBusy} onNewSession={startNewSession} />

        <section className="min-h-0 flex-1 overflow-y-auto bg-white">
          {showEmptyState ? (
            <EmptyState />
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}

              {isBusy && (
                <div className="flex w-full gap-4 bg-white px-4 py-6">
                  <div className="mx-auto flex w-full max-w-3xl gap-4">
                    <div className="mt-1 h-8 w-8 shrink-0 rounded-full bg-gray-900" />
                    <div className="flex items-center gap-1 pt-2 text-gray-500">
                      <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.2s]" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.1s]" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
                    </div>
                  </div>
                </div>
              )}

              {error && (
                <div className="mx-auto max-w-3xl px-4 py-4">
                  <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                    {error}
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </section>

        <ChoiceButtons mode={inputMode} disabled={isBusy} onChoose={handleChoose} />
        <QuizPanel questions={quizQuestions} disabled={isBusy} onSubmitAnswers={handleSubmitAnswers} />
        <Composer mode={inputMode} disabled={isBusy} onSubmitText={handleSubmitText} />
      </main>
    </div>
  );
}
