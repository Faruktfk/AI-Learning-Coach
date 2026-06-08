import { Sparkles } from 'lucide-react';

export default function EmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center px-6 text-center">
      <div className="mb-5 rounded-3xl bg-zinc-100 p-5 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-100">
        <Sparkles size={34} />
      </div>
      <h2 className="mb-2 text-2xl font-semibold text-zinc-950 dark:text-white">
        Was möchtest du heute lernen?
      </h2>
      <p className="max-w-xl text-sm leading-6 text-zinc-600 dark:text-zinc-400">
        Gib ein Thema ein. Der Coach sucht einen passenden Wikipedia-Artikel, erklärt Abschnitt für Abschnitt
        und prüft dein Verständnis mit kurzen Multiple-Choice-Fragen.
      </p>
    </div>
  );
}
