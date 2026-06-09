import { useEffect, useMemo, useRef, useState } from 'react';

import { buildDownloadUrl, createLearningSession, stepLearningSession, generateLearningHandout } from './api/learningApi.js';
import ChatMessage from './components/ChatMessage.jsx';
import ChoiceButtons from './components/ChoiceButtons.jsx';
import Composer from './components/Composer.jsx';
import EmptyState from './components/EmptyState.jsx';
import Header from './components/Header.jsx';
import QuizPanel from './components/QuizPanel.jsx';
import Sidebar from './components/Sidebar.jsx';
import LearningProgress from './components/LearningProgress.jsx';
import { createMessage, titleFromFirstUserMessage } from './utils/messages.js';
import { loadConversations, loadSidebarCollapsed, loadTheme, saveConversations, saveSidebarCollapsed, saveTheme } from './utils/storage.js';

function createConversationFromSession(apiResponse) {
  return {
    id: crypto.randomUUID(),
    apiSessionId: apiResponse.session_id,
    title: 'Neuer Chat',
    messages: [createMessage('assistant', apiResponse.message, { stream: true })],
    inputKind: apiResponse.input_kind,
    pendingData: apiResponse.data || {},
    articleSections: [],
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
      articleSections: conversation.articleSections || [],
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
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => loadSidebarCollapsed());
  const [learningProgressOpen, setLearningProgressOpen] = useState(true);
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
    saveSidebarCollapsed(sidebarCollapsed);
  }, [sidebarCollapsed]);

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

  async function handleDeleteConversation(conversationId) {
    const remaining = conversations.filter(
      (conversation) => conversation.id !== conversationId,
    );

    if (remaining.length > 0) {
      setConversations(remaining);

      if (conversationId === activeConversationId) {
        setActiveConversationId(remaining[0].id);
      }

      return;
    }
    setConversations([]);
    setActiveConversationId(null);

    await handleNewConversation();
  }

