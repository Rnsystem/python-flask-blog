import sys
import stripe

# 参考文献
# https://docs.stripe.com/api/products
# https://docs.stripe.com/api/prices


# FileMakerAPIクラス
class StripeAPI():
    # 初期設定
    def __init__(self, secret_key):
        # stripe モジュールの API キーを設定
        stripe.api_key = secret_key
        self.stripe = stripe

    # 商品リストを取得
    def get_products(self, limit=10) -> list:
        products = self.stripe.Product.list(limit=limit) 
        return products
    
    # 商品を取得
    def find_product(self, product_id) -> dict:
        product = self.stripe.Product.retrieve(product_id) 
        return product

    # 商品価格リストを取得
    def get_prices(self, limit=10) -> list:
        products = self.stripe.Price.list(limit=limit) 
        return products
    
    # 商品価格を取得
    def find_price(self, price_id) -> dict:
        product = self.stripe.Price.retrieve(price_id)
        return product
    
    # 決済
    def post_checkout(self, success_url, cancel_url, *items, mode='payment') -> dict:
        try:
            session = self.stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=items,
                mode=mode,
                success_url=success_url,
                cancel_url=cancel_url,
                shipping_address_collection={
                    'allowed_countries': ['JP'],  # 配送可能な国を指定
                },
                phone_number_collection={
                    'enabled': True  # 電話番号を必須にする
                }
            )
            return {'status':'ok', 'code':200, 'message':'success', 'id':str(session.id)}
        except Exception as e:
            print(f"Error creating checkout session: {e}")  # 詳細なエラーメッセージを出力
            return {'status':'error', 'code':403, 'message':str(e), 'id':None}



if __name__ == '__main__':
    print("\n----------")
    print("main")
    print('-----')