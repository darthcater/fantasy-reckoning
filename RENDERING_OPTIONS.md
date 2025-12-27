# HTML to PNG Rendering Options for Fantasy Reckoning

## Use Case
Convert HTML card previews (website/index.html) to 1080×1920px PNG images for Instagram Story sharing.

---

## Option 1: Playwright ⭐ **RECOMMENDED**

### Overview
Modern browser automation tool with excellent screenshot capabilities. Successor to Puppeteer with broader browser support.

### Pros
- **Multi-browser support**: Chromium, Firefox, WebKit (vs Puppeteer's Chromium-only)
- **Modern API**: Auto-waiting, better error handling, parallel execution
- **Multi-language**: JavaScript, TypeScript, Python, Java, C#
- **Active development**: Built by ex-Puppeteer team at Microsoft
- **Screenshot quality**: Native high-DPI support, pixel-perfect rendering

### Cons
- Larger package size (~300MB with browsers)
- Slightly steeper learning curve than Puppeteer

### Implementation Example
```javascript
const { chromium } = require('playwright');

async function renderCard(htmlPath, outputPath) {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.setViewportSize({ width: 1080, height: 1920 });
  await page.goto(`file://${htmlPath}`);

  // Add data-render="true" attribute to scale up for PNG
  await page.evaluate(() => {
    document.querySelector('.card-preview').setAttribute('data-render', 'true');
  });

  await page.screenshot({
    path: outputPath,
    type: 'png',
    fullPage: false
  });

  await browser.close();
}
```

### Recommended for Fantasy Reckoning?
**YES** - Best balance of features, quality, and future-proofing.

---

## Option 2: Puppeteer

### Overview
Google's headless Chrome automation library. Battle-tested and widely used.

### Pros
- **Mature ecosystem**: Extensive documentation, large community
- **Lighter weight**: Smaller than Playwright
- **Chrome DevTools integration**: Direct access to Chrome APIs
- **Simple API**: Easy to get started

### Cons
- **Chromium-only**: No Firefox/Safari support
- **JavaScript/TypeScript only**: Limited language support
- Less modern features compared to Playwright

### Implementation Example
```javascript
const puppeteer = require('puppeteer');

async function renderCard(htmlPath, outputPath) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  await page.setViewport({ width: 1080, height: 1920 });
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0' });

  await page.screenshot({
    path: outputPath,
    type: 'png',
    clip: { x: 0, y: 0, width: 1080, height: 1920 }
  });

  await browser.close();
}
```

### Recommended for Fantasy Reckoning?
**MAYBE** - Solid choice if you only need Chrome rendering and want smaller bundle size.

---

## Option 3: node-html-to-image

### Overview
Wrapper around Puppeteer that simplifies HTML→image conversion with templating support.

### Pros
- **Simple API**: One-liner conversions
- **Handlebars templating**: Inject data directly into HTML templates
- **Multiple formats**: PNG, JPEG, WebP support
- **TypeScript support**: Built-in type definitions

### Cons
- Wrapper adds abstraction layer
- Uses Puppeteer under the hood (Chromium-only)
- Less control than direct Puppeteer/Playwright

### Implementation Example
```javascript
const nodeHtmlToImage = require('node-html-to-image');

await nodeHtmlToImage({
  output: './card.png',
  html: '<html><body>{{content}}</body></html>',
  content: { content: cardData },
  puppeteerArgs: {
    defaultViewport: {
      width: 1080,
      height: 1920
    }
  }
});
```

### Recommended for Fantasy Reckoning?
**NO** - Adds unnecessary abstraction. Direct Playwright/Puppeteer gives more control.

---

## Option 4: html2canvas (Client-side)

### Overview
Browser-only library that converts DOM to canvas, then canvas to PNG.

### Pros
- **No backend needed**: Runs in browser
- **No external dependencies**: Pure JavaScript
- **Instant rendering**: No page load delays

### Cons
- **Client-side only**: Requires user browser, can't automate
- **Rendering inconsistencies**: Not pixel-perfect across browsers
- **CSS limitations**: Some styles not supported
- **Performance**: Slower for complex layouts

### Recommended for Fantasy Reckoning?
**NO** - Requires users to generate images themselves. Not suitable for automated batch generation.

---

## Comparison Table

| Feature | Playwright | Puppeteer | node-html-to-image | html2canvas |
|---------|-----------|-----------|-------------------|-------------|
| **Browser Support** | Multi | Chrome only | Chrome only | All (client) |
| **Server-side** | ✅ | ✅ | ✅ | ❌ |
| **Image Quality** | Excellent | Excellent | Good | Fair |
| **Ease of Use** | Medium | Easy | Very Easy | Easy |
| **Bundle Size** | ~300MB | ~170MB | ~170MB | ~50KB |
| **Future-proof** | ✅ | ✅ | ⚠️ | ⚠️ |
| **Batch Processing** | ✅ | ✅ | ✅ | ❌ |

---

## Recommendation for Fantasy Reckoning

### Go with **Playwright** because:

1. **Better quality**: Best screenshot rendering engine
2. **Future-proof**: Active development, modern API
3. **Flexibility**: Multi-browser support if you ever need it
4. **Reliability**: Auto-waiting prevents timing issues
5. **Batch processing**: Perfect for generating cards for entire league

### Implementation Plan:

```javascript
// scripts/render-cards.js
const { chromium } = require('playwright');
const fs = require('fs');

async function renderAllCards(leagueData) {
  const browser = await chromium.launch();

  for (const manager of leagueData.managers) {
    for (let cardNum = 1; cardNum <= 4; cardNum++) {
      const page = await browser.newPage();
      await page.setViewportSize({ width: 1080, height: 1920 });

      // Load card HTML with manager data
      await page.goto(`file://${__dirname}/../website/index.html`);

      // Inject data and select specific card
      await page.evaluate(({ manager, cardNum }) => {
        // Set data-render="true" for PNG mode
        const card = document.querySelector(`.card-preview:nth-child(${cardNum})`);
        card.setAttribute('data-render', 'true');
        // Inject manager data...
      }, { manager, cardNum });

      // Screenshot
      await page.screenshot({
        path: `./output/${manager.name}_card_${cardNum}.png`,
        type: 'png'
      });

      await page.close();
    }
  }

  await browser.close();
}
```

---

## Next Steps

1. **Install Playwright**: `npm install playwright`
2. **Create render script**: `scripts/render-cards.js`
3. **Test with sample data**: Render one card first
4. **Optimize**: Add caching, parallel rendering for speed
5. **Deploy**: Integrate into generation pipeline

---

## Sources

- [Playwright vs Puppeteer: Which to choose in 2025? | BrowserStack](https://www.browserstack.com/guide/playwright-vs-puppeteer)
- [Playwright vs. Puppeteer in 2025 | ZenRows](https://www.zenrows.com/blog/playwright-vs-puppeteer)
- [node-html-to-image - npm](https://www.npmjs.com/package/node-html-to-image)
- [How to render screenshots with Playwright](https://screenshotone.com/blog/how-to-render-screenshots-with-playwright/)
- [HTML5 Canvas Export to High Quality Image | Konva](https://konvajs.org/docs/data_and_serialization/High-Quality-Export.html)
- [7 ways to take website screenshots with node.js | Urlbox](https://urlbox.com/7-ways-website-screenshots-nodejs-javascript)
