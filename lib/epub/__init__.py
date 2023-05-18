import os
import uuid
import requests
from tqdm import tqdm
from ebooklib import epub


class EpubLib:

    def __init__(self, book_id, book_name, author_name):
        self.epub = epub.EpubBook()
        self.book_name = book_name
        self.epub.set_language('zh')
        self.epub.set_identifier(book_id)
        self.epub.set_title(book_name)
        self.epub.add_author(author_name)
        self.epub_toc_list = []

    def add_chapter(self, chapter_name, index, chapter_content):
        chapter_index = str(index).zfill(8)
        chapter = epub.EpubHtml(title=chapter_name, file_name=f'{chapter_index}.xhtml', lang='zh')
        chapter.content = "<h1>" + chapter_name + "</h1>" + \
                          "".join(["<p>" + line + "</p>" for line in chapter_content.split("\n")])
        self.epub.add_item(chapter)
        self.epub_toc_list.append(chapter)

    def set_cover(self, cover_url: str, cover_path: str):
        if not os.path.exists(cover_path):
            response = requests.get(cover_url, stream=True, timeout=100)
            file_size = int(response.headers.get('Content-Length', 0))
            with open(cover_path, 'wb') as f:
                with tqdm(total=file_size, unit='B', unit_scale=True, ncols=90, desc="下载封面") as progress_bar:
                    for data in response.iter_content(chunk_size=1024):
                        f.write(data)
                        progress_bar.update(len(data))

        self.epub.set_cover('image.jpg', open(cover_path, 'rb').read())

    def write_epub(self, output_path):
        self.epub.toc = tuple(self.epub_toc_list)
        self.epub.add_item(epub.EpubNcx())
        self.epub.add_item(epub.EpubNav())
        self.epub.spine = self.epub.toc
        epub.write_epub(output_path, self.epub, {})
