const STORAGE_KEY = 'ai-learning-coach.conversations.v1';
const THEME_KEY = 'ai-learning-coach.theme.v1';
const SIDEBAR_COLLAPSED_KEY = 'ai-learning-coach-sidebar-collapsed';

export function loadConversations() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveConversations(conversations) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
}

export function loadTheme() {
  return localStorage.getItem(THEME_KEY) || 'dark';
}

export function saveTheme(theme) {
  localStorage.setItem(THEME_KEY, theme);
}

export function loadSidebarCollapsed() {
  try {
    const value = localStorage.getItem(SIDEBAR_COLLAPSED_KEY);
    return value === 'true';
  } catch {
    return false;
  }
}

export function saveSidebarCollapsed(collapsed) {
  try {
    localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(collapsed));
  } catch {
    // Ignore localStorage errors
  }
}