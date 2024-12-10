# Kindle Screenshot to PDF

このプロジェクトは、Kindleのスクリーンショットを撮影し、それらを1つのPDFファイルとして保存するツールです。

## 必要なライブラリ

以下のPythonライブラリが必要です

- fpdf
- pyautogui

インストールするには、以下のコマンドを実行してください

```sh
pip install fpdf pyautogui
```

## ファイルの説明

- `exec_all.py`: スクリーンショットを撮影し、それらをPDFに変換するメインスクリプト。
- `screenshot.py`: スクリーンショットを撮影するスクリプト。
- `image2pdf.py`: 画像をPDFに変換するスクリプト。


## 使い方

### スクリーンショットを撮影してPDFに変換する

`exec_all.py`を実行します。   
実行されるとカーソルを合わせるなど指示が出るのでそれに従ってください

```sh
python kindle/exec_all.py -s <開始ページ> -e <終了ページ> -o <出力ディレクトリ> -c <章の名前>
```

例：

```sh
python kindle/exec_all.py -s 1 -e 10 -o ./output -c "Chapter1"
```

### スクリーンショットを撮影する

`screenshot.py`を実行します。

```sh
python kindle/screenshot.py -s <開始ページ> -e <終了ページ> -o <出力ディレクトリ> -c <章の名前>
```

例：

```sh
python kindle/screenshot.py -s 1 -e 10 -o ./output -c "Chapter1"
```

### 画像をPDFに変換するだけ

`image2pdf.py` を実行します。

```sh
python kindle/image2pdf.py -s <開始ページ> -e <終了ページ> -o <出力ディレクトリ> -c <章の名前>
```

例：

```sh
python kindle/image2pdf.py -s 1 -e 10 -o ./output -c "Chapter1"
```
