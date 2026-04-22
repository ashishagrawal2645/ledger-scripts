import puppeteer from 'puppeteer';

(async () => {
    // Launch the browser and open a new blank page
    const browserURL = 'http://127.0.0.1:9222';
    const browser = await puppeteer.connect({ browserURL });


    const page = await browser.newPage();

    await page.setViewport(null);
    const gc = [
        'GNTQKHAD6SEDBU','7FFEKCC399R2T9','M6KJ3MQ446UTQM','UDMA5JR3543CM7','CEJK6TAJU9TCB9','43DEADHPERGRU3','ZWYGQ93VCNQKXQ','C2M95TEC2C9V6V','YYZZWHSQNZRNG6','JWBMWVAHWQGDX9','VBBZGBKT7YH2UF','AFUUTF674HNFQK','NMQ4EZED3GTJXS','HKH238M3RY7EGQ','4C2UFT2HV8ESUY','2SE79E3M3Y67F7','G66YFDSXBQ43YD','J9NFHAV2XCE4AK','F9FVRQRCK77JJ8','W4UJCGYYT6HBTW'
    ];

    for (var i = 0; i < gc.length; i++) {

        await page.goto('https://www.amazon.in/apay-products/gc/claim');

        await page.waitForSelector('#claim-Code-input-box');
        console.log('text box visible');
        console.log(gc[i]);
        await page.evaluate((gc) => {
            document.getElementById('claim-Code-input-box').value = gc;
        }, gc[i]);

        // const tb = await page.$('#claim-Code-input-box');
        // await tb.evaluate(input => input.textContent = gc[i]);
        await page.click('.add-gift-card-button');
        const selector = await page.waitForSelector('#thankYouPageTitle', { visible: true, timeout: 30000 });
        console.log('thank you page loaded');

        if (!selector) {
            console.log('gc addition failed: ' + gc[i]);
            break;
        }
    }
    console.log('all GC added');
    // await browser.close();
})();
