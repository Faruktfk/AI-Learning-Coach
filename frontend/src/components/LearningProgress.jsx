import { BookOpen, Check, FileText, MessageCircle } from 'lucide-react';

function scrollToMessage(scrollContainerRef, messageId) {
  if (!messageId) return;

  const container = scrollContainerRef.current;
  const target = document.getElementById(`message-${messageId}`);

  if (!container || !target) return;

  const containerRect = container.getBoundingClientRect();
  const targetRect = target.getBoundingClientRect();

  const top = container.scrollTop + (targetRect.top - containerRect.top) - 24;

  container.scrollTo({
    top,
    behavior: 'smooth',
  });
}

function buildProgressSteps(conversation) {
  if (!conversation) return [];

  const messages = conversation.messages || [];
  const articleSections = conversation.articleSections || [];

  const promptMessage =
    messages.find((message) => message.progressType === 'prompt') ||
    messages.find((message) => message.role === 'user');

  const sectionSteps = articleSections.map((title, index) => {
    const sectionMessage = messages.find(
      (message) =>
        message.progressType === 'section' &&
        message.chunkIndex === index,
    );

    return {
      id: `section-${index}`,
      label: title,
      compactLabel: `${index + 1}`,
      type: 'section',
      anchorMessageId: sectionMessage?.id || null,
    };
  });

  const handoutMessage = messages.find(
    (message) => message.progressType === 'handout',
  );

  return [
    {
      id: 'prompt',
      label: 'Prompt',
      compactLabel: 'P',
      type: 'prompt',
      anchorMessageId: promptMessage?.id || null,
    },
    ...sectionSteps,
    {
      id: 'handout',
      label: 'Handout',
      compactLabel: 'H',
      type: 'handout',
      anchorMessageId: handoutMessage?.id || null,
    },
  ];
}

function StepIcon({ step, isDone }) {
  if (isDone) return <Check size={13} />;

  if (step.type === 'prompt') return <MessageCircle size={13} />;
  if (step.type === 'handout') return <FileText size={13} />;

  return <BookOpen size={13} />;
}

function stepButtonClass({ isClickable }) {
  if (isClickable) {
    return (
      'group flex w-full items-center gap-3 rounded-2xl px-2 py-2 text-left ' +
      'transition hover:bg-zinc-100 dark:hover:bg-zinc-900/80'
    );
  }

  return (
    'flex w-full cursor-default items-center gap-3 rounded-2xl px-2 py-2 ' +
    'text-left opacity-50'
  );
}

function circleClass({ isDone, isCurrent }) {
  const base =
    'relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full transition';

  if (isDone) {
    return `${base} bg-emerald-600 text-white shadow-sm shadow-emerald-900/10`;
  }

  if (isCurrent) {
    return (
      `${base} border border-emerald-500 bg-emerald-50 text-emerald-700 ` +
      'dark:bg-emerald-950/40 dark:text-emerald-300'
    );
  }

  return (
    `${base} border border-zinc-200 bg-white text-zinc-400 ` +
    'dark:border-zinc-800 dark:bg-black dark:text-zinc-600'
  );
}

function connectorClass({ isDone }) {
  if (isDone) {
    return 'absolute left-[25px] top-[46px] h-5 w-px rounded-full bg-emerald-600';
  }

  return 'absolute left-[25px] top-[46px] h-5 w-px rounded-full bg-zinc-200 dark:bg-zinc-800';
}

function handoutActionButtonClass() {
  return (
    'mt-3 w-full rounded-2xl px-3 py-2.5 text-xs font-bold text-white shadow-lg ' +
    'transition hover:scale-[1.02] active:scale-[0.98] ' +
    'bg-gradient-to-r from-emerald-500 via-cyan-500 to-violet-500 ' +
    'animate-[gradientShift_2.8s_ease_infinite]'
  );
}

function handoutDisabledButtonClass() {
  return (
    'mt-3 w-full rounded-2xl border border-zinc-200 px-3 py-2.5 text-xs font-semibold ' +
    'text-zinc-400 dark:border-zinc-800 dark:text-zinc-600'
  );
}

