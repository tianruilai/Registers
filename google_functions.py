import re
import json
from google.cloud import storage
import os, json, time
from datetime import date
import re
import pandas as pd
from google.cloud import vision



os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\87208\Documents\Documents\RA\Social register\key2.json"

# Underline: a variable is tempt, not important
def output_creator(City: str, Year: str):


    def async_detect_document(gcs_source_uri, gcs_destination_uri):
        # triple quotes 1）allowing for changing lines and special symbols 2) can be used to annotate functions but they are sting literals not comments, and might break the loop if not indent correctly
        """OCR with PDF/TIFF as source files on GCS"""
        import json
        import re
        from google.cloud import vision
        from google.cloud import storage
        
        # global variables defined outside the function and useful throughout the program
        global response
        global annotation

        # Supported mime_types are: 'application/pdf' and 'image/tiff'
        # type-subtype, https://www.iana.org/assignments/media-types/media-types.xhtml
        mime_type = 'application/pdf'

        # How many pages should be grouped into each json output file.
        # Maximum batch_size is 100, a.k.a 100 pages in each JSON output file
        batch_size = 100

        client = vision.ImageAnnotatorClient()

        feature = vision.Feature(
            type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

        gcs_source = vision.GcsSource(uri=gcs_source_uri)
        input_config = vision.InputConfig(
            gcs_source=gcs_source, mime_type=mime_type)

        gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
        output_config = vision.OutputConfig(
            gcs_destination=gcs_destination, batch_size=batch_size)

        async_request = vision.AsyncAnnotateFileRequest(
            features=[feature], input_config=input_config,
            output_config=output_config)

        operation = client.async_batch_annotate_files(
            requests=[async_request])

        print('Waiting for the operation to finish.')
        # Stop the operator if it takes too long
        operation.result(timeout=1000)

        # Once the request has completed and the output has been
        # written to GCS, we can list all the output files.
        storage_client = storage.Client()
        
        # r'': claim that use the original literals(字符); 'gs://([^/]+)/(.+)' for all the files under the directory(遍历路径中的文件)
        match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
        bucket_name = match.group(1)
        prefix = match.group(2)

        bucket = storage_client.get_bucket(bucket_name)

        # List objects with the given prefix, filtering out folders.
        blob_list = [blob for blob in list(bucket.list_blobs(
            prefix=prefix)) if not blob.name.endswith('/')]
        print('Output files:')
        for blob in blob_list:
            print(blob.name)

        # Process the first output file from GCS.
        # Blob_list is the dictioanry of output blobs. Since we specified batch_size=2, the first response contains the first two pages of the input file.
        output = blob_list[0]

        json_string = output.download_as_string()
        response = json.loads(json_string)

        # The actual response for the first page of the input file.
        # Responses is one of the element in the dictionary, so is fullTexAnnotation
        try:
            first_page_response = response['responses'][0]
            annotation = first_page_response['fullTextAnnotation']
            print('Full text:\n')
            print(annotation['text'])
        except:
            pass

        # Here we print the full text from the first page.
        # The response contains more information:
        # annotation/pages/blocks/paragraphs/words/symbols
        # including confidence scores and bounding boxes


    gcs_source_uri = 'gs://registers-pdf/'+City + ' ' + Year +'.pdf'
    gcs_destination_uri = 'gs://registers-output/'+City + ' ' + Year +'text_output'
    
###Execute the function async_detect_document
    async_detect_document(gcs_source_uri, gcs_destination_uri)


for pdfpath,pdfdirs,pdffiles in os.walk(r"C:\Users\87208\Documents\Documents\RA\Social register\pdf_input"):
    for pdf in pdffiles:
        City = re.findall(r"[A-z ]+(?= [0-9])", pdf)[0]
        Year = re.findall(r"[0-9]+", pdf)[0]
        print(City, Year)
        output_creator(City, Year)

# Underline: a variable is tempt, not important
def text_creator(City: str, Year: str):

    ###Download and convert to txt
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'C:\Users\87208\Documents\Documents\RA\Social register\key2.json'
    storage_client = storage.Client.from_service_account_json(r'C:\Users\87208\Documents\Documents\RA\Social register\key2.json')

    # TODO: SPECIFY THE PATHS
    # bucket_name (folder) and file (what does it start with) refer to the documents on Google Storage
    # folder is the download location on your computer,

    bucket_name = 'registers-output'

    folder = r"C:/Users/87208/Documents/Documents/RA/Social register/json_output"
    delimiter = '/'

    # STEP 1: WE DOWNLOAD ALL OUTPUT FILES FROM GOOGLE STORAGE API

    # Retrieve all blobs with a prefix matching the file.
    bucket = storage_client.get_bucket(bucket_name)
    # List blobs iterate in folder;  prefix to filter blobs, delimiter to emulate hierachy
    # Excluding folder inside bucket, stop and star a new one after '/'
    blobs = bucket.list_blobs(delimiter=delimiter)
    for blob in blobs:
        print(blob.name)
        destination_uri = '{}/{}'.format(folder, blob.name)
        blob.download_to_filename(destination_uri)


    # STEP 2: LOAD THEM HERE
    #Set a format string: the string is evaluated at run time
    path_to_json = f'{folder}'
    #Scrape josn data from json files, output is string
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    #Sort the documents by order
    json_files = sorted(json_files)
    #No space in the document name here
    json_files = [j for j in json_files if City in j and Year in j]
    print(json_files)

    import json

    text_per_page_list = []
    recognised_output_list = []

    page_index = 0
    #Load the json files
    for file in json_files:

        current_file = open(f'{folder}/{file}', errors="ignore")
        file_to_dict = json.load(current_file)

        pages = file_to_dict['responses']

        for page in pages:
            content = page['fullTextAnnotation']
            recognised_output = content['text']
            # print(" ")
            print(f"---------------- PAGE {page_index} IN PROGRESS ----------------")
            # print(recognised_output)
            text_per_page_list.append(recognised_output)
            page_index += 1
            #Not every page has recognized output



    print(" ")
    print(f"--- DONE! WE HAVE {page_index} PAGES IN TOTAL ---")
    print(" ")
    # print(text_per_page_list)
    print(len(text_per_page_list))


    # DURING TS LECTURE, GRABS PARANTHESES AND SINGLE CAPITAL
    # FAILS WHEN THERE ARE TWO NAMES FOR A SINGLE PERSON

    # CREATES THE OCR OUTPUT

    f = open("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\text_output\\"+City+" "+Year+".txt", "w")

    __ = 0
    f.write(f" FILE CREATED ON {date.today()}")
    for page in text_per_page_list:
        f.write(f"------------ PAGE {__ + 1} ------------")
        f.write("\n")
        f.write(page)
        f.write("\n")
        __ += 1
        print("------------------------------------------")
        print(f"Loop count is currently {__}")
    print("Done")

for pdfpath,pdfdirs,pdffiles in os.walk(r"C:/Users/87208/Documents/Documents/RA/Social register/pdf_input"):
    for pdf in pdffiles:
        City = re.findall(r"[A-z ]+(?= [0-9])", pdf)[0]
        Year = re.findall(r"[0-9]+", pdf)[0]
        print(City, Year)
        text_creator(City, Year)