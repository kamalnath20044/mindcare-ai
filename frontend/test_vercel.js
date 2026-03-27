const https = require('https');

https.get('https://mindcare-ai-chi.vercel.app/', (res) => {
  let data = '';
  res.on('data', d => data += d);
  res.on('end', () => {
    let match = data.match(/src="(\/assets\/index-[^"]+\.js)"/);
    if (!match) return console.log('no js file found');
    
    let url = 'https://mindcare-ai-chi.vercel.app' + match[1];
    console.log('Fetching', url);
    
    https.get(url, (resJs) => {
      let jsData = '';
      resJs.on('data', d => jsData += d);
      resJs.on('end', () => {
        let regex = /https?:\/\/[a-zA-Z0-9.-]+\.onrender\.com[a-zA-Z0-9.\/_-]*/g;
        let urls = [...new Set(jsData.match(regex))];
        console.log('API URLs embedded in Vercel deployment:');
        console.log(urls);
      });
    });
  });
});
