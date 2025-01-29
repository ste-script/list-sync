import csv
import json


def write_to_file(json_data: str, file_name='./src/output.csv', consumer_id='', split_updates=True, split_files=False):
    file_name = f'{file_name}_{consumer_id}.csv'
    json_data = json.loads(json_data)
    with open(file_name, 'a', newline='') as file:
        writer = csv.writer(file)
        action = json_data['action']
        if file.tell() == 0:
            write_header(json_data, writer)

        if action == 'U':
            if split_updates:
                split_update(json_data, writer)
                return
            write_update(json_data, writer)
            return

        if action == 'D':
            write_delete(json_data, writer)
            return

        if action == 'I':
            write_insert(json_data, writer)
            return


def write_header(json_data, writer):
    if json_data['action'] != 'I':
        header = ['action', 'table'] + [col['name']
                                        for col in json_data['identity']]
    else:
        header = ['action', 'table'] + [col['name']
                                        for col in json_data['columns']]
    writer.writerow(header)


def write_update(row, writer):
    write_action(row, writer, 'U', 'columns')


def split_update(row, writer):
    write_delete(row, writer)
    write_insert(row, writer)


def write_insert(row, writer):
    write_action(row, writer, 'I', 'columns')


def write_delete(row, writer):
    write_action(row, writer, 'D', 'identity')


def write_action(row, writer, action, columns_name):
    row1 = [action]+[row['table']] + [col['value']
                                      for col in row[columns_name]]
    writer.writerow(row1)
