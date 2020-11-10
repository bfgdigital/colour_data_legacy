##################################
# Imports
##################################

# Flask
import flask
from flask import Flask, send_file, request, render_template, make_response, session

# SQL
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

# app
import math
import random
import sys
from datetime import datetime
import os
import dotenv
dotenv.load_dotenv()

import numpy as np
import pandas as pd
import secrets
from PIL import Image, ImageDraw
try:
    from scipy.spatial import cKDTree as KDTree
    import numpy as np
    IMPORTED_SCIPY = True
except ImportError:
    IMPORTED_SCIPY = False


# Structure
# ├── /templates
# │   ├── /CSS
# │   │   └── style.css
# │   ├── index.html
# │   └── thankyou.html
# ├── /static
# │   ├── /img
# │   │   ├── bluey1.png
# │   │   ├── bluey2.png
# │   │   ├── bluey3.png
# │   │   └── etc...
# │   ├── /masks
# │   │   ├── A.png
# │   │   ├── 1.png
# │   │   ├── B.png
# │   │   └── etc...
# │   ├── /records
# │   │   └── all recorded images...
# │   ├── temp.png
# │   └── welcome.png
# ├── /CSV
# │   └── pallets_dictionary.csv
# ├── app.py
# └── requirements.txt

##################################
# Flask App Start
##################################

app = Flask(__name__,instance_relative_config=False)
# Config
KEY = os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = KEY
app.config['FLASK_APP'] = 'wsgi.py'
app.config['DEBUG'] = False
app.config['ASSETS_DEBUG'] = False
app.config['COMPRESSOR_DEBUG'] = False
app.config['STATIC_FOLDER'] = 'static'
app.config['TEMPLATES_FOLDER'] = 'templates'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1 # To ensure new image loads

# SQL Connection
HEROKU_POSTGRESQL = os.environ.get('HEROKU_POSTGRESQL_PURPLE_URL')
engine = create_engine(HEROKU_POSTGRESQL)

##################################
# Route = /
##################################

@app.route('/', methods=['GET','POST'])

def main():

    # Front End Variables
    ##################################
    
    # Welcome Image
    temp_img_url = '/static/welcome.png'
    
    # Display Thank You page after 100 attempts.
    counter = image_data['counter']
    
    if image_data["counter"] >= 31:
        url = 'thankyou.html'
    else:
        url = 'index.html'
        
    if 'user' in session:
        session['user'] = image_data['user']  # reading and updating session data  
    else:
        session['user'] = USER
    
    # Response Capturing
    ##################################

    if flask.request.method == 'POST':
        inputs = flask.request.form
        recorded_result = inputs['submit']
        dummytime = datetime.now().strftime("%S")
        temp_img_url = '/static/temp.png?dummy=' + str(dummytime) # display new image.
        answer(recorded_result) # Answer Function
        # session user here?
        
    else:
        print('Response Capturing else')
    
    # Render Template
    return flask.render_template(url, counter = counter, temp_img_url = temp_img_url) 

##################################
# Global Variables
##################################

USER = secrets.token_urlsafe(4) # User to store in the session.

BACKGROUND = (255, 255, 255) # White background.

TOTAL_CIRCLES = 700 # set to limit generation time.

PALLET_SELECTED = 0 # Iterator for the pallet outside of the functions.

##################################
# Ishihara Data
##################################

# Data dictionary pushed to SQL/CSV
image_data = {
    'user': USER,
    'counter' : 0,
    'correct': 0,
    'near_miss' : 0,
    'recorded_result' : "",
    'mask_image' : 6,
    'cb_type1' : 0,
    'cb_type2' : 0,
    'ncb' : 0,
    'datetime' : 'New User',
    'random_spread' : 15,
    'pallet_used' : "",
    'baseline' : [],
    'ishihara_list' :[],
    'COLORS_ON' : [],
    'COLORS_OFF' : [],
}

##################################
# Pallets
##################################

