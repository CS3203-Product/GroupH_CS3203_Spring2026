function normalizeApiBase(url) {
  return (url || '').trim().replace(/\/$/, '');
}

function getEffectiveApiBase(stored) {
  const override = normalizeApiBase(
    typeof stored.apiBaseUrl === 'string' ? stored.apiBaseUrl : '',
  );
  if (override) return override;

  const bases = self.DISTRACTION_BLOCKER_API_BASES;
  const key = stored.apiEnvironment === 'prod' ? 'prod' : 'dev';
  const preset = bases[key] || bases.dev;
  return normalizeApiBase(preset);
}

document.addEventListener('DOMContentLoaded', () => {
  const baseInput = document.getElementById('apiBaseUrl');
  const envRadios = document.querySelectorAll('input[name="apiEnv"]');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const statusEl = document.getElementById('status');
  const saveBaseBtn = document.getElementById('saveBase');
  const loginBtn = document.getElementById('login');
  const logoutBtn = document.getElementById('logout');

  function applyEnvironmentToRadios(apiEnvironment) {
    const prod = apiEnvironment === 'prod';
    envRadios.forEach((r) => {
      r.checked = (prod && r.value === 'prod') || (!prod && r.value === 'dev');
    });
  }

  chrome.storage.local.get(
    ['apiBaseUrl', 'apiEnvironment', 'userId', 'accessToken'],
    (stored) => {
      const env = stored.apiEnvironment === 'prod' ? 'prod' : 'dev';
      applyEnvironmentToRadios(env);
      baseInput.value = getEffectiveApiBase({ ...stored, apiEnvironment: env });
      if (stored.userId != null && stored.accessToken) {
        statusEl.textContent = `Signed in (user id ${stored.userId}).`;
      } else {
        statusEl.textContent = 'Not signed in.';
      }
    },
  );

  envRadios.forEach((radio) => {
    radio.addEventListener('change', () => {
      if (!radio.checked) return;
      const apiEnvironment = radio.value === 'prod' ? 'prod' : 'dev';
      chrome.storage.local.set({ apiEnvironment }, () => {
        chrome.storage.local.get(['apiBaseUrl', 'apiEnvironment'], (s) => {
          applyEnvironmentToRadios(apiEnvironment);
          baseInput.value = getEffectiveApiBase(s);
          statusEl.textContent = 'Environment saved.';
        });
      });
    });
  });

  saveBaseBtn.addEventListener('click', () => {
    const trimmed = normalizeApiBase(baseInput.value);
    if (!trimmed) {
      chrome.storage.local.remove('apiBaseUrl', () => {
        chrome.storage.local.get(['apiBaseUrl', 'apiEnvironment'], (s) => {
          baseInput.value = getEffectiveApiBase(s);
          statusEl.textContent = 'Using preset URL for the selected environment.';
        });
      });
      return;
    }
    chrome.storage.local.set({ apiBaseUrl: trimmed }, () => {
      baseInput.value = trimmed;
      statusEl.textContent = 'Custom API base URL saved (overrides environment preset).';
    });
  });

  loginBtn.addEventListener('click', async () => {
    chrome.storage.local.get(['apiBaseUrl', 'apiEnvironment'], async (stored) => {
      const base = getEffectiveApiBase(stored);
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
        const patch = { accessToken: data.access_token, userId: data.user_id };

        await new Promise((resolve, reject) => {
          chrome.storage.local.set(patch, () => {
            if (chrome.runtime.lastError) reject(chrome.runtime.lastError);
            else resolve();
          });
        });

        chrome.storage.local.get(['apiBaseUrl', 'apiEnvironment'], (after) => {
          baseInput.value = getEffectiveApiBase(after);
        });
        passwordInput.value = '';
        statusEl.textContent = `Signed in. User id ${data.user_id}; token stored in local extension storage.`;
      } catch (e) {
        statusEl.textContent = `Error: ${e.message || e}`;
      }
    });
  });

  logoutBtn.addEventListener('click', () => {
    chrome.storage.local.remove(['accessToken', 'userId'], () => {
      statusEl.textContent = 'Signed out.';
    });
  });
});
