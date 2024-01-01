# https://gist.github.com/goldsborough/c973d934f620e16678bf
###########################################################################
#
## @file database.py
#
###########################################################################

import sqlite3


class Database:
    def __init__(self, name=None):
        self.conn = None
        self.cursor = None

        if name:
            self.open(name)

    def open(self, name):
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        try:
            self.conn = sqlite3.connect(name)
            self.conn.row_factory = dict_factory

            self.cursor = self.conn.cursor()

        except sqlite3.Error as e:
            print("Error connecting to database!")

    def close(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get(self, table, columns, limit=None, where=None, groupBy=None):
        query = "SELECT {0} from {1}".format(columns, table)

        if where:
            query += " WHERE {}".format(where)

        if groupBy:
            query += " GROUP BY {}".format(groupBy)

        query += ';'

        self.cursor.execute(query)

        # fetch data
        rows = self.cursor.fetchall()

        return rows[len(rows) - limit if limit else 0:]

    def getLast(self, table, columns):
        return self.get(table, columns, limit=1)[0]

    @staticmethod
    def toCSV(data, fname="output.csv"):
        with open(fname, 'a') as file:
            file.write(",".join([str(j) for i in data for j in i]))

    def write(self, table, columns, data):
        query = "INSERT INTO {0} ({1}) VALUES ({2});".format(
            table, columns, data)

        self.cursor.execute(query)

    def query(self, sql):
        self.cursor.execute(sql)

    @staticmethod
    def summary(rows):
        # split the rows into columns
        cols = [[r[c] for r in rows] for c in range(len(rows[0]))]

        # the time in terms of fractions of hours of how long ago
        # the sample was assumes the sampling period is 10 minutes
        t = lambda col: "{:.1f}".format((len(rows) - col) / 6.0)

        # return a tuple, consisting of tuples of the maximum,
        # the minimum and the average for each column and their
        # respective time (how long ago, in fractions of hours)
        # average has no time, of course
        ret = []

        for c in cols:
            hi = max(c)
            hi_t = t(c.index(hi))

            lo = min(c)
            lo_t = t(c.index(lo))

            avg = sum(c) / len(rows)

            ret.append(((hi, hi_t), (lo, lo_t), avg))

        return ret