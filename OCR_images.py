#!/usr/bin/env python
# coding: utf-8

# In[ ]:


####Tianrui Lai####
#####Feb 2023#####


# In[1]:

import io
import json
from google.cloud import storage
import os
import shutil
from google.cloud import vision

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'C:\Users\87208\Documents\Documents\RA\Social register\key.json'


# In[2]:


####The google OCR to detect text from png
def detect_text(inputpath,outputpath):
    """Detects text in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open(inputpath, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    if len(texts) != 0:
       
        text = texts[0]
        '''
        print('Texts:')

        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))
        '''
        
        f = open(outputpath,"w",encoding='utf-8')
        f.write(text.description)
        f.close()

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

BASE_PATH = r"C:\Users\87208\Documents\Documents\RA\Social register"
STATE_PATH = os.path.join(BASE_PATH, "script_state.json")

def save_state(state):
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f)

def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, 'r') as f:
            return json.load(f)
    else:
        return {}

def process_directory(image_folder, text_folder):
    image_dir = os.path.join(BASE_PATH, image_folder)
    text_dir = os.path.join(BASE_PATH, text_folder)

    state = load_state()

    for _, dirs, _ in os.walk(image_dir):
        for dir in dirs:
            inputdir = os.path.join(image_dir, dir)
            outputdir = os.path.join(text_dir, dir)

            if not os.path.exists(outputdir):
                os.makedirs(outputdir)

            for _, _, pics in os.walk(inputdir):
                for pic in pics:
                    inputpath = os.path.join(inputdir, pic)
                    outputpath = os.path.join(outputdir, pic[:-4] + ".txt")

                    if inputpath in state and state[inputpath] == 'done':
                        print(f'Skipping {inputpath}, already processed')
                        continue

                    try:
                        detect_text(inputpath, outputpath)
                        state[inputpath] = 'done'
                    except Exception as e:
                        print(f'Error processing {inputpath}: {e}')
                        state[inputpath] = 'error'

                    save_state(state)



# In[ ]:


###Traverse all the pictures
'''
for _,picdirs,_ in os.walk("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\images_household_new"):
    for picdir in picdirs:
        inputdir = os.path.join("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\images_household_new",picdir)
        outputdir = os.path.join("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\text_output_household_new",picdir)
        if os.path.exists(outputdir):
            shutil.rmtree(outputdir)
        os.makedirs(outputdir)
        for _,_,pics in os.walk(inputdir):
            for pic in pics:
                inputpath = os.path.join(inputdir,pic)        
                outputpath = os.path.join(outputdir,pic[:-4]+".txt")
                detect_text(inputpath,outputpath)


for _,picdirs,_ in os.walk("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\images_single_new"):
    for picdir in picdirs:
        inputdir = os.path.join("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\images_single_new",picdir)
        outputdir = os.path.join("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\text_output_single_new",picdir)
        if os.path.exists(outputdir):
            shutil.rmtree(outputdir)
        os.makedirs(outputdir)
        for _,_,pics in os.walk(inputdir):
            for pic in pics:
                inputpath = os.path.join(inputdir,pic)        
                outputpath = os.path.join(outputdir,pic[:-4]+".txt")
                detect_text(inputpath,outputpath)
'''

def main():
    process_directory(r"register\images_household_new", r"text_output_household_new")
    #process_directory("images_single_new", "text_output_single_new")
    for dirpath, dirnames, files in os.walk("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\text_output_household_new"):
        # For each subdirectory, create the file
        for dirname in dirnames:
            file_path = os.path.join(dirpath, dirname, "empty.txt")
            with open(file_path, 'w') as file:
                pass

if __name__ == "__main__":
    main()

