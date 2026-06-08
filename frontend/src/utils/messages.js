export function createMessage(role, content, extra = {}) {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    createdAt: new Date().toISOString(),
    ...extra,
  };
}

export function titleFromFirstUserMessage(messages) {
  const firstUserMessage = messages.find((message) => message.role === 'user');
  if (!firstUserMessage) return 'Neuer Lern-Chat';

  const compact = firstUserMessage.content.replace(/\s+/g, ' ').trim();
  if (!compact) return 'Neuer Lern-Chat';
  return compact.length > 34 ? `${compact.slice(0, 34)}...` : compact;
}
