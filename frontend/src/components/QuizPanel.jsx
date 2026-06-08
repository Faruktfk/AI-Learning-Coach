import { useMemo, useState } from 'react';

export default function QuizPanel({ questions, disabled, onSubmitAnswers }) {
  const [answers, setAnswers] = useState({});

  const allAnswered = useMemo(() => {
    if (!questions?.length) return false;
    return questions.every((question) => answers[question.id]);
  }, [answers, questions]);

  if (!questions?.length) return null;

  function choose(questionId, optionId) {
    if (disabled) return;
    setAnswers((current) => ({ ...current, [questionId]: optionId }));
  }

  function submit() {
    if (!allAnswered || disabled) return;
    const orderedAnswers = questions.map((question) => answers[question.id]);
    onSubmitAnswers(orderedAnswers);
    setAnswers({});
  }

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-4">
      <div className="mx-auto max-w-3xl space-y-4">
        <div className="rounded-3xl border border-gray-200 bg-gray-50 p-4 shadow-sm">
          <div className="mb-4 text-sm font-semibold text-gray-900">Wähle pro Frage eine Antwort aus.</div>

          <div className="space-y-5">
            {questions.map((question) => (
              <div key={question.id} className="rounded-2xl border border-gray-200 bg-white p-4">
                <div className="mb-3 text-sm font-semibold text-gray-900">
                  {question.id}. {question.question}
                </div>

                <div className="grid gap-2 sm:grid-cols-2">
                  {question.options.map((option) => {
                    const selected = answers[question.id] === option.id;

                    return (
                      <button
                        key={option.id}
                        onClick={() => choose(question.id, option.id)}
                        disabled={disabled}
                        className={`rounded-xl border px-3 py-2 text-left text-sm transition ${
                          selected
                            ? 'border-gray-900 bg-gray-900 text-white'
                            : 'border-gray-200 bg-white text-gray-800 hover:bg-gray-100'
                        } disabled:cursor-not-allowed disabled:opacity-60`}
                      >
                        <span className="mr-2 font-semibold">{option.id}.</span>
                        {option.text}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 flex justify-end">
            <button
              onClick={submit}
              disabled={!allAnswered || disabled}
              className="rounded-2xl bg-gray-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:bg-gray-300"
            >
              Antworten absenden
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
