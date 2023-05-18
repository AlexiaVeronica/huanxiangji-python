# Novel Downloader

Novel Downloader is a Python program for downloading novels. It supports downloading novels from `www.huanxiangji.com` and other online libraries, as well as providing database management functions.

## Installation

1. Download the code.

```shell
$ git clone https://github.com/username/novel-downloader.git
```

2. Install dependencies.

```shell
$ pip install -r requirements.txt
```

## Usage

### Command Line Parameters

The following are the available command line parameters for Novel Downloader:

```shell
usage: python main.py <command> [<args>] [-h|--help]

Novel Downloader

optional arguments:
  -h, --help            show this help message and exit
  -o file_name, --output file_name
                        save to local file name (default: novel)
  -t threads_num, --thread threads_num
                        number of threads (default: 16)
  -e, --epub            generate an epub file (default: False)
  -m, --merge           do not merge local chapters (default: True)

sub-commands:
  download              download novel
    -i book_id          book id

  database              database operations
    -i book_id          book id
    -s keyword          search books
    -u                  update book
```

### Downloading Novels

```python
python main.py download -i book_id
```

book_id: The unique identifier of the book. For example, ``1234`` in ``https://www.huanxiangji.com/book/1234``.

The downloaded novel will be saved in a file named ``novel.txt`` in the same directory as the program.

### Database Management

```python
python main.py database [-i book_id] [-s keyword] [-u]
```

- search books: ``python main.py database -s keyword``
- update book: ``python main.py database -i book_id -u``

### Other Parameters

- save to local file name: ``-o file_name`` or ``--output file_name``
- number of threads: ``-t threads_num`` or ``--thread threads_num``
- generate an epub file: ``-e`` or ``--epub``
- do not merge local chapters: ``-m`` or ``--merge``

## License

The source code is licensed under the MIT License. Please see the `LICENSE` file for details.