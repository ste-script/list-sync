import csv
import json


def write_to_file(json_data, file_name='./src/output.csv', consumer_id=''):
    file_name = f'{file_name}_{consumer_id}.csv'
    json_data = json.loads(json_data)
    with open(file_name, 'a', newline='') as file:
        writer = csv.writer(file)

        if json_data['action'] == 'I' or json_data['action'] == 'U':
            header = ['action', 'table'] + [col['name']
                                            for col in json_data['columns']]
            row = [json_data['action'], json_data['table']] + \
                [col['value'] for col in json_data['columns']]
        else:
            return

        # Write header if the file is empty
        if file.tell() == 0:
            writer.writerow(header)

        # Write the row data
        writer.writerow(row)