function appendAssistantResponse(conversation, apiResponse) {
  const downloadUrl = buildDownloadUrl(apiResponse.download_url);

  const messageMeta = {};

  if (
    typeof apiResponse.data?.chunk_index === 'number' &&
    apiResponse.data?.chunk_title &&
    apiResponse.data?.summary
  ) {
    messageMeta.progressType = 'section';
    messageMeta.chunkIndex = apiResponse.data.chunk_index;
    messageMeta.chunkTitle = apiResponse.data.chunk_title;
  }

  if (apiResponse.state_after === 'FINISHED') {
    messageMeta.progressType = 'handout';
  }

  const assistantMessage = createMessage('assistant', apiResponse.message, {
    stream: true,
    downloadUrl,
    ...messageMeta,
  });

  const nextMessages = [...conversation.messages, assistantMessage];

  const resolvedTopicTitle = apiResponse.data?.resolved_topic?.trim();

  const articleSections = Array.isArray(apiResponse.data?.chunk_titles)
    ? apiResponse.data.chunk_titles
    : conversation.articleSections || [];

  return {
    ...conversation,
    messages: nextMessages,
    inputKind: apiResponse.input_kind,
    pendingData: apiResponse.data || {},
    articleSections,
    backendState: apiResponse.state_after,
    downloadUrl: downloadUrl || conversation.downloadUrl,
    handoutGenerated: Boolean(downloadUrl) || conversation.handoutGenerated,
    title: resolvedTopicTitle || conversation.title,
  };
}

  async function sendStep(conversationId, payload = {}, visibleUserMessage = null, isAutoStep = false) {
    const conversation = conversations.find((item) => item.id === conversationId);
    if (!conversation?.apiSessionId) return;

    if (visibleUserMessage) {
      updateConversation(conversationId, (current) => {
        const userMessageMeta = current.inputKind === 'topic' ? { progressType: 'prompt' } : {};
        const nextMessages = [...current.messages, createMessage('user', visibleUserMessage, userMessageMeta)];
        return {
            ...current,
            messages: nextMessages,
            title: current.title,
            isLoading: true,
            inputKind: null,
            pendingData: {},
          };
        }
      );
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

  async function handleGenerateHandout() {
    if (!activeConversation?.apiSessionId) return;

    const conversationId = activeConversation.id;

    const previousInputKind = activeConversation.inputKind;
    const previousPendingData = activeConversation.pendingData || {};

    updateConversation(conversationId, (current) => ({
      ...current,
      isLoading: true,
      inputKind: null,
    }));

    try {
      const apiResponse = await generateLearningHandout(activeConversation.apiSessionId);
      const downloadUrl = buildDownloadUrl(apiResponse.download_url);

      updateConversation(conversationId, (current) => {
        const assistantMessage = createMessage('assistant', apiResponse.message, {
          stream: true,
          downloadUrl,
          progressType: 'early_handout',
        });

        return {
          ...current,
          messages: [...current.messages, assistantMessage],
          isLoading: false,

          // Important:
          // The user should continue exactly where they were before.
          inputKind: previousInputKind,
          pendingData: previousPendingData,

          downloadUrl: downloadUrl || current.downloadUrl,
          handoutGenerated: Boolean(downloadUrl) || current.handoutGenerated,
        };
      });
    } catch (error) {
      updateConversation(conversationId, (current) => ({
        ...current,
        messages: [
          ...current.messages,
          createMessage('assistant', `Fehler beim Generieren des Handouts: ${error.message}`, {
            stream: true,
          }),
        ],
        isLoading: false,
        inputKind: previousInputKind,
        pendingData: previousPendingData,
      }));
    }
  }

  const inputKind = activeConversation?.inputKind;
  const isLoading = activeConversation?.isLoading || false;
  const quizQuestions = activeConversation?.pendingData?.questions || [];

  const isInQuiz = inputKind === 'quiz_answers';
  const handoutDownloadUrl = activeConversation?.downloadUrl || null;
  const handoutAlreadyGenerated = Boolean(handoutDownloadUrl);

  const hasLoadedArticle =
    Array.isArray(activeConversation?.articleSections) &&
    activeConversation.articleSections.length > 0;

  const isFinished = activeConversation?.backendState === 'FINISHED';

  const canGenerateHandout =
    hasLoadedArticle &&
    !isFinished &&
    !handoutAlreadyGenerated &&
    !isLoading &&
    !isInQuiz;

  return (
    <div className="flex h-screen overflow-hidden bg-white text-zinc-950 dark:bg-black dark:text-zinc-100">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        collapsed={sidebarCollapsed}
        theme={theme}
        onToggleCollapsed={() => setSidebarCollapsed((current) => !current)}
        onToggleTheme={() => setTheme((current) => (current === 'dark' ? 'light' : 'dark'))}
        onCreateConversation={handleNewConversation}
        onSelectConversation={handleSelectConversation}
        onDeleteConversation={handleDeleteConversation}
      />

      <main className="relative flex min-w-0 flex-1 flex-col overflow-hidden">
        <Header
          activeConversation={activeConversation}
          onNewConversation={handleNewConversation}
          learningProgressOpen={learningProgressOpen}
          onToggleLearningProgress={() =>
            setLearningProgressOpen((current) => !current)
          }
        />

        <section ref={scrollRef} className="scrollbar-thin min-h-0 flex-1 overflow-y-auto bg-white dark:bg-black">
          {!activeConversation || activeConversation.messages.length === 0 ? (
            <EmptyState />
          ) : (
            <>
              {activeConversation.messages.map((message) => (
                <div key={message.id} id={`message-${message.id}`}>
                 <ChatMessage
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
                </div>
              ))}
              {isLoading ? <ThinkingIndicator /> : null}
            </>
          )}
        </section>
       
        {learningProgressOpen ? (
          <LearningProgress
            conversation={activeConversation}
            scrollContainerRef={scrollRef}
            canGenerateHandout={canGenerateHandout}
            handoutDownloadUrl={handoutDownloadUrl}
            handoutAlreadyGenerated={handoutAlreadyGenerated}
            isFinished={isFinished}
            onGenerateHandout={handleGenerateHandout}
          />
        ) : null}

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