export default function LearningProgress({
  conversation,
  scrollContainerRef,
  canGenerateHandout,
  handoutDownloadUrl,
  handoutAlreadyGenerated,
  isFinished,
  onGenerateHandout,
}) {
  const steps = buildProgressSteps(conversation);

  if (!conversation || steps.length <= 1) {
    return null;
  }

  const firstPendingIndex = steps.findIndex((step) => !step.anchorMessageId);

  return (
    <aside className="pointer-events-none absolute right-3 top-16 bottom-28 z-20 w-56 overflow-hidden hidden lg:block">
      <div
        className="
          pointer-events-auto flex max-h-full flex-col rounded-3xl border
          border-zinc-200 bg-white/85 shadow-sm backdrop-blur-xl
          dark:border-zinc-900 dark:bg-black/75
        "
      >
        <div className="shrink-0 border-b border-zinc-100 px-4 py-3 dark:border-zinc-900">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-zinc-500 dark:text-zinc-500">
            Fortschritt
          </p>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-2 py-2">
          <div className="space-y-1">
            {steps.map((step, index) => {
              const isDone = Boolean(step.anchorMessageId);
              const isCurrent =
                !isDone &&
                (firstPendingIndex === index || firstPendingIndex === -1);

              const isClickable = Boolean(step.anchorMessageId);
              const hasNextStep = index < steps.length - 1;

              return (
                <div key={step.id} className="relative">
                  {hasNextStep ? <div className={connectorClass({ isDone })} /> : null}

                  <button
                    type="button"
                    disabled={!isClickable}
                    onClick={() =>
                      scrollToMessage(scrollContainerRef, step.anchorMessageId)
                    }
                    title={
                      isClickable
                        ? step.label
                        : `${step.label} noch nicht erreicht`
                    }
                    className={stepButtonClass({ isClickable })}
                  >
                    
                    <span className={circleClass({ isDone, isCurrent })}>
                      <StepIcon step={step} isDone={isDone} />
                    </span>

                    <span className="min-w-0 flex-1">
                      <span
                        className={
                          isDone
                            ? 'block truncate text-xs font-medium text-zinc-900 dark:text-zinc-100'
                            : isCurrent
                              ? 'block truncate text-xs font-medium text-emerald-700 dark:text-emerald-300'
                              : 'block truncate text-xs font-medium text-zinc-500 dark:text-zinc-500'
                        }
                      >
                        {step.label}
                      </span>

                      <span className="block text-[10px] text-zinc-400 dark:text-zinc-600">
                        {step.type === 'section'
                          ? `Abschnitt ${step.compactLabel}`
                          : step.type === 'prompt'
                            ? 'Start'
                            : 'Abschluss'}
                      </span>
                    </span>
                  </button>

                  {step.type === 'handout' ? (
                    <div className="ml-12 pr-2">
                      {!isFinished && !handoutAlreadyGenerated ? (
                        canGenerateHandout ? (
                          <button
                            type="button"
                            onClick={onGenerateHandout}
                            className={handoutActionButtonClass()}
                          >
                            Handout generieren
                          </button>
                        ) : (
                          <button
                            type="button"
                            disabled
                            className={handoutDisabledButtonClass()}
                            title="Während eines Tests oder während der Assistent arbeitet, kann kein Handout generiert werden."
                          >
                            Generieren nicht verfügbar
                          </button>
                        )
                      ) : null}

                      {handoutAlreadyGenerated && !isFinished ? (
                        <a
                          href={handoutDownloadUrl}
                          target="_blank"
                          rel="noreferrer"
                          download
                          className={`${handoutActionButtonClass()} inline-flex items-center justify-center`}
                        >
                          PDF herunterladen
                        </a>
                      ) : null}
                    </div>
                  ) : null}

                </div>
              );
            })}
          </div>
        </div>
      </div>
    </aside>
  );
}