
  (function(){
    const sel = document.getElementById('categorySelect');
    const btn = document.getElementById('applyCategoryBtn');

    if (sel) {
      // 選択変更でボタンの有効/無効を切り替え
      sel.addEventListener('change', () => {
        if (btn) btn.disabled = !sel.value;
      });
    }

    if (btn) {
      // 更新ボタン押下で /category/<code> へ遷移
      btn.addEventListener('click', () => {
        const val = sel.value;
        if (!val) return;
        window.location.href = '/category/' + encodeURIComponent(val);
      });
    }
  })();