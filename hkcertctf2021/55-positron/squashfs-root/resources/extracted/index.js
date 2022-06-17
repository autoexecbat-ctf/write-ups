const {app, BrowserWindow} = require('electron');

const openWindow = (url) => {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    icon: require('path').join(__dirname, '/icon.png'),
    webPreferences: {
      contextIsolation: false,
      nodeIntegration: true
    }
  });
  //win.webContents.openDevTools();
  win.loadURL(url);
}

app.on('ready', () => {
  const home = 'https://bl.ocks.org/positron-browser/raw/de363db7c6eae43a20a932753b1c29b4/';
  var url = process.argv[2] || home;
  var HashCash = Math.abs(require('crypto-js/sha256')(url).words[1])>>1<1<<11;
  if(!url.startsWith('https://bl.ocks.org/positron-browser') || !HashCash){
    url = home;
  }
  openWindow(url);
});

app.on('window-all-closed', () => {
  app.quit();
});
