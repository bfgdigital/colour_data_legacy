##################################
# Imports
##################################

# Flask
from PIL import Image, ImageDraw
import secrets
import pandas as pd
import numpy as np
import flask  # TODO do I need this import?
from flask import Response, Flask, send_file, request, render_template, make_response, session

# SQL
import sqlalchemy

# Redis
# import redis

# app
import math
import random
import sys
from datetime import datetime
import os
import dotenv

from src.utils import create_app, create_cache_connection, create_db_connection, get_or_create_user_id, get_or_create_counter
from src.colours import RANDOM_SPREAD, pallet_randomiser
from src.constants import IMAGE_BACKGROUND_COLOUR, TOTAL_CIRCLES, DEVELOPMENT, PRODUCTION
from src.ishihara import overlaps_motive, circle_intersection, generate_circle
from src.image import ImageMetadata

dotenv.load_dotenv()

try:
    from scipy.spatial import cKDTree as KDTree
    IMPORTED_SCIPY = True
except ImportError:
    IMPORTED_SCIPY = False

##################################
# Flask App Start
##################################

app = Flask(__name__, instance_relative_config=False)
# Config
KEY = os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = KEY
app.config['FLASK_APP'] = 'wsgi.py'
app.config['STATIC_FOLDER'] = 'static'
app.config['TEMPLATES_FOLDER'] = 'templates'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1  # To ensure new image loads

if os.environ.get('ENVIRONMENT') == DEVELOPMENT:
    app.config['DEBUG'] = True
    app.config['ASSETS_DEBUG'] = True
    app.config['COMPRESSOR_DEBUG'] = False

cache = create_cache_connection()
db = create_db_connection()

##################################
# Routes
##################################


@app.route('/health_status', methods=['GET', 'POST'])
def health_status():
    return Response("OK", 200)


@app.route('/', methods=['GET', 'POST'])
def homepage():
    # Front End Variables
    ##################################
    temp_img_url = '/static/welcome.png'  # Welcome Image

    get_or_create_user_id()
    get_or_create_counter()

    print(session)

    # Post
    ##################################
    if flask.request.method == 'POST':  # Start the action
        # TODO move all this to a process_answer func

        # Input from user
        inputs = flask.request.form
        recorded_result = inputs['submit']
        # This query string added to the URL tricks it into reloading.
        dummytime = datetime.now().strftime("%S")
        # display new image.
        temp_img_url = '/static/temp.png?dummy=' + str(dummytime)

        image_metadata = ImageMetadata()
        if session['counter'] == 0:
            # generates the first image in the background to match reponse to image.
            generate_image(image_metadata)
            session['counter'] += 1
        else:
            user_data = {
                'user': session['user'],
                'counter': session['counter'],
                'correct': 0,
                'near_miss': 0,
                'recorded_result': "recorded_result",
            }
            process_answer(user_data, image_metadata,
                           recorded_result)  # Answer Function
            write_data(user_data, image_metadata)
            generate_image(image_metadata)
            session['counter'] += 1

    # TODO move all this GET method stuff into meaning functions
    # initial load is GET, (only below). However POST is above and below

    # Page Selector
    ##################################
    enough_submissions = session['counter']
    if enough_submissions > 35:
        session.clear()
        url = 'thankyou.html'
        return flask.render_template(url, temp_img_url=temp_img_url)
    else:
        url = 'index.html'

        # hot tip: use this for debugging
        # import ipdb; ipdb.set_trace()
        # Google for more.

        return flask.render_template(url, counter=session['counter'], temp_img_url=temp_img_url)

##################################
# Data Preperation
##################################


def circle_draw(image_metadata, draw_image, image, xyr_values3):
    (x, y, r) = xyr_values3
    # TODO does image_metadata need to contain COLORS_ON?
    fill_colors = image_metadata.COLORS_ON if overlaps_motive(
        image, (x, y, r)) else image_metadata.COLORS_OFF
    fill_color = random.choice(fill_colors)
    draw_image.ellipse((x - r, y - r, x + r, y + r),
                       fill=fill_color,
                       outline=fill_color)

# Image Generation Function
# Adapted from https://github.com/franciscouzo/ishihara_generator
##################################################################


