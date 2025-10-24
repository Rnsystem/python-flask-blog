# mysql-connector-python
import mysql.connector as mysqldb
import sys


#RakutenWebService_Ichibaitemを操作するためのクラス
class MySqlControl:
    #初期値
    def __init__(self, host, port, user, password, database):
        # データベースへの接続とカーソルの生成
        #情報を設定
        try:
            self.connection = mysqldb.connect(
                host        = str(host),
                port        = int(port),
                user        = str(user),
                passwd      = str(password),
                database    = str(database),
                )
        except Exception as e:
            print(f"RWSINFO初期設定に失敗しました。: {e}")
            sys.exit(1)

    #カーソルを設定する
    def cursor(self, dicttype=True):
      return self.connection.cursor(dictionary=dicttype, buffered=True)

    #辞書型を一括インポート01
    def execute_insert_dict1(self, tbl_name,**kwargs) -> str:
        try:
            #変数を定義
            tbl_deli    = '`'   #区切り文字
            key_deli    = '`'   #区切り文字
            val_deli    = '\''  #区切り文字
            keys        = ''    #項目名
            values      = ''    #値
            #辞書のキーワード分繰り返す
            for k,v in kwargs.items():
                #クォーテーション判定【】
                key     = 'null' if k is None else\
                            key_deli + str(k) + key_deli if type(k) is str else str(k)
                value   = 'null' if v is None else\
                            val_deli + str(v) + val_deli if type(v) is str else str(v)
                keys    += key if not keys else ', ' + key
                values  += value if not values else ', ' + value
            #sql構文作成
            sql =   'INSERT INTO '+ tbl_deli + tbl_name + tbl_deli + '(' + keys + ') VALUES (' + values + ')'
            # print(sql)
        except Exception as e:
            print(f"MySQL辞書型を一括インポート01に失敗しました。: {e}")
            sys.exit(1)
        #返却値出力
        return sql
    
    #辞書型を一括インポート02
    def execute_insert_dict2(self, tbl_name, **kwargs) -> str:
        try:
            columns = kwargs.keys()
            cols_comma_separated = ', '.join(columns)
            binds_comma_separated = ', '.join(['%(' + item + ')s' for item in columns])
            sql = f'INSERT INTO {tbl_name} ({cols_comma_separated}) VALUES ({binds_comma_separated})'
            # print(sql)
        except Exception as e:
            print(f"MySQL辞書型を一括インポート02に失敗しました。: {e}")
            sys.exit(1)
        #返却値出力
        return sql
    
    #辞書型を一括アップデート01
    def execute_update_dict(self, tbl_name, where_column, **kwargs) -> str:
        try:
            del kwargs[where_column]
            columns = kwargs.keys()
            # cols_comma_separated = ' = %s, '.join(columns)
            binds_comma_separated = ', '.join([item + ' = %(' + item + ')s ' for item in columns])
            sql = f'UPDATE {tbl_name} SET {binds_comma_separated} WHERE {where_column} = %({where_column})s'
            # print(sql)
        except Exception as e:
            print(f"MySQL辞書型を一括インポート02に失敗しました。: {e}")
            sys.exit(1)
        #返却値出力
        return sql
    #辞書型一致する検索条件を表示
    def execute_select_dict(self, tbl_name, *args, **kwargs) -> str:
        try:
            columns = kwargs.keys()
            cols_comma_separated = ', '.join(args)
            binds_comma_separated = 'and '.join([str(k)+'=\''+v+'\' ' for k,v in kwargs.items()])
            sql = f'SELECT {cols_comma_separated} FROM `{tbl_name}` WHERE {binds_comma_separated}'
            print(sql)
        except Exception as e:
            print(f"MySQL辞書型を一括インポート02に失敗しました。: {e}")
            sys.exit(1)
        #返却値出力
        return sql
    #保存を実行
    def commit(self):
        try:
            self.connection.commit()
        except Exception as e:
            print(f"MySQLコミットに失敗しました。: {e}")
            sys.exit(1)
    #コネクションを閉じる
    def close(self):
        try:
            self.connection.close()
        except Exception as e:
            print(f"MySQLコネクションを閉じるのに失敗しました。: {e}")
            sys.exit(1)
    #辞書型の中にある配列、辞書のみ登録する。
    def conversion_dict(self, *args, **kwargs) -> dict:
        cd = {}
        for k,v in kwargs.items():
            if k in args:
                cd[k] = v
        return cd
    

#mainの実行
if __name__ == '__main__':
    print("\n----------")
    print("main")
    print('-----')
