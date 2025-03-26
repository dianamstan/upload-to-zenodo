import sys
import csv
import os.path
import json
import ast

def safe_json_conversion(value, output_filename):
    try:
        python_obj = ast.literal_eval(value)
        return json.loads(json.dumps(python_obj))
    except (SyntaxError, ValueError) as e:
        print(f"{value} had error {e} in file {output_filename}")
        return value

def create_json(metadata_filename, file: None):
    from iso639 import Lang

    with open(metadata_filename,"r", encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        path = '/Users/dianastan/tapeworm'
        for row in csv_reader:
            if file is not None:
                if row['filename'] != file:
                    continue
            output_filename = f'{path}/{row["filename"]}'.strip('.pdf') + '.json'
            output_dict = {}

            for column in csv_reader.fieldnames:
                field_value = row[column].strip()
                if field_value == "" or field_value is None:
                    continue
                if column in ('title', 'description', 'journal_title'):
                    output_dict[column] = field_value
                elif column == 'language':
                    lang = Lang(field_value)
                    output_dict[column] = lang.pt3 if field_value in (lang.pt2b, lang.pt2t) else field_value
                elif column == 'publication_type':
                    output_dict[column] = 'other' if field_value == 'presentation' else field_value
                else:
                    output_dict[column] = safe_json_conversion(field_value, output_filename) if \
                        field_value.startswith('[') else field_value
            output_dict['custom'] = {
                'dwc:otherCatalogNumbers': [output_dict['CITATION_ID']],
                'dwc:kingdom': ['Animalia'],
                'dwc:phylum': ['Platyhelminthes'],
                'dwc:class': ['Cestoda'],
                'dwc:order': ['Cyclophyllidea'],
                'dwc:family': ['Taeniidae'],
                'dwc:genus': ['Echinococcus'],
                'dwc:specificEpithet': ['multilocularis'],
                'dwc:scientificName': ['Echinococcus multilocularis'],
            }

            print("Writing %s..." % output_filename)
            try:
                with open(output_filename, "w", encoding='utf-8') as output_file:
                    json.dump({'metadata': output_dict}, output_file, indent=4)
            except FileNotFoundError:
                os.mkdir(path)
                with open(output_filename, "w", encoding='utf-8') as output_file:
                    json.dump({'metadata': output_dict}, output_file, indent=4)
                
if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print("Usage: create_json.py <metadata_filename>")
    #     exit()
    #
    # metadata_filename = sys.argv[1] # e.g. "data.csv"
    # if not os.path.isfile(metadata_filename):
    #     print("Invalid metadata filename.")
    #     exit()

    import argparse

    parser = argparse.ArgumentParser(description="Usage: create json metadata files from csv file.")
    parser.add_argument("-m", "--metadata_csv_filename", type=str)
    parser.add_argument("-f", "--file", type=str, help="optionall create json for just one file")

    args = parser.parse_args()

    metadata_filename = args.metadata_csv_filename
    file = args.file if args.file else None
    if not os.path.isfile(metadata_filename):
        print("Invalid metadata filename.")
        exit()

    create_json(metadata_filename, file)