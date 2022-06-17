urlBase = 'https://bl.ocks.org/positron-browser-by/raw/52c42a2f358c82dd22d75dc74c6e9a96/?';
for (var i = 5500000; i < 9500000; i++) {
  var url = `${urlBase}${i}`;
  var HashCash = Math.abs(require('crypto-js/sha256')(url).words[1])>>1<1<<11;
  if(HashCash){
    console.log(url);
  }
}
