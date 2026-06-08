import { GraduationCap } from 'lucide-react';

export default function EmptyState() {
  return (
    <div className="flex h-full items-center justify-center px-6 text-center">
      <div className="max-w-lg">
        <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gray-900 text-white">
          <GraduationCap size={28} />
        </div>
        <h1 className="text-2xl font-semibold tracking-tight text-gray-900">Was möchtest du heute lernen?</h1>
        <p className="mt-3 text-sm leading-6 text-gray-500">
          Gib ein Thema ein. Der Coach sucht den passenden Wikipedia-Artikel, erklärt Abschnitt für Abschnitt und fragt dich zwischendurch ab.
        </p>
        <div className="mt-6 grid gap-2 text-left text-sm text-gray-600 sm:grid-cols-3">
          <div className="rounded-2xl border border-gray-200 bg-white p-4">Schwarzes Loch</div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4">Photosynthese</div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4">Datenbanknormalisierung</div>
        </div>
      </div>
    </div>
  );
}
