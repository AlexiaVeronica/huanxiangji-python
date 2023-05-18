from .model import Book, Chapter


def get_cache_chapter_by_book_id(book_id):
    return Chapter.select().where(Chapter.book_id == book_id)


def get_cache_chapter_by_chapter_id(chapter_id):
    return Chapter.get_or_none(Chapter.chapter_id == chapter_id)


def get_cache_book_info_by_book_id(book_id):
    return Book.get_or_none(Book.book_id == book_id)


def get_cache_book_info_by_like_book_name(book_name):
    result = Book.select().where(Book.book_name.contains(book_name))
    if result:
        return result
    print(f"not found book info by like book name in database for {book_name}")
    return []
