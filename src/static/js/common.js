/* 各エレメントのアニメーションを設定 */
function showElementAnimation() {
    // ボタンの表示非表示
    showElementAnimation_arrow_button();
    // コンテンツの表示非表示
    showElementAnimation_mainContent()
        .then(() => showElementAnimation_subContent())
        .then(() => showElementAnimation_topMainCatchTxt())
        .then(() => showElementAnimation_cookieDialog())
        .catch(error => console.error(error)); // エラーハンドリング
}

function showElementAnimation_arrow_button() {
    var scrollButton = document.querySelector('.scroll_button');
    if (!scrollButton) return;  // scrollButtonが存在しない場合は処理しない

    // ボタンにアニメーション用のクラスを追加
    scrollButton.style.transition = 'opacity 0.3s ease';  // アニメーションの設定（透明度の変更）

    // スクロール位置が一番上でない場合、ボタンを表示
    if (window.scrollY > 0) {
        // ボタンが表示されるとき（透明度をすぐに1に）
        scrollButton.style.display = 'flex';  // まず表示
        setTimeout(() => {
            scrollButton.style.opacity = '1';  // 透明度を1にしてアニメーション
        }, 10);  // 少しだけ遅延を入れることで、表示が即座に行われてからアニメーションを開始
    } else {
        // ボタンが非表示になるとき（透明度を0に）
        scrollButton.style.opacity = '0';  // 透明度を0にしてアニメーション
        // アニメーション終了後に非表示にする
        scrollButton.addEventListener('transitionend', function() {
            if (scrollButton.style.opacity === '0') {
                scrollButton.style.display = 'none';  // 透明度が0になった後に非表示にする
            }
        });
    }
}


/* 各エレメントのアニメーションを設定 */
function showElementAnimation_mainContent() {
    return new Promise((resolve, reject) => {
        try {
            var elements = document.getElementsByClassName('js-animation-mainContent');
            if (!elements || elements.length === 0) return resolve(); // 要素がない場合でもresolve()を返す

            var elementsCount = elements.length;
            var animationsCompleted = 0;

            for (var i = 0; i < elements.length; i++) {
                var element = elements[i];
                var showTiming = window.innerHeight > 768 ? 200 : 40;
                var scrollY = window.pageYOffset;
                var windowH = window.innerHeight;
                var elemClientRect = element.getBoundingClientRect();
                var elemY = scrollY + elemClientRect.top;

                if (scrollY + windowH - showTiming > elemY) {
                    element.classList.add('is-show');
                } else if (scrollY + windowH < elemY) {
                    element.classList.remove('is-show');
                }

                // アニメーション終了時にresolveを呼ぶ
                element.addEventListener('transitionend', () => {
                    animationsCompleted++;
                    if (animationsCompleted === elementsCount) {
                        resolve(); // 全ての要素のアニメーションが終了したらresolve
                    }
                });
            }
        } catch (error) {
            reject(error);
        }
    });
}

function showElementAnimation_subContent() {
    return new Promise((resolve, reject) => {
        try {
            var elements = document.getElementsByClassName('js-animation-subContent');
            if (!elements || elements.length === 0) return resolve(); // 要素がない場合でもresolve()を返す

            var elementsCount = elements.length;
            var animationsCompleted = 0;

            for (var i = 0; i < elements.length; i++) {
                var element = elements[i];
                var showTiming = window.innerHeight > 768 ? 200 : 40;
                var scrollY = window.pageYOffset;
                var windowH = window.innerHeight;
                var elemClientRect = element.getBoundingClientRect();
                var elemY = scrollY + elemClientRect.top;

                if (scrollY + windowH - showTiming > elemY) {
                    element.classList.add('is-show');
                } else if (scrollY + windowH < elemY) {
                    element.classList.remove('is-show');
                }

                // アニメーション終了時にresolveを呼ぶ
                element.addEventListener('transitionend', () => {
                    animationsCompleted++;
                    if (animationsCompleted === elementsCount) {
                        resolve(); // 全ての要素のアニメーションが終了したらresolve
                    }
                });
            }
        } catch (error) {
            reject(error);
        }
    });
}

function showElementAnimation_topMainCatchTxt() {
    return new Promise((resolve, reject) => {
        try {
            var elements = document.getElementsByClassName('js-animation-topMainCatchTxt');
            if (!elements || elements.length === 0) return resolve(); // 要素がない場合でもresolve()を返す

            var elementsCount = elements.length;
            var animationsCompleted = 0;

            for (var i = 0; i < elements.length; i++) {
                var element = elements[i];
                var showTiming = window.innerHeight > 768 ? 200 : 40;
                var scrollY = window.pageYOffset;
                var windowH = window.innerHeight;
                var elemClientRect = element.getBoundingClientRect();
                var elemY = scrollY + elemClientRect.top;

                if (scrollY + windowH - showTiming > elemY) {
                    element.classList.add('is-show');
                } else if (scrollY + windowH < elemY) {
                    element.classList.remove('is-show');
                }

                // アニメーション終了時にresolveを呼ぶ
                element.addEventListener('transitionend', () => {
                    animationsCompleted++;
                    if (animationsCompleted === elementsCount) {
                        resolve(); // 全ての要素のアニメーションが終了したらresolve
                    }
                });
            }
        } catch (error) {
            reject(error);
        }
    });
}

function showElementAnimation_cookieDialog() {
    return new Promise((resolve, reject) => {
        try {
            var cookieOverlay = document.getElementById('cookie-overlay');
            var cookieDialog = document.getElementById('cookie-dialog');
            var animationsCompleted = 0;

            function handleAnimationEnd() {
                animationsCompleted++;
                if (animationsCompleted === 2) {
                    resolve();
                }
            }

            if (cookieOverlay) {
                cookieOverlay.classList.add('is-show');
                cookieOverlay.addEventListener('transitionend', handleAnimationEnd, { once: true });
            } else {
                animationsCompleted++;
            }

            if (cookieDialog) {
                cookieDialog.classList.add('is-show');
                cookieDialog.addEventListener('transitionend', handleAnimationEnd, { once: true });
            } else {
                animationsCompleted++;
            }
        } catch (error) {
            reject(error);
        }
    });
}

// ページ読み込み時にアニメーションを実行
showElementAnimation();

// スクロールイベントでアニメーションを適用
window.addEventListener('scroll', showElementAnimation);

// 初回ロード時にスクロールイベントを手動でトリガーする
window.addEventListener('load', showElementAnimation);

/*-- pagetop --*/
$(function() {
    var showFlag = false;
    var topBtn = $('.pagetop');   
    topBtn.css('bottom', '-135px');
    //スクロールが100に達したらボタン表示
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            if (showFlag == false) {
                showFlag = true;
                topBtn.stop().animate({'bottom' : '10px'}, 200);
            }
        } else {
            if (showFlag) {
                showFlag = false;
                topBtn.stop().animate({'bottom' : '-135px'}, 200);
            }
        }
    });
    //スクロールしてトップ
    topBtn.click(function () {
        $('body,html').animate({
            scrollTop: 0
        }, 500);
        return false;
    });
});
$(function(){
    $('a[href^="#"]').click(function(){ 
        var speed = 500;
        var href= $(this).attr("href"); 
        var target = $(href == "#" || href == "" ? 'html' : href);
        var position = target.offset().top;
        $("html, body").animate({scrollTop:position}, speed, "swing");
        return false;
    });
});
/*-- /pagetop --*/
