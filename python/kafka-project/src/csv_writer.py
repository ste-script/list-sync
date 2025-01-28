import csv
import uuid
import json


def write_to_file(json_data, file_name='./src/output.csv'):
    file_name = f'{file_name}_{uuid.uuid1()}.csv'
    json_data = json.loads(json_data)
    with open(file_name, 'a', newline='') as file:
        writer = csv.writer(file)
        
        # Extracting the header and row data from json_data
        header = ['action', 'table'] + [col['name'] for col in json_data['columns']]
        row = [json_data['action'], json_data['table']] + [col['value'] for col in json_data['columns']]
        
        # Write header if the file is empty
        if file.tell() == 0:
            writer.writerow(header)
        
        # Write the row data
        writer.writerow(row)

