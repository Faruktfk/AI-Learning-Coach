import { useMemo, useState } from 'react';

export default function QuizPanel({ questions, disabled, onComplete }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});

  const currentQuestion = questions?.[currentIndex];
  const total = questions?.length || 0;
  const progressLabel = total > 0 ? `${currentIndex + 1} / ${total}` : '0 / 0';

  const chosenAnswerList = useMemo(() => {
    return Array.from({ length: total }, (_, index) => answers[index + 1] || null);
  }, [answers, total]);

  if (!currentQuestion) {
    return null;
  }

  function choose(optionId) {
    if (disabled) return;

    const nextAnswers = {
      ...answers,
      [currentQuestion.id]: optionId,
    };
    setAnswers(nextAnswers);

    if (currentIndex >= total - 1) {
      const finalAnswers = Array.from({ length: total }, (_, index) => nextAnswers[index + 1] || null);
      onComplete(finalAnswers);
      return;
    }

    setCurrentIndex((value) => value + 1);
  }

  return (
    <div className="border-t border-zinc-200 bg-white px-4 py-4 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="mx-auto max-w-3xl rounded-3xl border border-zinc-200 bg-zinc-50 p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
        <div className="mb-3 flex items-center justify-between text-xs text-zinc-500 dark:text-zinc-400">
          <span>Frage {progressLabel}</span>
          <span>{Object.keys(answers).length} beantwortet</span>
        </div>

        <div className="mb-4 h-2 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-800">
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
              disabled={disabled}
              onClick={() => choose(option.id)}
              className="rounded-2xl border border-zinc-300 bg-white px-4 py-3 text-left text-sm leading-6 text-zinc-900 transition hover:bg-zinc-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:bg-zinc-800"
            >
              <span className="mr-2 font-semibold">{option.id}.</span>
              {option.text}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
