export function shouldAutoContinue(response) {
  if (!response) return false;
  if (response.requires_input) return false;
  if (response.session?.done) return false;

  // The API is stateful. After a non-input response, the next state can usually
  // be executed immediately until the API asks for user input.
  const nextState = response.state_after || response.session?.current_state;
  return ['TEACH', 'CHECK', 'ADAPT', 'HANDOUT'].includes(nextState);
}

export function getInputMode(response) {
  if (!response?.requires_input) return { type: 'none' };

  switch (response.input_kind) {
    case 'topic':
      return {
        type: 'text',
        placeholder: 'Welches Thema möchtest du lernen?',
      };

    case 'start_test_decision':
      return {
        type: 'buttons',
        options: [
          { label: 'Ja, Test starten', value: 'ja' },
          { label: 'Nein, überspringen', value: 'nein' },
        ],
      };

    case 'adapt_decision':
      return {
        type: 'buttons',
        options: [
          { label: 'Nochmal versuchen', value: 'nochmal' },
          { label: 'Skip', value: 'skip' },
        ],
      };

    case 'quiz_answers':
      return {
        type: 'quiz',
      };

    default:
      return {
        type: 'text',
        placeholder: 'Nachricht eingeben...',
      };
  }
}

export function extractAssistantTitle(response) {
  const data = response?.data || {};

  if (data.chunk_title) {
    return data.chunk_title;
  }

  if (data.article_title) {
    return data.article_title;
  }

  return null;
}
