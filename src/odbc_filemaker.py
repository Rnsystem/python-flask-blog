

import pyodbc


# FileMakerODBCクラス
class FileMakerODBC():
    # 初期設定
    def __init__(self, dsn, user, password, database):
        # 接続文字列を作成します
        conn_str = f'DSN={dsn};UID={user};PWD={password};DATABASE={database}'
        # 接続を確立します
        self.conn = pyodbc.connect(conn_str)
        # カーソルを作成します
        self.cursor = self.conn.cursor()

    # クエリを実行します
    def execute(self, query):
        self.cursor.execute(query)
        # 結果をフェッチします
        rows = self.cursor.fetchall()
        return rows
    
    # クエリを実行します
    def execute_dict(self, query):
        # クエリを実行
        rows = self.execute(query)
        # カラム名を取得
        columns = self.get_colums()
        # 結果格納用の変数を定義
        res = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            res.append(row_dict)
        return res

    # カラム一覧を取得
    def get_colums(self):
        columns = [column[0] for column in self.cursor.description]
        return columns

    # 接続を閉じます
    def close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    print("\n----------")
    print("main")
    print('-----')