def generate_image(image_metadata):
    image = Image.open(image_metadata.mask_path)
    image2 = Image.new('RGB', image.size, IMAGE_BACKGROUND_COLOUR)
    draw_image = ImageDraw.Draw(image2)

    width, height = image.size

    # Set dot size here
    min_diameter = (width + height) / 185
    max_diameter = (width + height) / 51

    circle = generate_circle(width, height, min_diameter, max_diameter)
    circles = [circle]

    circle_draw(image_metadata, draw_image, image, circle,)

    try:
        for i in range(TOTAL_CIRCLES):
            tries = 0
            if IMPORTED_SCIPY:
                kdtree = KDTree([(x, y) for (x, y, _) in circles])
                while True:
                    circle = generate_circle(
                        width, height, min_diameter, max_diameter)
                    elements, indexes = kdtree.query(
                        [(circle[0], circle[1])], k=12)
                    for element, index in zip(elements[0], indexes[0]):
                        if not np.isinf(element) and circle_intersection(circle, circles[index]):
                            break
                    else:
                        break
                    tries += 1
            else:
                while any(circle_intersection(circle, circle2) for circle2 in circles):
                    tries += 1
                    circle = generate_circle(
                        width, height, min_diameter, max_diameter)

            # print('{}/{} {}'.format(i, TOTAL_CIRCLES, tries))

            circles.append(circle)
            circle_draw(image_metadata, draw_image, image, circle)
    except (KeyboardInterrupt, SystemExit):
        pass
    thetime = image_metadata.datetime
    # image2.save('static/records/' + str(thetime) + '.png') # Only used locally
    image2.save('static/temp.png')  # overwrites existing image


##################################
# Result Variables
##################################

def process_answer(user_data, image_metadata, recorded_result):
    # Update Response
    user_data.update(recorded_result=recorded_result)
    if user_data['recorded_result'] == image_metadata.mask_image:
        user_data.update(correct=1)
    else:
        user_data.update(correct=0)

    # Evaluate near-misses
    near_miss_scenarios = [("E", "B"), ("D", "B"), ("3", "B"), ("C", "5")]
    near_miss_situation = (
        user_data['recorded_result'], image_metadata.mask_image
    )
    if near_miss_situation in near_miss_scenarios or near_miss_situation[::-1] \
            in near_miss_scenarios:
        user_data.update(near_miss=1)
    else:
        user_data.update(near_miss=0)


def sanitise_data(user_data, image_metadata):
    # Build single file
    datafile = pd.DataFrame(image_metadata.__dict__.values(),
                            index=image_metadata.__dict__.keys()).T
    userfile = pd.DataFrame(user_data.values(), index=user_data.keys()).T
    resultfile = pd.concat([datafile, userfile], axis=1)

    # Prepare Data for SQL
    # Note: annoying bug with SQL Alchemy numpy.int64 requires to cast to int
    resultfile[['counter', 'correct', 'near_miss', 'cb_type1', 'cb_type2', 'ncb', 'random_spread']] = \
        resultfile[['counter', 'correct', 'near_miss', 'cb_type1', 'cb_type2', 'ncb',
                    'random_spread']].astype(int)

    # Get rid of numpy values for SQLAlchemy
    # Sort columns reverse aphabetically.
    resultfile = resultfile.reindex(
        sorted(resultfile.columns, reverse=True), axis=1)
    resultfile = resultfile.drop(
        ['mask_path', 'COLORS_ON', 'COLORS_OFF'], axis=1)  # drop unnecessary data
    user_result = resultfile.drop(
        ['baseline', 'datetime', 'colour_list', 'random_spread'], axis=1)  # drop unnecessary data
    return resultfile, user_result



# Push data to file/SQL
def write_data(user_data, image_metadata):
    resultfile, user_result = sanitise_data(user_data, image_metadata)
    # Push Data to file/sql
    if str(user_data['user']) == session['user']:
        action = 'replace'
    else:
        action = 'append'
    
    if os.environ.get('ENVIRONMENT') == DEVELOPMENT:
        # Save to local csv
        user_result.to_csv('./Notebooks/CSV/local_colour_results.csv',
                        mode='a', header=False, index=False)
        resultfile.to_csv('./Notebooks/CSV/local_colour_data.csv',
                        mode='a', header=False, index=False)
    else:
        # Save to SQL DB
        # user_result .to_sql('colour_results', db, if_exists=action, index=False)
        resultfile.to_sql('colour_data', db, if_exists='append', index=False)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5000, use_reloader=True)
# [END gae_python38_app]
