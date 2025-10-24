
  // 公開用のStripeキーを設定（Flaskのバックエンドから取得）
  var stripe = Stripe('pk_test_Nej5kGA1pDwAOEofRWwU8A1P');
  var checkoutButton = document.getElementById('checkout-button');
  checkoutButton.addEventListener('click', function () {
      // 渡したい引数（例えば商品IDなど）
      var stripe_price_id = checkoutButton.getAttribute('stripe-price-id');
      var selectedQuantity = document.getElementById('quantity').value;
      fetch('/payment/create-checkout-session', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({
              stripe_price_id: stripe_price_id, // stripe id
              stripe_quantity: selectedQuantity,// 購入数量
          })
      })
      .then(function (response) {
          return response.json();
      })
      .then(function (sessionId) {
          console.log(sessionId)
          return stripe.redirectToCheckout({ sessionId: sessionId.id });
      })
      .then(function (result) {
          if (result.error) {
              alert(result.error.message);
          }
      })
      .catch(function (error) {
          console.error('Error:', error);
      });
  });