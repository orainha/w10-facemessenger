    function encodeUnicode(str) {
        // first we use encodeURIComponent to get percent-encoded UTF-8,
        // then we convert the percent encodings into raw bytes which
        // can be fed into btoa.
        return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g,
            function toSolidBytes(match, p1) {
                return String.fromCharCode('0x' + p1);
        }));
    }
  
  //console.log(encodeUnicode('JavaScript is fun é 🎉')); // SmF2YVNjcmlwdCBpcyBmdW4g8J+OiQ==
  //console.log(encodeUnicode('🔥💡')); // 8J+UpfCfkqE=
  