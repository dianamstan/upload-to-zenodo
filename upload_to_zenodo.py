import json
import requests
import os
import codecs

def upload(metadata, pdf_path, file_to_upload, sandbox: True):
    base_url = "https://sandbox.zenodo.org" if sandbox else "https://zenodo.org"

    if not _is_valid_json(metadata):
        return
    headers = {"Content-Type": "application/json"}

    params = {'access_token': token}
    response = requests.post(f'{base_url}/api/deposit/depositions', params=params, json={})
    deposition_id = json.loads(response.text)["id"]
    if response.status_code > 210:
        print(f"Error happened during submission, status code: {response.status_code}")
        return

    bucket_url = response.json()["links"]["bucket"]

    with open(pdf_path, "rb") as fp:
        r = requests.put(
            "%s/%s" % (bucket_url, pdf_path.split("/")[-1]),
            data=fp,
            params=params
        )
    if r.status_code > 210:
        print("Error occurred during file upload, status code: " + str(r.status_code) + str(r.reason))
        return

    metadata_response = requests.put(
        f'{base_url}/api/deposit/depositions/%s' % deposition_id,
        params={'access_token': token},
        data=metadata,
        headers=headers
    )
    if metadata_response.status_code > 210:
        print(f"Error occurred during metadata upload, status code: "
              f"{metadata_response.status_code} {metadata_response.text}")
        if metadata_response.status_code == 500:
            with open("timeouts.txt", "a") as file:
                file.write(f"{file_to_upload}\n")
        elif metadata_response.status_code == 400:
            with open("bad_metadata.txt", "a") as file:
                file.write(f"{file_to_upload} has error {metadata_response.text}\n")
        return

    print("{file} submitted with submission ID = {id} (DOI: 10.5281/zenodo.{id})".format(file=pdf_path,id=deposition_id))

    publish_response = requests.post(
        f'{base_url}/api/deposit/depositions/%s/actions/publish' % deposition_id, params={'access_token': token}
    )
    if publish_response.status_code > 210:
        print(f"Error occurred during publishing, status code: {publish_response.status_code} {publish_response.text}")
    print("{file} published with submission ID = {id} (DOI: 10.5281/zenodo.{id})".format(file=pdf_path,id=deposition_id))


def batch_upload(directory, file: None, sandbox: True):
    files = os.listdir(directory) if file is None else list(filter(lambda x: x.startswith(file), os.listdir(directory)))
    for metadata_file in files:
        metadata_file = os.path.join(directory, metadata_file)
        if metadata_file.endswith(".json"):
            pdf_file = metadata_file.replace(".json",".pdf")
            if os.path.isfile(pdf_file):
                print("Uploading %s & %s" % (metadata_file, pdf_file))
                with codecs.open(metadata_file, 'r', 'utf-8') as f:
                    metadata = f.read()
                    metadata_json = json.loads(metadata)
                    file_to_upload = metadata_json['metadata']['filename']
                    metadata = json.dumps(metadata_json, ensure_ascii=True)
                upload(metadata, pdf_file, file_to_upload, sandbox)
            else:
                print("The file %s might be a submission metadata file, but %s does not exist." % (metadata_file, pdf_file))
           
           
def _is_valid_json(text):
    try:
        json.loads(text)
        return True
    except ValueError as e:
        print('Invalid json: %s' % e)
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Usage: upload_to_zenodo.py <token> <directory> <optional: file>."
                                                 " The directory contains .json metadata descriptors and .pdf files.")
    parser.add_argument("-t", "--token", type=str, help="zenodo api token")
    parser.add_argument("-d", "--directory", type=str, help="directory with metadata and pdfs")
    parser.add_argument("-f", "--file", type=str, help="optionally upload just one file")
    parser.add_argument("-s", "--sandbox", type=str, help="optionally test against sandbox")

    args = parser.parse_args()

    # TOKEN = args.token
    directory = args.directory
    file = args.file if args.file else None
    if not os.path.isdir(directory):
        print("Invalid directory.")
        exit()
    sandbox = True if args.sandbox in ("true", "True", "t") else False

    batch_upload(directory, file, sandbox)

# if __name__ == "__main__":
#     batch_upload("/Users/dianastan/tapeworm/", "Petavy_etal_1984", False)
