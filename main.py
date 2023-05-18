import book
from config import Vars
import argparse
from lib import database, table


def shell_parser():
    parser = argparse.ArgumentParser(
        description='小说下载器',
        usage='python main.py <command> [<args>] [-h|--help]',
        epilog='welcome to use novel downloader, if you have any questions, please submit issues on Github',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('-o', '--output', default="novel", metavar='file_name', help='保存到本地文件名')
    parser.add_argument('-t', '--thread', default=16, type=int, metavar='threads_num', help='线程数')
    parser.add_argument('-e', '--epub', default=False, action='store_true', help='生成epub文件')
    parser.add_argument('-m', '--merge', default=True, action='store_false', help='不合并本地章节')

    subparsers = parser.add_subparsers(help='子命令', dest='command')
    download_command = subparsers.add_parser('download', help='下载小说')
    download_command.add_argument('-i', '--id', type=str, metavar='book_id', required=True, help='书籍id')
    database_command = subparsers.add_parser('database', help='数据库操作')
    database_command.add_argument('-i', '--id', type=str, metavar='book_id', help='书籍id')
    database_command.add_argument('-s', '--search', type=str, metavar='keyword', help='搜索书籍')
    database_command.add_argument('-u', '--update', default=False, action='store_true', help='更新书籍')

    args = parser.parse_args()

    # 配置检查及处理
    Vars.cf.set_value("output", args.output)
    Vars.cf.set_value("thread", args.thread)
    Vars.cf.set_value("merge", args.merge)
    Vars.cf.set_value("epub", args.epub)

    if not args.command:
        parser.error('请提供一个子命令')
    elif args.command == 'database' and not (args.id or args.search):
        parser.error('请提供书籍id或关键字')

    return args


def shell_download_book(book_id):
    book.Book().init_book_info(book_id).create_file().get_context().merge_local_chapter()


def main():
    args = shell_parser()
    if args.command == "download" and args.id is not None:
        shell_download_book(args.id)

    elif args.command == "database":
        table_init = table.Table()
        if args.id is not None:
            result = database.get_cache_book_info_by_book_id(args.id)
            if result:
                table_init.add_row(result.book_name, result.book_author, result.book_state, result.book_update,
                                   database.get_cache_chapter_by_book_id(result.book_id).count()).print_table()
            else:
                print("没有找到书籍信息,请先下载!")
        elif args.search is not None:
            table_init.add_rows([
                [
                    item.book_name, item.book_author, item.book_state, item.book_update,
                    database.get_cache_chapter_by_book_id(item.book_id).count()
                ] for item in database.get_cache_book_info_by_like_book_name(args.search)
            ]).print_table()
        elif args.update:
            for item in database.Book.select():
                shell_download_book(item.book_id)
        else:
            print("please input id or search keyword to search book info")


if __name__ == '__main__':
    main()
