import csv
import json


class CsvWriter:

    def write_to_file(self, json_data: str, file_name='./test/data/output', consumer_id='', split_updates=True, split_files=True):
        self.filename = file_name
        self.consumer_id = consumer_id
        json_data = json.loads(json_data)
        action = json_data['action']
        if action == 'U':
            if split_updates:
                self.split_update(json_data)
                return
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
        self.write_action(row, 'U', 'columns')

    def split_update(self, row):
        self.write_delete(row)
        self.write_insert(row)

    def write_insert(self, row):
        self.write_action(row, 'I', 'columns')

    def write_delete(self, row):
        self.write_action(row, 'D', 'identity')

    def write_action(self, row, action, columns_name):
        if action == 'D':
            filename = self.filename + self.consumer_id + '_delete.csv'
            self.check_and_write_header(row, filename)
        else:
            filename = self.filename + self.consumer_id + '_insert.csv'
            self.check_and_write_header(row, filename)
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            row1 = [action]+[row['table']] + [col['value']
                                              for col in row[columns_name]]
            writer.writerow(row1)
