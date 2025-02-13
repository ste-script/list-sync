import csv
import json
import sys


class CsvWriter:

    def __init__(self, filename='./test/data/output', consumer_id='', split_files=True):
        self.consumer_id = consumer_id
        self.split_files = split_files
        if len(consumer_id) > 0:
            self.filename = filename + '_' + consumer_id
        else:
            self.filename = filename

    def write(self, json_data: str):
        json_data = json.loads(json_data)
        action = json_data['action']
        if action == 'U':
            self.write_update(json_data)
            return

        if action == 'D':
            self.write_delete(json_data)
            return

        if action == 'I':
            self.write_insert(json_data)
            return

    def check_and_write_header(self, json_data, file_name):
        with open(file_name, 'a', newline='') as file:
            if file.tell() != 0:
                return
            writer = csv.writer(file)
            if json_data['action'] != 'I':
                header = ['action', 'table'] + [col['name']
                                                for col in json_data['identity']]
            else:
                header = ['action', 'table'] + [col['name']
                                                for col in json_data['columns']]
            writer.writerow(header)

    def write_update(self, row):
        self.write_delete(row)
        self.write_insert(row)

    def write_insert(self, row):
        self.write_action(row, 'I', 'columns')

    def write_delete(self, row):
        self.write_action(row, 'D', 'identity')

    def write_action(self, row, action, columns_name):
        if self.split_files:
            if action == 'D':
                filename = self.filename + '_delete.csv'
            else:
                filename = self.filename + '_insert.csv'
        else:
            filename = self.filename + '.csv'

        self.check_and_write_header(row, filename)
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            row1 = [action]+[row['table']] + [col['value']
                                              for col in row[columns_name]]
            writer.writerow(row1)
