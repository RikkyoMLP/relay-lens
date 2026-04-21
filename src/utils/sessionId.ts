/**
 * Browser-local session ID for per-user file isolation.
 * Stored in localStorage so it survives tab close / browser restart.
 */

const SESSION_KEY = "relay-lens-session-id";

export function getSessionId(): string {
  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}
