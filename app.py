##################################
# Imports
##################################

# Flask
import flask
from flask import Flask, send_file, request, render_template, make_response, session

# SQL
# import sqlalchemy
# from sqlalchemy import create_engine
# from flask_sqlalchemy import SQLAlchemy

# Redis
import redis

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
# │   ├── PALLETS_DICT.csv
# │   └── welcome.png
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
app.config['DEBUG'] = True
app.config['ASSETS_DEBUG'] = True
app.config['COMPRESSOR_DEBUG'] = True
app.config['STATIC_FOLDER'] = 'static'
app.config['TEMPLATES_FOLDER'] = 'templates'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1 # To ensure new image loads

# SQL Connection
HEROKU_POSTGRESQL = os.environ.get('HEROKU_POSTGRESQL_PURPLE_URL')
engine = create_engine(HEROKU_POSTGRESQL)

# Redis Connection
HEROKU_REDIS = os.getenv('REDIS_URL')
redis = redis.from_url(HEROKU_REDIS)

##################################
# Route = /
##################################
@app.route('/', methods=['GET','POST'])
def main():

    # Front End Variables
    ##################################
    temp_img_url = '/static/welcome.png' # Welcome Image
    
    # Set Globals
    ##################################    
    global USER
    global COUNTER
    
    # Post
    ##################################
    if flask.request.method == 'POST': # Start the action
        
        ##################################
        # Start App
        ##################################
        print(f'{USER} in redis data') # look for this in logs.
        
        # Input from user
        inputs = flask.request.form
        recorded_result = inputs['submit']
        dummytime = datetime.now().strftime("%S") # This query string added to the URL tricks it into reloading.
        temp_img_url = '/static/temp.png?dummy=' + str(dummytime) # display new image.
        
        # Magic
        if COUNTER == 0:
            generate_image()
            COUNTER += 1
            redis.set('counter', COUNTER) # Set Redis Token
            redis.set('user', USER) # Set Redis Token
        else:
            process_answer(recorded_result) # Answer Function
            write_data()
            generate_image()
            COUNTER += 1
            redis.set('counter', COUNTER) # Set Redis Token
            redis.set('user', USER) # Set Redis Token
    else:
        print('Not Post')
    
    # Page Selector
    ##################################
    enough_submissions = int(redis.get('counter'))
    if enough_submissions > 30:
        reset_app()
        url = 'thankyou.html'
    else:
        url = 'index.html'
        
    # Render Template
    ##################################
    return flask.render_template(url, counter = int(redis.get('counter')), temp_img_url = temp_img_url) 

##################################
# Global Variables
##################################
USER = secrets.token_urlsafe(4) # User to store in the session.
redis.set('user', USER) # Set Redis Token
COUNTER = 0
redis.set('counter', COUNTER) # Set Redis Token
PALLET_ITER = 0 # Start with pallet 0. 
RANDOM_SPREAD = 15
BACKGROUND = (255, 255, 255) # White background.
TOTAL_CIRCLES = 700 # set to limit generation time.

# Pallets
PALLETS_DICT = pd.read_csv('./static/pallets_dictionary.csv', index_col=['pallet_name']) # local
# PALLETS_DICT = pd.read_sql('colour_pallets', engine, index_col='pallet_name') # remote

##################################
# Randomisation of Colours
##################################

# Each collumn is a new pallet
def pallet_selector():
    global PALLET_ITER
    if PALLET_ITER > 16: # 16 pallets
        PALLET_ITER = 0       
    selected_pallet = PALLETS_DICT.iloc[PALLET_ITER]
    pallet_name = selected_pallet.name
    PALLET_ITER += 1
    return selected_pallet, pallet_name # 1,2

# Selecting a pallet and randomizing.
def pallet_randomiser():
    selected_pallet, pallet_name = pallet_selector() # 1,2
    randomised_pallet = []  # reset the colours
    for colour in selected_pallet[:12]:
        hex_colour = colour.lstrip('#')
        converted_value = list(int(hex_colour[i:i+2], 16) for i in (0, 2, 4)) # Hex conversion
        colour_randomised = [np.random.randint((max(0, channel - RANDOM_SPREAD)), \
                                               (min(255, channel + RANDOM_SPREAD)) \
                                              ) for channel in converted_value]
        randomised_pallet.append(tuple(colour_randomised))
    return selected_pallet, pallet_name, randomised_pallet # 3

def mask():
    masks = ["A","B","C","D","E","1","2","3","4","5","No Image"]
    random_mask = random.choice(masks)
    mask_path = './static/masks/'+random_mask+".png"
    return random_mask, mask_path # 4,5

##################################
# Data Preperation
##################################

