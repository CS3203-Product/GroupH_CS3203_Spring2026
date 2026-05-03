chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {

// Checks the main address bar and disregards ads, embedded videos
  if (details.frameId !== 0) return;

// URL string converts to URL object for extracting domain name
  const url = new URL(details.url);

// Cleans domain: e.g.,  “://youtube.com” becomes “youtube.com”
  const hostname = url.hostname.replace('www.', '');

  try {

// Send POST request to FASTAPI backend hosted on Render. The fetch sends the current domain to a remote FASTAPI endpoint to check if the site is restricted based on user focus settings. Centralizes blocking logic for the backend so the extension makes real time decisions using records from Supabase. 
    const response = await fetch('https://grouph-cs3203-spring2026-h2lk.onrender.com/blocker/check-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
url: hostname, 
user_id: '123'
 })
    });

    const data = await response.json();

// If FASTAPI indicates site is blocked, redirect the user to “blocked.html” page 
    if (data.blocked) {
      chrome.tabs.update(details.tabId, { url: chrome.runtime.getURL(`blocked.html?site=${hostname}`) 
});
    }
  } catch (err) {

// Log errors to extension console ( e.g., if FASTAPI server is offline)
    console.error('Blocker check failed:', err);
  }
});
