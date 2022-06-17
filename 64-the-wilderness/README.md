# Challege 64 - The Wilderness

After downloading the source and looking at the PHP file, we knew that this should be a question regarding a known vulnerability since the PHP file does not really do anything at all.

The `Dockerfile` included shows that the tagged PHP commit `c730aa26bd52829a49f2ad284b181b7e82a68d7d` was the really notorious PHP 8 backdoor attempt (that, luckily was never released.)

The exploited code uses a payload on `User-Agentt`. When it is `zerodium`, it basically runs anything we throw to it.

We went lazy and simply used [one of the many PoCs out there](https://github.com/flast101/php-8.1.0-dev-backdoor-rce/blob/main/revshell_php_8.1.0-dev.py) to open a reverse shell, and `cat index.php`. Done!
