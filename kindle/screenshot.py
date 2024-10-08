import argparse
import os
import time

import pyautogui as pag


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_page', help='開始ページ', type=int, required=True)
    parser.add_argument('-e', '--end_page', help='終了ページ', type=int, required=True)
    parser.add_argument('-o', '--output_dir', help='出力ディレクトリ', default='.')
    parser.add_argument('-c', '--chapter_name', help='章などの名前')

    return parser.parse_args()


def decide_capture_region(
    wait_sec: int = 5,
) -> tuple[int, int, int, int]:
    """スクショする範囲を決める"""
    print("カーソルをスクショしたい範囲の左上角に合わせてください")
    for sec in range(wait_sec, 0, -1):
        print(sec)
        time.sleep(1)
    x1, y1 = pag.position()
    print(f"左上の座標を({x1},{y1})にセットしました")

    print("カーソルをスクショしたい範囲の右下角に合わせてください")
    for sec in range(wait_sec, 0, -1):
        print(sec)
        time.sleep(1)
    x2, y2 = pag.position()
    print(f"右下の座標を({x2},{y2})にセットしました")

    return x1, y1, x2-x1, y2-y1


def capture_screen(
    start_page: int,
    end_page: int,
    image_dir: str,
    chapter_name: str,
    region: tuple[int, int, int, int],
):
    """スクショし画像として保存"""
    shot_span = 2
    next_page_key = 'right'

    print(region)

    # スクリーンの移動
    print("撮影したいウィンドウを選択してください")
    for sec in range(5, 0, -1):
        print(sec)
        time.sleep(1)

    # 実行
    print("撮影を始めます")
    for page in range(start_page, end_page+1):
        file_name = f"{chapter_name}_{page}.png" if chapter_name else f"{page}.png"
        s = pag.screenshot(region=region)
        s.save(f"{image_dir}/{file_name}")
        pag.keyDown(next_page_key)
        pag.keyUp(next_page_key)
        time.sleep(shot_span)
    print(f"画像を {image_dir} に保存しました")


def main():
    args = _parse_args()

    start_page = args.start_page
    end_page = args.end_page
    output_dir = args.output_dir
    chapter_name = args.chapter_name

    image_dir = output_dir + "/image"
    for dir in [output_dir, image_dir]:
        if not os.path.isdir(dir):
            os.mkdir(dir)

    # スクショする範囲を指定します
    # region = (左上のx座標, 左上のy座標, スクショの横幅, スクショの縦幅)
    region = decide_capture_region()

    capture_screen(start_page, end_page, image_dir, chapter_name, region)


if __name__ == "__main__":
    main()
