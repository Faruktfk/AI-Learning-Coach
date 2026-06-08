import { useEffect, useMemo, useRef, useState } from 'react';

import { buildDownloadUrl, createLearningSession, stepLearningSession } from './api/learningApi.js';
import ChatMessage from './components/ChatMessage.jsx';
import ChoiceButtons from './components/ChoiceButtons.jsx';
import Composer from './components/Composer.jsx';
import EmptyState from './components/EmptyState.jsx';
import Header from './components/Header.jsx';
import QuizPanel from './components/QuizPanel.jsx';
import Sidebar from './components/Sidebar.jsx';
import { createMessage, titleFromFirstUserMessage } from './utils/messages.js';
import { loadConversations, loadTheme, saveConversations, saveTheme } from './utils/storage.js';

function createConversationFromSession(apiResponse) {
  return {
    id: crypto.randomUUID(),
    apiSessionId: apiResponse.session_id,
    title: 'Neuer Lern-Chat',
    messages: [createMessage('assistant', apiResponse.message, { stream: true })],
    inputKind: apiResponse.input_kind,
    pendingData: apiResponse.data || {},
    backendState: apiResponse.state_after,
    downloadUrl: buildDownloadUrl(apiResponse.download_url),
    isLoading: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
}

function ThinkingIndicator() {
  return (
    <div className="mx-auto flex w-full max-w-3xl gap-4 px-4 py-5">
      <div className="h-8 w-8 rounded-full bg-emerald-600" />
      <div className="mt-2 flex gap-1">
        <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.2s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.1s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400" />
      </div>
    </div>
  );
}

export default function App() {
  const [conversations, setConversations] = useState(() =>
    loadConversations().map((conversation) => ({
      ...conversation,
      messages: conversation.messages.map((message) => ({
        ...message,
        stream: false,
      })),
    })),
  );
  
  const [activeConversationId, setActiveConversationId] = useState(() => {
    const loaded = loadConversations();
    return loaded[0]?.id || null;
  });

  const [theme, setTheme] = useState(() => loadTheme());
  const scrollRef = useRef(null);

  const activeConversation = useMemo(
    () => conversations.find((conversation) => conversation.id === activeConversationId) || null,
    [conversations, activeConversationId],
  );

  useEffect(() => {
    saveConversations(conversations);
  }, [conversations]);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    saveTheme(theme);
  }, [theme]);

  useEffect(() => {
    if (conversations.length === 0) {
      handleNewConversation();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [activeConversation?.messages?.length, activeConversation?.isLoading]);

  function updateConversation(conversationId, updater) {
    setConversations((current) =>
      current.map((conversation) => {
        if (conversation.id !== conversationId) return conversation;

        const updated = updater(conversation);
        return {
          ...updated,
          updatedAt: new Date().toISOString(),
        };
      }),
    );
  }

  async function handleNewConversation() {
    try {
      const apiResponse = await createLearningSession();
      const newConversation = createConversationFromSession(apiResponse);
      setConversations((current) => [newConversation, ...current]);
      setActiveConversationId(newConversation.id);
    } catch (error) {
      const offlineConversation = {
        id: crypto.randomUUID(),
        apiSessionId: null,
        title: 'Backend nicht erreichbar',
        messages: [
          createMessage(
            'assistant',
            `Backend konnte nicht erreicht werden. Starte FastAPI mit: uvicorn api:app --reload\n\nFehler: ${error.message}`,
            { stream: true },
          ),
        ],
        inputKind: null,
        pendingData: {},
        backendState: null,
        isLoading: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      setConversations((current) => [offlineConversation, ...current]);
      setActiveConversationId(offlineConversation.id);
    }
  }

  function handleSelectConversation(conversationId) {
    setConversations((current) =>
      current.map((conversation) => {
        if (conversation.id !== conversationId) return conversation;

        return {
          ...conversation,
          messages: conversation.messages.map((message) => ({
            ...message,
            stream: false,
          })),
        };
      }),
    );

    setActiveConversationId(conversationId);
  }

  function handleDeleteConversation(conversationId) {
    setConversations((current) => {
      const remaining = current.filter((conversation) => conversation.id !== conversationId);

      if (conversationId === activeConversationId) {
        setActiveConversationId(remaining[0]?.id || null);
      }

      return remaining;
    });
  }

  function appendAssistantResponse(conversation, apiResponse) {
    const downloadUrl = buildDownloadUrl(apiResponse.download_url);
    const assistantMessage = createMessage('assistant', apiResponse.message, {
      stream: true,
      downloadUrl,
    });

    const nextMessages = [...conversation.messages, assistantMessage];

    return {
      ...conversation,
      messages: nextMessages,
      inputKind: apiResponse.input_kind,
      pendingData: apiResponse.data || {},
      backendState: apiResponse.state_after,
      downloadUrl,
      title: titleFromFirstUserMessage(nextMessages),
    };
  }

  async function sendStep(conversationId, payload = {}, visibleUserMessage = null, isAutoStep = false) {
    const conversation = conversations.find((item) => item.id === conversationId);
    if (!conversation?.apiSessionId) return;

    if (visibleUserMessage) {
      updateConversation(conversationId, (current) => {
        const nextMessages = [...current.messages, createMessage('user', visibleUserMessage)];
        return {
          ...current,
          messages: nextMessages,
          title: titleFromFirstUserMessage(nextMessages),
          isLoading: true,
          inputKind: null,
          pendingData: {},
        };
      });
    } else {
      updateConversation(conversationId, (current) => ({
        ...current,
        isLoading: true,
        inputKind: null,
      }));
    }

    try {
      const apiResponse = await stepLearningSession(conversation.apiSessionId, payload);

      updateConversation(conversationId, (current) => ({
        ...appendAssistantResponse(current, apiResponse),
        isLoading: !apiResponse.requires_input && apiResponse.state_after !== 'FINISHED',
      }));

      if (!apiResponse.requires_input && apiResponse.state_after !== 'FINISHED') {
        window.setTimeout(() => {
          sendStep(conversationId, {}, null, true);
        }, isAutoStep ? 250 : 500);
      }
    } catch (error) {
      updateConversation(conversationId, (current) => ({
        ...current,
        messages: [
          ...current.messages,
          createMessage('assistant', `Fehler: ${error.message}`, { stream: true }),
        ],
        isLoading: false,
        inputKind: current.inputKind || 'topic',
      }));
    }
  }

  function handleSubmitText(text) {
    if (!activeConversation) return;
    sendStep(activeConversation.id, { message: text }, text);
  }

  function handleChoice(value) {
    if (!activeConversation) return;
    const label = value === 'ja' ? 'Ja' : value === 'nein' ? 'Nein' : value === 'nochmal' ? 'Nochmal' : 'Skip';
    sendStep(activeConversation.id, { message: value }, label);
  }

  function handleQuizComplete(answers) {
    if (!activeConversation) return;
    const visibleAnswer = `Antworten: ${answers.map((answer) => answer ?? '-').join(', ')}`;
    sendStep(activeConversation.id, { answers }, visibleAnswer);
  }

  const inputKind = activeConversation?.inputKind;
  const isLoading = activeConversation?.isLoading || false;
  const quizQuestions = activeConversation?.pendingData?.questions || [];

  return (
    <div className="flex h-full bg-white text-zinc-950 dark:bg-zinc-900 dark:text-zinc-100">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onNewConversation={handleNewConversation}
        onSelectConversation={handleSelectConversation}
        onDeleteConversation={handleDeleteConversation}
      />

      <main className="flex min-w-0 flex-1 flex-col">
        <Header
          activeConversation={activeConversation}
          theme={theme}
          onToggleTheme={() => setTheme((current) => (current === 'dark' ? 'light' : 'dark'))}
          onNewConversation={handleNewConversation}
        />

        <section ref={scrollRef} className="scrollbar-thin min-h-0 flex-1 overflow-y-auto bg-white dark:bg-zinc-900">
          {!activeConversation || activeConversation.messages.length === 0 ? (
            <EmptyState />
          ) : (
            <>
              {activeConversation.messages.map((message) => (
                 <ChatMessage
                    key={message.id}
                    message={message}
                    onAnimationDone={() => {
                      updateConversation(activeConversation.id, (current) => ({
                        ...current,
                        messages: current.messages.map((item) =>
                          item.id === message.id ? { ...item, stream: false } : item,
                        ),
                      }));
                    }}
                  />
              ))}
              {isLoading ? <ThinkingIndicator /> : null}
            </>
          )}
        </section>

        {inputKind === 'topic' ? (
          <Composer
            disabled={isLoading}
            placeholder="Thema eingeben, z.B. Schwarzes Loch..."
            onSubmit={handleSubmitText}
          />
        ) : null}

        {inputKind === 'start_test_decision' || inputKind === 'adapt_decision' ? (
          <ChoiceButtons kind={inputKind} disabled={isLoading} onChoose={handleChoice} />
        ) : null}

        {inputKind === 'quiz_answers' ? (
          <QuizPanel questions={quizQuestions} disabled={isLoading} onComplete={handleQuizComplete} />
        ) : null}
      </main>
    </div>
  );
}
