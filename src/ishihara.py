import math
import random 

from src.constants import IMAGE_BACKGROUND_COLOUR

# Circle / Dot Functions
# Adapted from https://github.com/franciscouzo/ishihara_generator
##################################################################

def generate_circle(image_width, image_height, min_diameter, max_diameter):
    radius = random.triangular(
        min_diameter, max_diameter, max_diameter * .8 + min_diameter * .2) / 2
    angle = random.uniform(0, math.pi * 2)
    distance_from_center = random.uniform(0, image_width * 0.48 - radius)
    x = image_width * 0.5 + math.cos(angle) * distance_from_center
    y = image_height * 0.5 + math.sin(angle) * distance_from_center
    return x, y, radius


def overlaps_motive(image, xyr_values):
    (x, y, r) = xyr_values
    points_x = [x, x, x, x-r, x+r, x-r*0.93, x-r*0.93, x+r*0.93, x+r*0.93]
    points_y = [y, y-r, y+r, y, y, y+r*0.93, y-r*0.93, y+r*0.93, y-r*0.93]

    for xy in zip(points_x, points_y):
        if image.getpixel(xy)[:3] != IMAGE_BACKGROUND_COLOUR:
            return True
    return False


def circle_intersection(xyr_values1, xyr_values2):
    (x1, y1, r1) = xyr_values1
    (x2, y2, r2) = xyr_values2
    return (x2 - x1)**2 + (y2 - y1)**2 < (r2 + r1)**2
