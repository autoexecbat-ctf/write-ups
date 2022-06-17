# Challege 53 - No Door 1

We were given a Gather.town link, and it was a service that allowed online gathering with a 2D JRPG-like interface. After creating our avatar, we got in, walked around, and immediately attracted to a red herring treasure box in the center of the map that has nothing.

Given our target is to "Find the hidden room.", we walked around looking for teleporters. Nothing. We have also tried using a Chrome extension to [try to teleport, but that failed too](https://github.com/michmich112/teleporter).

Which is then time to look at the browser inspector and see if there are anything of interest. It seems that the map was loaded in WebSocket, and a 44.2kB exchange seems very interesting.

Looking at it, we are already seeing a lot of assets being loaded. Judging from the URL, we ignored the ones that look like:

```
https://cdn.gather.town/storage.googleapis.com/gather-town.appspot.com/internal-dashboard/images/xxxxxxx
```

because these likely are the default assets. Instead, we focused on these that look like custom assets:

```
https://cdn.gather.town/v0/b/gather-town.appspot.com/o/uploads%2Fxxxxxxxxx%2Fmaps%2Fxxxxxxx?alt=media&token=xxxxxx
```

When we combed the file, the word `Secret` showing near `Living Room` indiciated that there is really a hidden space! But it turned out to be unnecessary, since we simply saw the flag there directly in the transport file by searching for the flag prefix.

Solved!

(Hindsight: we should really look for global objects first in the `document` first. Did not expect the whole `gameSpace` is exposed after all lol.)