def prepare_data():

    selected_pallet, pallet_name, randomised_pallet = pallet_randomiser() # 1,2,3
    random_mask, mask_path = mask() # 4,5
    
    # Write to data
    global image_data
    image_data = {
        'mask_path' : mask_path,
        'mask_image' : random_mask, # 1
        'cb_type1' : selected_pallet[12],
        'cb_type2' : selected_pallet[13],
        'ncb' : selected_pallet[14], # 1
        'datetime' : datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # auto
        'random_spread' : RANDOM_SPREAD, # default
        'pallet_used' : pallet_name, # 3
        'baseline' : list(selected_pallet[:12]),
        'colour_list' : randomised_pallet,
        'COLORS_ON' : [i  for i in randomised_pallet[0:6]],
        'COLORS_OFF' : [i for i in randomised_pallet[6:12]],
    }
    return image_data

# Circle / Dot Functions
# Adapted from https://github.com/franciscouzo/ishihara_generator
################################################################## 

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
# Adapted from https://github.com/franciscouzo/ishihara_generator
##################################################################           

def generate_image():
    
    prepare_data()
    
    image = Image.open(image_data['mask_path'])
    image2 = Image.new('RGB', image.size, BACKGROUND)
    draw_image = ImageDraw.Draw(image2)

    width, height = image.size

    # Set dot size here
    min_diameter = (width + height) / 185
    max_diameter = (width + height) / 51

    circle = generate_circle(width, height, min_diameter, max_diameter)
    circles = [circle]

    circle_draw(draw_image, image, circle,)

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
    thetime =  image_data['datetime']
    # image2.save('static/records/' + str(thetime) + '.png') # Only used locally
    image2.save('static/temp.png') #overwrites existing image
    

##################################
# Result Variables
##################################

def process_answer(recorded_result):
    global user_data
    user_data = {
        'user': str(redis.get('user')),
        'counter' : int(redis.get('counter')),
        'correct': 0,
        'near_miss' : 0,
        'recorded_result' : "recorded_result",
    }
    
    # Update Response
    user_data.update(recorded_result = recorded_result)
    if user_data['recorded_result'] == image_data['mask_image']:
        user_data.update(correct = 1) 
    else:
        user_data.update(correct = 0)
        
    # Evaluate near-misses
    near_miss_scenarios = [("E","B"),("D","B"),("3","B"),("C","5")]
    near_miss_situation = (user_data['recorded_result'],image_data['mask_image'],)
    if near_miss_situation in near_miss_scenarios or near_miss_situation[::-1] \
    in near_miss_scenarios :
        user_data.update(near_miss = 1)
    else:
        user_data.update(near_miss = 0)


# Annoying bug with SQL Alchemy numpy.int64
def final_cleaning():
    global image_data
    global user_data
    
    # Build single file
    datafile = pd.DataFrame(image_data.values(), index=image_data.keys()).T
    userfile = pd.DataFrame(user_data.values(), index=user_data.keys()).T
    resultfile = pd.concat([datafile,userfile], axis=1)
    
    # Prepare Data for SQL
    resultfile[['counter','correct','near_miss','cb_type1','cb_type2','ncb','random_spread']] = \
    resultfile[['counter','correct','near_miss','cb_type1','cb_type2','ncb','random_spread']].astype(int) # Get rid of numpy values for SQLAlchemy
    resultfile = resultfile.reindex(sorted(resultfile.columns, reverse=True), axis=1) # Sort columns reverse aphabetically.
    resultfile = resultfile.drop(['mask_path','COLORS_ON','COLORS_OFF'],axis=1) # drop unnecessary data
    user_result = resultfile.drop(['baseline','datetime','colour_list','random_spread'],axis=1) # drop unnecessary data
    
    return resultfile, user_result

# Push data to file/SLQ
def write_data():
    resultfile, user_result = final_cleaning()
    # Push Data to file/sql
    if str(user_data['user']) == str(redis.get('user')):
        action = 'append'
    else:
        action = 'replace'
    # SQL
#     user_result .to_sql('colour_results', engine, if_exists=action, index=False) # need a good mechanism here, based on user 
#     resultfile.to_sql('colour_data', engine, if_exists='append', index=False) 
    # Local
    user_result.to_csv('./Notebooks/CSV/local_colour_results.csv', mode='a', header=False, index=False)
    resultfile.to_csv('./Notebooks/CSV/local_colour_data.csv', mode='a', header=False, index=False)
    
def reset_app():
    global USER
    global COUNTER
    redis.flushdb()
    USER = secrets.token_urlsafe(4) # User to store in the session.
    redis.set('user', USER) # Set Redis Token
    COUNTER = 0
    redis.set('counter', COUNTER) # Set Redis Token
    pass
    
##################################
# Image Refresh 
##################################

# No caching at all for API endpoints.
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
    app.run(host='127.0.0.1', port=5000, use_reloader=True)
# [END gae_python38_app]