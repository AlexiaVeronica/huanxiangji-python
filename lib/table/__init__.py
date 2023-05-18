from prettytable import PrettyTable


class Table:
    def __init__(self, table_header: list = None):
        self.table = PrettyTable()
        self.table_header = table_header
        if self.table_header is None:
            self.table_header = ["书名", "作者", "状态", "最后更新", "缓存章节数"]
        self.table.field_names = self.table_header

    def add_row(self, *row):
        if len(row) != len(self.table_header):
            raise Exception("row length not equal to table header")
        self.table.add_row(row)
        return self

    def add_rows(self, rows: list):
        if len(rows[0]) != len(self.table_header):
            raise Exception("row length not equal to table header")
        self.table.add_rows(rows)
        return self

    def print_table(self):
        print(self.table)
        return self
