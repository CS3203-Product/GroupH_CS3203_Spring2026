
// Triggers when user navigates to another website
chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  
  // Checks the main address bar and disregards ads, embedded videos
  if (details.frameId !== 0) return;

  // URL string converts to URL object for extracting domain name
  const url = new URL(details.url);
  
  // Cleans domain: e.g., "://youtube.com" becomes "youtube.com"
  const hostname = url.hostname.replace('www.', '');

  // Ignores internal extension pages to prevent a nonstop indirect loop
  if (url.protocol === 'chrome-extension:') return;

  try {

    // Send the domain to your FASTAPI to check if domain is blocked
    const response = await fetch('http://localhost:8000/blocker/check-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        url: hostname, 
        user_id: '123' 
      })
    });

    const data = await response.json();

    // If FASTAPI indicates site is blocked, redirect the user to "blocked.html" page
    if (data.blocked) {
      chrome.tabs.update(details.tabId, { 
        url: chrome.runtime.getURL(`blocked.html?site=${hostname}`) 
      });
    }
  } catch (err) {

    // Log errors to extension console ( e.g., if FASTAPI server is offline) 
    console.error('Blocker check failed:', err);
  }
});