# Open and read the pallets csv
# pallets_dictionary = pd.read_csv('./CSV/pallets_dictionary.csv', index_col=False)
pallets_dictionary = pd.read_sql('colour_pallets', engine, index_col='pallet_name')

##################################
# Randomisation of Colours
##################################

# Each collumn is a new pallet
def pallet_selector():
    global PALLET_SELECTED
    if PALLET_SELECTED > 16: # 16 pallets
        PALLET_SELECTED = 0       
    selected_pallet = pallets_dictionary.iloc[PALLET_SELECTED]
    pallet_name = selected_pallet.name
    PALLET_SELECTED += 1
    return selected_pallet, pallet_name    


# Selecting a pallet and randomizing.
def pallet_randomiser():
    selected_pallet, pallet_name = pallet_selector()
    image_data['ishihara_list'] = []  # reset the colours
    for colour in selected_pallet[:12]:
        hex_colour = colour.lstrip('#')
        converted_value = list(int(hex_colour[i:i+2], 16) for i in (0, 2, 4)) # Hex conversion
        colour_randomised = [np.random.randint((max(0, channel - image_data['random_spread'])), (min(255, channel + image_data['random_spread']))) for channel in converted_value]
        image_data['ishihara_list'].append(tuple(colour_randomised))

    image_data['COLORS_ON'] = [i  for i in image_data['ishihara_list'][0:6]] # Set the colours on the symbol
    image_data['COLORS_OFF'] = [i for i in image_data['ishihara_list'][6:12]] # Set the background colours
    image_data.update(pallet_used = pallet_name)  # update the pallet name
    image_data.update(baseline = list(selected_pallet[:12]))  # (numpy) record baseline colours
    image_data.update(cb_type1 = selected_pallet[12])
    image_data.update(cb_type2 = selected_pallet[13])
    image_data.update(ncb = selected_pallet[14])


# Circle / Dot Functions
##################################

# max_diameter * 2.6 + min_diameter * 0.6
def generate_circle(image_width, image_height, min_diameter, max_diameter):
    radius = random.triangular(min_diameter, max_diameter,max_diameter * .8 + min_diameter * .2) / 2

    angle = random.uniform(0, math.pi * 2)
    distance_from_center = random.uniform(0, image_width * 0.48 - radius)
    x = image_width  * 0.5 + math.cos(angle) * distance_from_center
    y = image_height * 0.5 + math.sin(angle) * distance_from_center

    return x, y, radius


def overlaps_motive(image, xyr_values):
    (x, y, r) = xyr_values
    points_x = [x, x, x, x-r, x+r, x-r*0.93, x-r*0.93, x+r*0.93, x+r*0.93]
    points_y = [y, y-r, y+r, y, y, y+r*0.93, y-r*0.93, y+r*0.93, y-r*0.93]

    for xy in zip(points_x, points_y):
        if image.getpixel(xy)[:3] != BACKGROUND:
            return True

    return False


def circle_intersection(xyr_values1, xyr_values2):
    (x1, y1, r1) = xyr_values1
    (x2, y2, r2) = xyr_values2
    return (x2 - x1)**2 + (y2 - y1)**2 < (r2 + r1)**2


def circle_draw(draw_image, image, xyr_values3):
    (x, y, r) = xyr_values3
    fill_colors = image_data['COLORS_ON'] if overlaps_motive(image, (x, y, r)) else image_data['COLORS_OFF']
    fill_color = random.choice(fill_colors)
    draw_image.ellipse((x - r, y - r, x + r, y + r),
                    fill=fill_color,
                    outline=fill_color)


# Image Generation Function
##################################                    

