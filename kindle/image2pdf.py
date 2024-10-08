import argparse
import os

from fpdf import FPDF, Align


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_page', help='開始ページ', type=int, required=True)
    parser.add_argument('-e', '--end_page', help='終了ページ', type=int, required=True)
    parser.add_argument('-o', '--output_dir', help='出力ディレクトリ', default='.')
    parser.add_argument('-c', '--chapter_name', help='章などの名前')

    return parser.parse_args()


def image_to_pdf(
    start_page: int,
    end_page: int,
    output_dir: str,
    chapter_name: str,
):
    """複数の画像を1つのPDFとして保存"""
    print("画像をPDFに変換します")
    pdf = FPDF()
    pdf.set_auto_page_break(False) # これをつけないと勝手に次のページが作られて空白ページができてしまう
    for page in range(start_page, end_page+1):
        image = f"{output_dir}/image/{chapter_name}_{page}.png" if chapter_name else f"{output_dir}/image/{page}.png"
        pdf.add_page()
        pdf.image(image, x=Align.C) # w=pdf.ephなどでフルサイズ指定できる
    pdf_path = f"{output_dir}/pdf/{chapter_name}_{start_page}_{end_page}.pdf" \
            if chapter_name else f"{output_dir}/pdf/{start_page}_{end_page}.pdf"
    pdf.output(pdf_path)
    print(f"PDFを {pdf_path} に保存しました")


def main():
    args = _parse_args()

    start_page = args.start_page
    end_page = args.end_page
    output_dir = args.output_dir
    chapter_name = args.chapter_name

    pdf_dir = output_dir + "/pdf"
    for dir in [output_dir, pdf_dir]:
        if not os.path.isdir(dir):
            os.mkdir(dir)

    image_to_pdf(start_page, end_page, output_dir, chapter_name)


if __name__ == "__main__":
    main()
