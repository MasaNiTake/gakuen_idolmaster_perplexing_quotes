import sqlite3
import json

# 空のインメモリDBを作成
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

# CREATE文を読み込んで実行
try:
    with open("create_template.sql", "r", encoding="utf-8") as f:
        create_sql = f.read()
    cursor.executescript(create_sql)
    print("CREATE TABLE文の実行に成功しました。")
except FileNotFoundError:
    print("エラー: create_template.sql が見つかりません。ファイルが存在するか確認してください。")
    conn.close() # エラー発生時はDB接続を閉じる
    exit()
except Exception as e:
    print(f"エラー: CREATE TABLE文の実行中にエラーが発生しました: {e}")
    conn.close()
    exit()

# データINSERT文を読み込んで実行
try:
    with open("data.sql", "r", encoding="utf-8") as f:
        insert_sql = f.read()
    cursor.executescript(insert_sql)
    print("INSERT文の実行に成功しました。")
except FileNotFoundError:
    print("エラー: data.sql が見つかりません。ファイルが存在するか確認してください。")
    conn.close()
    exit()
except Exception as e:
    print(f"エラー: INSERT文の実行中にエラーが発生しました: {e}")
    conn.close()
    exit()

# データを取得
try:
    cursor.execute("SELECT * FROM gakuen_idolmaster_perplexing_quotes")
    rows = cursor.fetchall()
    print(f"{len(rows)}件のデータを取得しました。")
except Exception as e:
    print(f"エラー: データの取得中にエラーが発生しました: {e}")
    conn.close()
    exit()

# 不適切な文字のセットを定義します。
# ここに含めた文字が、データから削除されます。
# 例: パスに使用できない文字 ('/', '\', ':', '*', '?', '"', '<', '>', '|', ヌル文字 '\x00')
#     に加えて、ユーザー例にある「…」を含めます。
#     必要に応じて、句読点（'、', '。', '！', '？' など）やその他の記号を追加・削除してください。
invalid_chars_set = set('/\\:*?"<>|\x00.')

cleaned_elements = []
for row in rows:
    cleaned_element = []
    for i, element in enumerate(row):
        if i == 9:
            continue   # 9番目の要素はスキップします
        # null (PythonではNone) でない場合のみ処理対象とします
        if element is not None:
            s = str(element)  # 要素を一旦文字列に変換します
            # 文字列sの中からinvalid_chars_setに含まれない文字だけを選んで新しい文字列(cleaned_s)を作成します
            cleaned_s = "".join(char for char in s if char not in invalid_chars_set)
            # strip後の文字列をリストに追加します
            cleaned_element.append(cleaned_s)
    cleaned_elements.append("-".join(cleaned_element))

# txtファイルに保存
output_txt_filename = "stripped_elements.txt"
try:
    with open(output_txt_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_elements))
    print(f"null以外の要素から不適切な文字をstripし、'{output_txt_filename}'に保存しました。")
except Exception as e:
    print(f"エラー: TXTファイルの書き込み中にエラーが発生しました: {e}")

# カラム名を取得 (JSON出力用)
column_names = [description[0] for description in cursor.description]

# 辞書リストに変換 (JSON出力用)
updated_data = []
for row, cleaned_element in zip(rows, cleaned_elements):
    # 各行を辞書に変換し、cleaned_element を追加
    row_dict = dict(zip(column_names, row))
    row_dict["image_path"] = cleaned_element+".avif"  # cleaned_element を追加
    updated_data.append(row_dict)

# JSONに保存
output_json_filename = "quotes.json"
try:
    with open(output_json_filename, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    print(f"データを'{output_json_filename}'に保存しました。")
except Exception as e:
    print(f"エラー: JSONファイルの書き込み中にエラーが発生しました: {e}")

# 8. DBを閉じる
conn.close()
print("データベース接続を閉じました。")
