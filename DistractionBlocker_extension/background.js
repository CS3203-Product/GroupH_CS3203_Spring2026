const DEFAULT_API_BASE = 'http://localhost:8000';

async function getApiBaseUrl() {
  const { apiBaseUrl } = await chrome.storage.local.get(['apiBaseUrl']);
  const raw = typeof apiBaseUrl === 'string' ? apiBaseUrl.trim() : '';
  return (raw || DEFAULT_API_BASE).replace(/\/$/, '');
}

async function getAccessToken() {
  const { accessToken } = await chrome.storage.local.get(['accessToken']);
  return typeof accessToken === 'string' && accessToken ? accessToken : null;
}

chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  if (details.frameId !== 0) return;

  const url = new URL(details.url);
  const hostname = url.hostname.replace(/^www\./, '');

  const token = await getAccessToken();
  if (!token) {
    console.warn(
      'Distraction Blocker: no session. Set API URL and sign in under extension options.',
    );
    return;
  }

  const apiBase = await getApiBaseUrl();

  try {
    const response = await fetch(`${apiBase}/blocker/check-url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ url: hostname }),
    });

    if (response.status === 401) {
      console.warn('Distraction Blocker: session invalid; sign in again in options.');
      await chrome.storage.local.remove(['accessToken', 'userId']);
      return;
    }

    if (!response.ok) {
      console.error('Blocker check failed:', response.status, await response.text());
      return;
    }

    const data = await response.json();

    if (data.blocked) {
      const siteParam = encodeURIComponent(hostname);
      chrome.tabs.update(details.tabId, {
        url: chrome.runtime.getURL(`blocked.html?site=${siteParam}`),
      });
    }
  } catch (err) {
    console.error('Blocker check failed:', err);
  }
});
