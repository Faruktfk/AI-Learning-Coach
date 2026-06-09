import { useEffect, useMemo, useState } from 'react';

function optionButtonClass({ optionId, selectedOptionId, correctOptionId, showResult }) {
  const base =
    'rounded-2xl border px-4 py-3 text-left text-sm leading-6 transition disabled:cursor-not-allowed';

  if (!showResult) {
    return `${base} border-zinc-300 bg-white text-zinc-900 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-[#101010] dark:text-zinc-100 dark:hover:bg-zinc-900`;
  }

  if (optionId === correctOptionId) {
    return `${base} border-emerald-500 bg-emerald-50 text-emerald-950 dark:border-emerald-500 dark:bg-emerald-950/40 dark:text-emerald-100`;
  }

  if (optionId === selectedOptionId && selectedOptionId !== correctOptionId) {
    return `${base} border-red-500 bg-red-50 text-red-950 dark:border-red-500 dark:bg-red-950/40 dark:text-red-100`;
  }

  return `${base} border-zinc-200 bg-zinc-50 text-zinc-500 opacity-70 dark:border-zinc-900 dark:bg-[#080808] dark:text-zinc-500`;
}

export default function QuizPanel({ questions, disabled, onComplete }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [selectedOptionId, setSelectedOptionId] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [wrongCount, setWrongCount] = useState(0);

  const questionSignature = useMemo(() => {
    return (questions || []).map((question) => `${question.id}:${question.question}`).join('|');
  }, [questions]);

  useEffect(() => {
    setCurrentIndex(0);
    setAnswers({});
    setSelectedOptionId(null);
    setShowResult(false);
    setWrongCount(0);
  }, [questionSignature]);

  const currentQuestion = questions?.[currentIndex];
  const total = questions?.length || 0;
  const progressLabel = total > 0 ? `${currentIndex + 1} / ${total}` : '0 / 0';

  if (!currentQuestion) {
    return null;
  }

  const correctOptionId = currentQuestion.correct_option_id;
  const hasSelected = selectedOptionId !== null;
  const isSelectedCorrect = selectedOptionId === correctOptionId;
  const isLastQuestion = currentIndex >= total - 1;

  function choose(optionId) {
    if (disabled || showResult) return;

    const nextAnswers = {
      ...answers,
      [currentQuestion.id]: optionId,
    };

    setAnswers(nextAnswers);
    setSelectedOptionId(optionId);
    setShowResult(true);

    if (optionId !== correctOptionId) {
      setWrongCount((current) => current + 1);
    }
  }

  function goNext() {
    if (!hasSelected) return;

    if (isLastQuestion) {
      const finalAnswers = questions.map((question) => answers[question.id] ?? null);
      onComplete(finalAnswers);
      return;
    }

    setCurrentIndex((value) => value + 1);
    setSelectedOptionId(null);
    setShowResult(false);
  }

  return (
    <div className="border-t border-zinc-200 bg-white px-4 py-4 dark:border-zinc-800 dark:bg-black">
      <div className="mx-auto max-w-3xl rounded-3xl border border-zinc-200 bg-zinc-50 p-4 shadow-sm dark:border-zinc-800 dark:bg-[#050505]">
        <div className="mb-3 flex items-center justify-between text-xs text-zinc-500 dark:text-zinc-400">
          <span>Frage {progressLabel}</span>
          <span>
            Falsch: {wrongCount} / {total}
          </span>
        </div>

        <div className="mb-4 h-2 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-900">
          <div
            className="h-full rounded-full bg-emerald-600 transition-all"
            style={{ width: `${((currentIndex + 1) / total) * 100}%` }}
          />
        </div>

        <h3 className="mb-4 text-base font-semibold leading-7 text-zinc-950 dark:text-white">
          {currentQuestion.question}
        </h3>

        <div className="grid gap-2">
          {currentQuestion.options.map((option) => (
            <button
              key={option.id}
              disabled={disabled || showResult}
              onClick={() => choose(option.id)}
              className={optionButtonClass({
                optionId: option.id,
                selectedOptionId,
                correctOptionId,
                showResult,
              })}
            >
              <span className="mr-2 font-semibold">{option.id}.</span>
              {option.text}
            </button>
          ))}
        </div>

        {showResult ? (
          <div className="mt-4 flex items-center justify-between gap-3">
            <p
              className={
                isSelectedCorrect
                  ? 'text-sm font-medium text-emerald-700 dark:text-emerald-300'
                  : 'text-sm font-medium text-red-700 dark:text-red-300'
              }
            >
              {isSelectedCorrect
                ? 'Richtig beantwortet.'
                : 'Falsch beantwortet. Die richtige Antwort ist grün markiert.'}
            </p>

            <button
              onClick={goNext}
              disabled={disabled}
              className="rounded-xl bg-zinc-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-black dark:hover:bg-zinc-200"
            >
              {isLastQuestion ? 'Test abschließen' : 'Next'}
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
}