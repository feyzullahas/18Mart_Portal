const puppeteer = require('puppeteer');

(async () => {
    try {
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        
        page.on('console', msg => console.log('PAGE LOG:', msg.text()));
        page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
        
        await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
        
        console.log("Page loaded. HTML snippet:");
        const html = await page.evaluate(() => document.body.innerHTML.substring(0, 500));
        console.log(html);
        
        await browser.close();
    } catch (e) {
        console.error("Puppeteer error:", e);
    }
})();
