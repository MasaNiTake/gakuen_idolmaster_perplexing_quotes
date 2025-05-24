from PIL import Image
import pillow_avif  # Pillow 9.2.0以降でAVIF対応
import os

def trim_and_save_avif(input_path, output_path, resize, target_size_kb=None):
  """画像を縮小し、指定サイズ以下になるようにAVIF形式で保存する。

  Args:
    input_path: 入力画像のパス。
    output_path: 出力画像のパス。
    trim_values: トリミング量 (left, top, right, bottom)。
    target_size_kb: 目標ファイルサイズ (KB)。Noneの場合はサイズ調整なし。
                    この値以下になるようにquantizerを調整します。
  """
  try:
    img = Image.open(input_path)

    # resizeにリサイズ
    img_cropped = img.resize((resize[0], resize[1]), Image.LANCZOS)
    print(f"処理中: {input_path}")

    if target_size_kb is not None:
        target_size_bytes = target_size_kb * 1024
        # AVIFのquantizerは0-63の範囲で、0が最高画質/最大サイズ、63が最低画質/最小サイズ
        current_quantizer = 80 # サイズ調整の開始quantizer（初期値）
        min_quantizer = 20     # quantizerの最小値
        quantizer_step = 5     # サイズオーバーだった場合にquantizerを増やすステップ
        max_attempts = 15      # 最大試行回数
        attempts = 0
        saved_size = float('inf') # 初期サイズは無限大としておく

        print(f"  サイズ調整を試行: 目標 {target_size_kb}KB 以下")

        # 目標サイズを超える限り、または最大試行回数・最大quantizerに達するまでループ
        while saved_size > target_size_bytes and current_quantizer >= min_quantizer and attempts < max_attempts:
            try:
                # AVIFで一時的に保存してサイズを確認する
                # 直接output_pathに保存し、サイズオーバーなら上書きする方法も可能だが、
                # 一時ファイルの方が安全。
                temp_output_path = output_path + ".temp"
                # quantizerを指定して保存を試みる
                img_cropped.save(temp_output_path, format="AVIF", quality=current_quantizer, optimize=True)
                saved_size = os.path.getsize(temp_output_path)

                print(f"  試行 {attempts+1}/{max_attempts}: quantizer={current_quantizer}, サイズ={saved_size/1024:.2f} KB")

                if saved_size > target_size_bytes:
                    # 目標サイズを超えている場合、quantizerを大きくして（圧縮率を上げて）再試行
                    current_quantizer -= quantizer_step
                    if current_quantizer < min_quantizer:
                         current_quantizer = min_quantizer # 上限を超えないように調整

            except Exception as e:
                print(f"  保存試行中にエラーが発生しました: {e}")
                # エラーが発生したら一時ファイルを削除してループを抜ける
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
                break # エラーが発生したらループを抜ける

            attempts += 1

        # ループ終了後の処理
        if saved_size <= target_size_bytes and os.path.exists(temp_output_path):
            # 目標サイズ以下で保存できた場合、一時ファイルを正規のパスに移動/リネーム
            os.rename(temp_output_path, output_path)
            print(f"トリミングとAVIF保存 成功: {input_path} -> {output_path} (最終 quantizer={current_quantizer}, サイズ={saved_size/1024:.2f} KB)")
        elif os.path.exists(temp_output_path):
             # 目標サイズ以下にはできなかったが、最後に保存した一時ファイルが存在する場合
             # そのファイル（最もサイズが小さい可能性がある）を正規のパスに移動/リネーム
             os.rename(temp_output_path, output_path)
             print(f"注意: {input_path} -> {output_path} {max_attempts} 回試行しましたが、目標サイズ {target_size_kb}KB 以下にできませんでした。(最終 quantizer={current_quantizer}, サイズ={saved_size/1024:.2f} KB)")
             print(f"  最後に試行した画像 ({saved_size/1024:.2f} KB) を保存しました。")
        else:
             # エラー等でファイルが保存されなかった場合
             print(f"エラーまたは試行失敗: {input_path} -> {output_path} ファイルは保存されませんでした。")


    else:
        # サイズ指定がない場合、元のコード通り一度だけ保存
        img_cropped.save(output_path, format="AVIF")
        print(f"トリミングとAVIF保存 成功: {input_path} -> {output_path} (サイズ調整なし)")

  except FileNotFoundError:
    print(f"エラー: ファイルが見つかりません: {input_path}")
  except Exception as e:
    print(f"エラー: {input_path} の処理中にエラーが発生しました: {e}")


# --- 使用例 ---
input_dir = "input_img"  # 入力画像が保存されているディレクトリ
output_dir = "output_img" # トリミング後の画像を保存するディレクトリ
# トリミング量 (left, top, right, bottom) - ピクセル数で指定
trim_values = [1280, 720]

# 目標ファイルサイズをKBで指定
# 例: 50KB以下にしたい場合
target_size_kb = 50

# または、サイズ調整をしない場合は None に設定
# target_size_kb = None

# 出力ディレクトリが存在しなければ作成
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 入力ディレクトリ内のすべての画像に対してトリミング処理を実行
for filename in os.listdir(input_dir):
    # 対応する拡張子を小文字でチェック (大文字小文字を区別しないように)
    if filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".avif")):
        input_path = os.path.join(input_dir, filename)
        # 出力ファイル名は元の拡張子に関わらず.avifにする
        output_filename = os.path.splitext(filename)[0] + ".avif"
        output_path = os.path.join(output_dir, output_filename)

        # 関数呼び出し時に target_size_kb を渡す
        trim_and_save_avif(input_path, output_path, trim_values, target_size_kb=target_size_kb)

print("\n--- トリミングとAVIF保存 処理が完了しました ---")