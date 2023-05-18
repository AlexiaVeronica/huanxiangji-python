import os
import re
from config import Vars
from tqdm import tqdm
from lib import request, database, epub
from concurrent.futures import ThreadPoolExecutor


class Book:
    def __init__(self):
        self.book_info = None
        self.book_id = None
        self.introduce = ""
        self.add_database_list = []
        self.get_database_list = {}
        self.requests_model = request.RequestsWithRetry()

    def init_book_info(self, book_id: str):
        self.book_id = str(book_id)
        self.book_info = BookInfo(self.book_id, requests_model=self.requests_model)

        if database.get_cache_book_info_by_book_id(book_id) is None:
            self.book_info.database_book_info().save()
        return self

    def create_file(self):
        if not os.path.exists(os.path.join(Vars.cf.get_value("output"), self.book_info.book_name)):
            os.makedirs(os.path.join(Vars.cf.get_value("output"), self.book_info.book_name))

        self.show_book_information()
        with open(self.book_info.out_put_path, "w", encoding="utf-8") as file:
            file.write(self.introduce)
        return self

    def show_book_information(self):
        self.introduce += "书名：{}\n".format(self.book_info.book_name)
        self.introduce += "作者：{}\n".format(self.book_info.book_author)
        self.introduce += "状态：{}\n".format(self.book_info.book_state)
        self.introduce += "最后更新：{}\n".format(self.book_info.book_update)
        print("书籍详细:\n" + self.introduce, "\n")

    def download_chapter(self, catalogue):
        chapter_id = catalogue["chapter_id"]
        result = database.get_cache_chapter_by_chapter_id(chapter_id)
        if not result:
            content_text = self.requests_model.get_chapter(self.book_id, chapter_id)
            if content_text:
                result = database.Chapter(
                    book_id=self.book_id,
                    chapter_id=chapter_id,
                    chapter_name=catalogue["chapter_name"],
                    chapter_url=f"{self.book_id}/{chapter_id}",
                    chapter_content='\n'.join(
                        ["　　" + line.replace('&nbsp;', '').replace(" ", "").strip() for line in
                         re.sub(re.compile('<.*?>'), '', content_text).split("\n") if line.strip() != '']
                    ),
                )
                self.add_database_list.append(result)
                self.get_database_list[chapter_id] = result
            else:
                print("章节:{}下载失败!".format(catalogue["chapter_name"]))
        else:
            self.get_database_list[chapter_id] = result

    def get_context(self):
        if not self.book_info.book_catalogue:
            raise Exception("没有提取到章节信息,请先调用get_catalogue方法!")
        # for catalogue in self.catalogue_list:
        #     self.download(catalogue)
        with ThreadPoolExecutor(max_workers=Vars.cf.get_value("thread")) as executor:
            pools = []
            for catalogue in self.book_info.book_catalogue:
                pools.append(executor.submit(self.download_chapter, catalogue))
            for future in tqdm(pools, total=len(pools), desc="下载进度", ncols=90):
                future.result()
        for chapter in self.add_database_list:
            chapter.save()

        return self

    def merge_local_chapter(self):
        epub_init = epub.EpubLib(self.book_id, self.book_info.book_name, self.book_info.book_author)
        if not Vars.cf.get_value("merge"):
            return self
        with open(self.book_info.out_put_path, 'a', encoding='utf-8') as file_text:

            if self.book_info.book_img.find('nocover') == -1:
                epub_init.set_cover(self.book_info.book_img, self.book_info.out_put_path.replace(".txt", ".jpg"))
                self.introduce = f'<img src="image.jpg" alt="{self.book_info.book_name}"/>\n' + self.introduce
            epub_init.add_chapter("简介", "0", "".join(["<p>" + line + "</p>" for line in self.introduce.split("\n")]))

            for index, catalogue in enumerate(self.book_info.book_catalogue, start=1):
                result: database.Chapter = self.get_database_list.get(catalogue["chapter_id"])
                if result:
                    epub_init.add_chapter(result.chapter_name, index, result.chapter_content)
                    file_text.write("\n\n" + result.chapter_name + "\n" + result.chapter_content)
            epub_init.write_epub(self.book_info.out_put_path.replace(".txt", ".epub"))
            print(self.book_info.book_name, "本地缓存文件合并完毕")

        return self


class BookInfo:
    def __init__(self, book_id, requests_model):
        self.book_id = book_id
        self.book_info = requests_model.get_book_info(book_id)
        if not self.book_info:
            raise Exception("书籍信息获取失败!")

    @property
    def book_name(self):
        book_name_ = self.book_info.xpath("/html/body/div[3]/div[1]/div/div/div[2]/div[1]/h1/text()")
        return re.sub(r'[\\/:*?"<>|\r\n]+', "", book_name_.get())

    @property
    def book_author(self):
        book_author_ = self.book_info.xpath("/html/body/div[3]/div[1]/div/div/div[2]/div[1]/div/p[1]/text()")
        return book_author_.get().replace("作者：", "")

    @property
    def book_state(self):
        book_state_ = self.book_info.xpath("/html/body/div[3]/div[1]/div/div/div[2]/div[1]/div/p[3]/text()")
        return book_state_.get().replace("状态：", "")

    @property
    def book_update(self):
        book_update_ = self.book_info.xpath("/html/body/div[3]/div[1]/div/div/div[2]/div[1]/div/p[5]/text()")
        return book_update_.get().replace("最后更新：", "")

    @property
    def book_introduce(self):
        book_introduce_ = self.book_info.xpath("/html/body/div[3]/div[1]/div/div/div[3]/div/text()").getall(),
        return "\n".join(book_introduce_)

    @property
    def book_img(self):
        return self.book_info.xpath("/html/body/div[3]/div[1]/div/div/div[1]/img/@src").get()

    @property
    def book_catalogue(self):
        catalogue_name = self.book_info.xpath('//*[@id="section-list"]/li/a/text()').getall()
        catalogue_url = self.book_info.xpath('//*[@id="section-list"]/li/a/@href').getall()
        catalogue_list = []
        for index, catalogue_info in enumerate(list(zip(catalogue_url, catalogue_name)), start=1):
            catalogue_list.append({
                "chapter_index": index,
                "chapter_id": catalogue_info[0],
                "chapter_name": catalogue_info[1]
            })
        return catalogue_list

    @property
    def out_put_path(self):
        return os.path.join(os.getcwd(), Vars.cf.get_value("output"), self.book_name, self.book_name + ".txt")

    def database_book_info(self) -> database.Book:
        return database.Book(
            book_id=self.book_id,
            book_name=self.book_name,
            book_author=self.book_author,
            book_state=self.book_state,
            book_update=self.book_update,
            book_introduce=self.book_introduce,
            book_img=self.book_img
        )
