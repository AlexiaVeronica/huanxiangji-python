from peewee import SqliteDatabase, Model, IntegerField, CharField, TextField, AutoField

db = SqliteDatabase('data.db')


class BaseModel(Model):
    class Meta:
        database = db


class Chapter(BaseModel):
    """章节"""
    id = AutoField(primary_key=True, unique=True, index=True)
    book_id = IntegerField()
    chapter_id = IntegerField()
    chapter_name = CharField()
    chapter_url = CharField()
    chapter_content = TextField()

    class Meta:
        table_name = 'chapter'


class Book(BaseModel):
    """书籍"""
    id = AutoField(primary_key=True, unique=True, index=True)
    book_id = IntegerField()
    book_name = CharField()
    book_author = CharField()
    book_state = CharField()
    book_update = CharField()
    book_introduce = TextField()
    book_img = CharField()

    class Meta:
        table_name = 'book'


# create

db.connect()
db.create_tables([Book, Chapter])

# insert

# Book.create(book_id=1, book_name='test', book_author='test', book_state='test', book_update='test',