def generate_image():
    
    pallet_randomiser()
    masks = ["A","B","C","D","E","1","2","3","4","5","No Image"]
    random_mask = random.choice(masks)
    image_data.update(mask_image = random_mask) # WRITING TO IMAGE_DATA
    mask_path = './static/masks/'+random_mask+".png"

    image = Image.open(mask_path)
    image2 = Image.new('RGB', image.size, BACKGROUND)
    draw_image = ImageDraw.Draw(image2)

    width, height = image.size

    # Set dot size here
    min_diameter = (width + height) / 185
    max_diameter = (width + height) / 51

    circle = generate_circle(width, height, min_diameter, max_diameter)
    circles = [circle]

    circle_draw(draw_image, image, circle)

    try:
        for i in range(TOTAL_CIRCLES):
            tries = 0
            if IMPORTED_SCIPY:
                kdtree = KDTree([(x, y) for (x, y, _) in circles])
                while True:
                    circle = generate_circle(width, height, min_diameter, max_diameter)
                    elements, indexes = kdtree.query([(circle[0], circle[1])], k=12)
                    for element, index in zip(elements[0], indexes[0]):
                        if not np.isinf(element) and circle_intersection(circle, circles[index]):
                            break
                    else:
                        break
                    tries += 1
            else:
                while any(circle_intersection(circle, circle2) for circle2 in circles):
                    tries += 1
                    circle = generate_circle(width, height, min_diameter, max_diameter)

            # print('{}/{} {}'.format(i, TOTAL_CIRCLES, tries))

            circles.append(circle)
            circle_draw(draw_image, image, circle)
    except (KeyboardInterrupt, SystemExit):
        pass

    image2.save('static/temp.png') #overwrites existing image
    thetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    image_data.update(datetime = thetime)
    # image2.save('static/records/' + str(thetime) + '.png') # Only used locally


##################################
# Result Variables
##################################

def answer(recorded_result):
    # 1) Update Response
    image_data.update(recorded_result = recorded_result)
    # 2) Evaluate Response
    if image_data['recorded_result'] == image_data['mask_image']:
        image_data.update(correct = 1) # WRITING TO IMAGE_DATA
    else:
        image_data.update(correct = 0) # WRITING TO IMAGE_DATA
    # 3) Evaluate near-misses
    if image_data['mask_image'] == "E" and image_data['recorded_result'] == "B":
        image_data.update(near_miss = 1)
    elif image_data['mask_image'] == "D" and image_data['recorded_result'] == "B":
        image_data.update(near_miss = 1)
    elif image_data['mask_image'] == "3" and image_data['recorded_result'] == "B":
        image_data.update(near_miss = 1)
    elif image_data['mask_image'] == "C" and image_data['recorded_result'] == "5":
        image_data.update(near_miss = 1)
    else:
        image_data.update(near_miss = 0)

    # 4) Turn the Counter +1
    image_data["counter"] += 1 # WRITING TO IMAGE_DATA

    # 4) Prepare Data for SQL
    datafile = pd.DataFrame(image_data.values(), index=image_data.keys()).T
    datafile[['counter','correct','near_miss','cb_type1','cb_type2','ncb','random_spread']] = datafile[['counter','correct','near_miss','cb_type1','cb_type2','ncb','random_spread']].astype(int)
    datafile = datafile.drop(['COLORS_ON','COLORS_OFF'],axis=1)
    user_result = datafile.drop(['baseline','datetime','ishihara_list','random_spread'],axis=1)
    
    # 5) Push Data
    datafile.to_sql('colour_data', engine, if_exists='append', index=False) 
    #     datafile.to_csv('./Notebooks/CSV/dev_colourdata.csv', header=False, index=False)
    if str(session['user']) == str(user_result['user']):
        user_result.to_sql('colour_results', engine, if_exists='replace', index=False) # need a good mechanism here, based on user existing.
        # user_result.to_csv('./CSV/dev_colour_results.csv', mode='a', header=False, index=False)
    else:
        user_result.to_sql('colour_results', engine, if_exists='append', index=False)
        # user_result.to_csv('./CSV/dev_colour_results.csv', mode='a', header=False, index=False)

    # 6) Generate New Image
    generate_image() # Run Main Func

##################################
# Image Refresh 
##################################

# No caching at all for API endpoints.
# Have disabled this previously, does not fix session issue.
# Solves most image refresh issues, not for everyone.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5000, use_reloader=False)
# [END gae_python38_app]
