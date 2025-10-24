/* =====================================================
   Swiper.js 設定ファイル
   - クラス名を "swiper-slider-" に統一して他と競合しないように変更
===================================================== */

document.addEventListener("DOMContentLoaded", function() {
    const swiper = new Swiper(".swiper-slider", {
        slidesPerView: 3,  // 画面に表示するスライドの数
        spaceBetween: 10,  // スライド間のスペース
        loop: true,  // 無限ループ設定
        loopAdditionalSlides: 3, // 無限ループをスムーズにするための追加スライド
        speed: 800,  // スライドの切り替え速度（ms単位）
        autoplay: {
            delay: 3000, // 自動スライドの間隔（ms）
            disableOnInteraction: false, // ユーザーが操作しても自動スライドを続行
        },
        navigation: {
            nextEl: ".swiper-slider-next", // 次へボタン
            prevEl: ".swiper-slider-prev", // 前へボタン
        },
        grabCursor: true,  // マウスカーソルを"つかむ"アイコンに変更
        effect: 'slide',  // スライド効果
        breakpoints: {
            900: { slidesPerView: 4 }, // PCでは3枚表示
            600: { slidesPerView: 3 }, // タブレットでは2枚表示
            0: { slidesPerView: 2 },  // スマホでは1枚表示
        }
    });

    // マウスオーバーで自動スライドを停止
    swiper.el.addEventListener('mouseenter', function () {
        swiper.autoplay.stop();
    });

    // マウスアウトで自動スライドを再開
    swiper.el.addEventListener('mouseleave', function () {
        swiper.autoplay.start();
    });
});
