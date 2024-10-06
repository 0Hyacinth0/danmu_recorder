
const md5 = require("md5");

function getSin(lm){
    let str = 'Dkdpgh4ZKsQB80/Mfvw36XI1R25+WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe='
    let ss = ''
    for (let i = 0; i < lm.length; i+=3) {
        let num1 = (lm.charCodeAt(i) & 255) << 16
        let num2 = (lm.charCodeAt(i+1) & 255) << 8
        let num3 = lm.charCodeAt(i+2) & 255
        let num4 = (num1 | num2) | num3
        ss += str.charAt((num4 & 16515072) >> 18);
        ss += str.charAt((num4 & 258048) >> 12);
        ss += str.charAt((num4 & 4032) >> 6);
        ss += str.charAt((num4 & 63) >> 0);
    }
    return ss
}

let lm = "P\u000bËV\" \u001fËL"

// console.log(getSin(lm))

_0x1f3b8d = function(a) {
    _0x19ae48 = [null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,0,1,2,3,4,5,6,7,8,9,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,10,11,12,13,14,15]
    for (var b = a.length >> 1, c = b << 1, e = new Uint8Array(b), d = 0, t = 0; t < c;) {
        e[d++] = _0x19ae48[a.charCodeAt(t++)] << 4 | _0x19ae48[a.charCodeAt(t++)];
    }
    return e;
}


function _0x4145f8(e, r) {
    for (var a = r['length'], n = new ArrayBuffer(a + 1), f = new Uint8Array(n), c = 0, i = 0; i < a; i++) {
        f[i] = r[i], c ^= r[i];
    }
    f[a] = c;
    var o = 255 & Math['floor'](255 * Math['random']()), d = String['fromCharCode']['apply'](null, f), _ = _0x21db29(String['fromCharCode'](o), d), x = "";
    return x += String['fromCharCode'](e), x += String['fromCharCode'](o), getSin(x += _);
}
function _0x21db29(e, r) {
    for (var a, n = [], f = 0, c = "", i = 0; i < 256; i++) {
        n[i] = i;
    }
    for (var o = 0; o < 256; o++) {
        f = (f + n[o] + e['charCodeAt'](o % e['length'])) % 256, a = n[o], n[o] = n[f], n[f] = a;
    }
    var d = 0;
    f = 0;
    for (var _ = 0; _ < r['length']; _++) {
        f = (f + n[d = (d + 1) % 256]) % 256, a = n[d], n[d] = n[f], n[f] = a, c += String['fromCharCode'](r['charCodeAt'](_) ^ n[(n[d] + n[f]) % 256]);
    }
    return c;
}


function getSigdd(room_id,user_unique_id) {
    let url = 'live_id=1,aid=6383,version_code=180800,webcast_sdk_version=1.0.12,room_id='+room_id+',sub_room_id=,sub_channel_id=,did_rule=3,user_unique_id='+user_unique_id+',device_platform=web,device_type=,ac=,identity=audience'
    url = md5(url)
    let uu = new Uint8Array(9)
    let num = _0x1f3b8d(md5(_0x1f3b8d(url)))
    let num1 = _0x1f3b8d(md5(_0x1f3b8d(md5(''))))
    uu[0] = 1;
    uu[1] = 0;
    uu[2] = 1;
    uu[3] = 14;
    uu[4] = num1[14];
    uu[5] = num1[15];
    uu[6] = num[14];
    uu[7] = num[15];
    uu[8] = 255 & Math['floor'](255 * Math['random']());
    let d= 0 | 1 << 6 | false << 5 | (1 & Math['floor'](100 * Math['random']())) << 4 | 0
    return _0x4145f8(d,uu)
}
// // let uu = new Uint8Array([{"0":2,"1":0,"2":1,"3":14,"4":255,"5":255,"6":37,"7":91,"8":192}])
// let uu = new Uint8Array([2,0,1,14,255,255,37,91,192])
// console.log(_0x4145f8(64,uu))
room_id = '7368225756100479763'
user_unique_id = '7313435273566897690'
console.log(getSigdd(room_id,user_unique_id))
