import { GraduationCap } from 'lucide-react';

export default function EmptyState() {
  return (
    <div className="flex h-full items-center justify-center px-4 text-center">
      <div className="max-w-md">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-600 text-white">
          <GraduationCap size={24} />
        </div>
        <h2 className="mb-2 text-xl font-semibold text-zinc-950 dark:text-white">MyWikiGPT</h2>
        <p className="text-sm leading-6 text-zinc-600 dark:text-zinc-400">
          Starte einen Chat und gib ein Thema ein. Der Coach erklärt Wikipedia-Abschnitte, prüft dein Verständnis und erstellt am Ende ein Handout.
        </p>
      </div>
    </div>
  );
}
