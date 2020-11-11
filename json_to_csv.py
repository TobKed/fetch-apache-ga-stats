import json
import csv

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Input file name", required=True)
parser.add_argument("-o", "--output", help="Output file name", required=True)
parser.add_argument("-a", "--additional_data", help="Additional data in form of json")

args = parser.parse_args()
json_filename = args.input
csv_filename = args.output
additional_data = args.additional_data
if additional_data is not None:
    additional_data = json.loads(additional_data)


def flatten_json(y):
    out = {}

    def flatten(x, name=""):
        # pull_requests may vary in length
        # it mess with csv headers
        if name == "pull_requests.":
            out[name[:-1]] = x
        elif type(x) is dict:
            for a in x:
                flatten(x[a], name + a + ".")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + ".")
                i += 1
        else:
            if isinstance(x, str):
                x = x.replace('\n', '\\n').replace('\r', '\\r')
            out[name[:-1]] = x

    flatten(y)
    return out


def get_flattened_json_array(filename):
    with open(filename) as json_file:
        flattened_json_array = [flatten_json(i) for i in json.load(json_file)]
        return flattened_json_array


def save_csv(filename, data, additional_data=None):
    if additional_data is None:
        additional_data = {}
    with open(filename, mode="w") as csv_file:
        fieldnames = list(data[0].keys()) + list(additional_data.keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        for d in data:
            writer.writerow({**d, **additional_data})


data = get_flattened_json_array(json_filename)
save_csv(csv_filename, data, additional_data)
