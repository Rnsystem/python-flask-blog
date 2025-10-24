document.addEventListener('DOMContentLoaded', function() {
    // 初回訪問の場合にクッキーの承諾ダイアログを表示
    if (!getCookie('cookies_accepted')) {
        document.getElementById('cookie-overlay').classList.remove('hidden');
        document.getElementById('cookie-dialog').classList.remove('hidden');
    }else{
        document.getElementById('cookie-overlay').classList.add('hidden');
        document.getElementById('cookie-dialog').classList.add('hidden');
        // console.log("test");
    }
    // クッキー承諾ボタンがクリックされたときの処理
    document.getElementById('accept-cookies').onclick = function() {
        setCookie('cookies_accepted', 'true', 365);
        hideCookieDialog();
    };
    // クッキー拒否ボタンがクリックされたときの処理
    document.getElementById('decline-cookies').onclick = function() {
        setCookie('cookies_accepted', 'false', 365);
        hideCookieDialog();
        alert("クッキーを拒否しました。");
    };
});

// クッキーの設定関数
function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

// クッキーを取得する関数
function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

// クッキーダイアログを非表示にする関数
function hideCookieDialog() {
    document.getElementById('cookie-overlay').classList.add('hidden');
    document.getElementById('cookie-dialog').classList.add('hidden');
}
