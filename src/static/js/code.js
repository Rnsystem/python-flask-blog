
// ソースコードのコピーボタン
function copyToClipboard(elementId) {
  var copyText = document.getElementById(elementId).innerText;
  var textarea = document.createElement('textarea');
  textarea.value = copyText;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand('copy');
  document.body.removeChild(textarea);
  // alert('クリップボードにコピーしました');
}


// アコーディオン表示、非表示切替ボタン
// $('.code-container .hide-text').hide();
$(".readmore").on("click", function() {
    $(this).toggleClass("on-click");
    // $(this).prev().slideToggle(); // 最初のもの（元コード）
    // $(this).prev('.code-container .hide-text').slideToggle(); // すべて閉じる処理（すべてを閉じるコード）
    // var content = $(this).prev('.code-container .hide-text');
    var content = $(this).closest('.code-container').find('.hide-text');
    if (content.hasClass('is-expanded')) {
        content.removeClass('is-expanded');
        // スクロール位置をアニメーションで上部に移動
        content.animate({ scrollTop: 0 }, "slow");
        // content.slideUp(); // アコーディオンを閉じる (すべて閉じてしまうためコメントアウト)
    } else {
        content.addClass('is-expanded');
        content.slideDown(); // アコーディオンを開く
    }
});