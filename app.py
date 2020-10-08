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
    
    if image_data["counter"] >= 101:
        url = 'thankyou.html'
    else:
        url = 'index.html'
    
    # Response Capturing
    ##################################

    if flask.request.method == 'POST':
        inputs = flask.request.form
        recorded_result = inputs['submit']
        dummytime = datetime.now().strftime("%S")
        temp_img_url = '/static/temp.png?dummy=' + str(dummytime) # display new image.
        answer(recorded_result)
        session['username'] = image_data['user']
        session['counter'] = image_data['counter']
        
    else:
        print('Not Post')
    
    # Render Template
    return flask.render_template(url, counter = counter, temp_img_url = temp_img_url) 

##################################
# Ishihara Data
##################################

# open and read the pallets csv
# this will become a second SQL Db down the line
pallets_dictionary = pd.read_csv('./CSV/pallets_dictionary.csv', index_col=False)

# Data dictionary pushed to SQL/CSV
image_data = {
    'user': secrets.token_urlsafe(4),
    'counter' : 0,
    'correct': 0,
    'recorded_result' : "",
    'mask_image' : 6,
    'cb_type1' : 0,
    'cb_type2' : 0,
    'ncb' : 0,
    'datetime' : 'New User',
    'random_spread' : 15,
    'pallet_used' : "",
    'pallet_values' : [],
    'ishihara_list' :[],
    'COLORS_ON' : [],
    'COLORS_OFF' : [],
}

##################################
# Global Variables
##################################

# Find somewhere to put these.
# White background.
BACKGROUND = (255, 255, 255)
# set to limit generation time.
TOTAL_CIRCLES = 700

##################################
# Randomisation of Colours
##################################

# Selecting a pallet and randomizing.
def pallet_randomiser():
    [random_hex] = pallets_dictionary.sample(n=1).values.tolist()
    random_set = random_hex[0]
    image_data['ishihara_list'] = []  # WRITING TO IMAGE_DATA
    for colour in random_hex[1:13]:
        hex_colour = colour.lstrip('#')
        converted_value = list(int(hex_colour[i:i+2], 16) for i in (0, 2, 4))
        colour_randomised = [np.random.randint((max(0, channel - image_data['random_spread'])), (min(255, channel + image_data['random_spread']))) for channel in converted_value]
        image_data['ishihara_list'].append(tuple(colour_randomised))

    image_data['COLORS_ON'] = [i  for i in image_data['ishihara_list'][0:6]] # WRITING TO IMAGE_DATA
    image_data['COLORS_OFF'] = [i for i in image_data['ishihara_list'][6:12]] # WRITING TO IMAGE_DATA
    image_data.update(pallet_used = random_set)  # WRITING TO IMAGE_DATA
    image_data.update(pallet_values = random_hex[1:13])  # WRITING TO IMAGE_DATA
    image_data.update(cb_type1 = random_hex[13])  # WRITING TO IMAGE_DATA
    image_data.update(cb_type2 = random_hex[14])  # WRITING TO IMAGE_DATA
    image_data.update(ncb = random_hex[15])  # WRITING TO IMAGE_DATA


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
    print("Running")

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

    # 1) Correct Or Not
    image_data.update(recorded_result = recorded_result)
    if image_data['recorded_result'] == image_data['mask_image']:
        image_data.update(correct = 1) # WRITING TO IMAGE_DATA
    else:
        image_data.update(correct = 0) # WRITING TO IMAGE_DATA

    # 2) Counter +1
    image_data["counter"] += 1 # WRITING TO IMAGE_DATA

    # 3) Write to file
    datafile = pd.DataFrame(image_data.values()).T
    datafile.columns = image_data.keys()
    # datafile.to_csv('./CSV/dev_colourdata.csv', mode='a', header=False, index=False)
    # print(datafile)
    # datafile.to_sql('colour_data', engine, if_exists='append', index=False)

    # 4) Generate New Image
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