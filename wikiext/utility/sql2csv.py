import csv
import codecs
import sys

csv.field_size_limit(2 ** 16)


def is_insert(line):
    return line.startswith('INSERT INTO') or False


def get_values(line):
    return line.partition('` VALUES ')[2]


def values_sanity_check(values):
    assert values
    assert values[0] == '('
    return True


def parse_values(values):
    latest_row = []

    reader = csv.reader([values], delimiter=',',
                        doublequote=False,
                        escapechar='\\',
                        quotechar="'",
                        strict=True
                        )

    for reader_row in reader:
        for column in reader_row:
            if len(column) == 0 or column == 'NULL':
                latest_row.append(chr(0))
                continue
            if column[0] == "(":
                new_row = False
                if len(latest_row) > 0:
                    if latest_row[-1][-1] == ")":
                        latest_row[-1] = latest_row[-1][:-1]
                        new_row = True
                if new_row:
                    yield latest_row
                    latest_row = []
                if len(latest_row) == 0:
                    column = column[1:]
            latest_row.append(column)
        if latest_row[-1][-2:] == ");":
            latest_row[-1] = latest_row[-1][:-2]
            yield latest_row


def sql2csv(input_file):
    with codecs.open(input_file, 'r', encoding='utf-8', errors='ignore') as inputfile:
        try:
            for line in inputfile.readlines():
                if is_insert(line):
                    values = get_values(line)
                    if values_sanity_check(values):
                        yield parse_values(values)
        except KeyboardInterrupt:
            sys.exit(0)
