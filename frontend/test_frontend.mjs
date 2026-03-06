import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('BROWSER CONSOLE:', msg.text()));
  page.on('pageerror', error => console.log('BROWSER ERROR:', error.message));
  page.on('requestfailed', request => console.log('FAILED REQUEST:', request.url(), request.failure().errorText));

  try {
      await page.goto('http://localhost:5173/');
      await page.waitForTimeout(2000);
      
      console.log("Looking for Archiwum button...");
      // Click the Archiwum tab
      await page.click('text=Archiwum');
      await page.waitForTimeout(2000);
      console.log("Clicked! Checking console for errors...");
      await page.waitForTimeout(2000);
  } catch (e) {
      console.log("Script error:", e);
  } finally {
      await browser.close();
  }
})();
