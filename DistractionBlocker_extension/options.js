const DEFAULT_API_BASE = 'http://localhost:8000';

function normalizeBase(url) {
  const t = (url || '').trim();
  return (t || DEFAULT_API_BASE).replace(/\/$/, '');
}

document.addEventListener('DOMContentLoaded', () => {
  const baseInput = document.getElementById('apiBaseUrl');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const statusEl = document.getElementById('status');
  const saveBaseBtn = document.getElementById('saveBase');
  const loginBtn = document.getElementById('login');
  const logoutBtn = document.getElementById('logout');

  chrome.storage.local.get(['apiBaseUrl', 'userId', 'accessToken'], (stored) => {
    if (stored.apiBaseUrl) baseInput.value = stored.apiBaseUrl;
    if (stored.userId != null && stored.accessToken) {
      statusEl.textContent = `Signed in (user id ${stored.userId}).`;
    } else {
      statusEl.textContent = 'Not signed in.';
    }
  });

  saveBaseBtn.addEventListener('click', () => {
    const base = normalizeBase(baseInput.value);
    chrome.storage.local.set({ apiBaseUrl: base }, () => {
      baseInput.value = base;
      statusEl.textContent = 'API base URL saved.';
    });
  });

  loginBtn.addEventListener('click', async () => {
    const base = normalizeBase(baseInput.value);
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!email || !password) {
      statusEl.textContent = 'Enter email and password.';
      return;
    }

    statusEl.textContent = 'Signing in…';

    try {
      const res = await fetch(`${base}/blocker/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const text = await res.text();
      if (!res.ok) {
        statusEl.textContent = `Login failed (${res.status}): ${text}`;
        return;
      }

      const data = JSON.parse(text);
      await new Promise((resolve, reject) => {
        chrome.storage.local.set(
          {
            apiBaseUrl: base,
            accessToken: data.access_token,
            userId: data.user_id,
          },
          () => {
            if (chrome.runtime.lastError) reject(chrome.runtime.lastError);
            else resolve();
          },
        );
      });

      baseInput.value = base;
      passwordInput.value = '';
      statusEl.textContent = `Signed in. User id ${data.user_id}; token stored in local extension storage.`;
    } catch (e) {
      statusEl.textContent = `Error: ${e.message || e}`;
    }
  });

  logoutBtn.addEventListener('click', () => {
    chrome.storage.local.remove(['accessToken', 'userId'], () => {
      statusEl.textContent = 'Signed out.';
    });
  });
});
