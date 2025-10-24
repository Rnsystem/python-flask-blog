import requests
import json
import urllib3

# 開発中はSSL警告を無視（本番では証明書設定推奨）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# FileMakerDataAPIクラス
class FileMakerDataAPI:
    def __init__(self, host, database,user, password, layout=None, verify_ssl=False):
        self.host = host.rstrip('/')
        self.database = database
        self.layout = layout
        self.user = user
        self.password = password
        self.verify_ssl = verify_ssl  # False: SSL証明書検証しない（開発用）
        self.token = self.get_token()

    # トークン取得（POST必須）
    def get_token(self):
        url = f'{self.host}/fmi/data/vLatest/databases/{self.database}/sessions'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, auth=(self.user, self.password), verify=self.verify_ssl)
        if response.status_code == 200:
            return response.json()['response']['token']
        else:
            print(url)
            raise Exception(f'Token取得エラー: {response.status_code} {response.text}')

    # 条件付きレコード検索（_findエンドポイントにPOST）
    def find_records(self, query=None, layout=None, sort=None, limit=None, offset=None):
        layout = layout or self.layout  # 指定がなければ初期化時のレイアウトを使用
        url = f'{self.host}/fmi/data/vLatest/databases/{self.database}/layouts/{layout}/_find'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        payload = {}
        if query:
            payload['query'] = [query]
        if sort:
            payload['sort'] = sort
        if limit:
            payload['limit'] = limit
        if offset:
            payload['offset'] = offset
        response = requests.post(url, headers=headers, data=json.dumps(payload), verify=self.verify_ssl)
        if response.status_code == 200:
            res_data = response.json()['response']['data']
            data_arr = []
            for record in res_data:
                # fieldData 部分のみを取り出してリストに格納
                data_arr.append(record.get('fieldData', {}))

            return data_arr

        else:
            raise Exception(f'レコード取得エラー: {response.status_code} {response.text}')


    # セッション終了（トークン削除）
    def logout(self):
        url = f'{self.host}/fmi/data/vLatest/databases/{self.database}/sessions/{self.token}'
        headers = {'Authorization': f'Bearer {self.token}'}
        try:
            requests.delete(url, headers=headers, verify=self.verify_ssl)
        except Exception as e:
            print(f"ログアウト時にエラー発生: {e}")


if __name__ == '__main__':
    print("\n----------")
    print("main")
    print('-----')
