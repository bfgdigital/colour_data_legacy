import pandas as pd
import numpy as np

##################################
# Randomisation of Colours
##################################

from .utils import create_cache_connection

PALLETS_DICT = pd.read_csv(
    './static/pallets_dictionary.csv', index_col=['pallet_name'])  # local
RANDOM_SPREAD = 15

number_of_pallets = 16

# Each collumn is a new pallet

cache = create_cache_connection()

def pallet_selector():
    # TODO make this unique to each user.
    current_iteration = cache.get('pallet_iteration')
    if not current_iteration:
        current_iteration = 0
    selected_pallet = PALLETS_DICT.iloc[int(current_iteration)]
    pallet_name = selected_pallet.name

    current_iteration = (int(current_iteration) % number_of_pallets) + 1
    cache.set('pallet_iteration', current_iteration)
    return selected_pallet, pallet_name  # 1,2

# Selecting a pallet and randomizing.

def pallet_randomiser():
    selected_pallet, pallet_name = pallet_selector()  # 1,2
    randomised_pallet = []  # reset the colours
    for colour in selected_pallet[:12]:
        hex_colour = colour.lstrip('#')  # TODO: change all values from hex to RGB.
        converted_value = list(
            int(hex_colour[i:i+2], 16) for i in (0, 2, 4))  # Hex conversion
        colour_randomised = [np.random.randint((max(0, channel - RANDOM_SPREAD)),
                                               (min(255, channel + RANDOM_SPREAD))
                                               ) for channel in converted_value]
        randomised_pallet.append(tuple(colour_randomised))
    return selected_pallet, pallet_name, randomised_pallet  # 3
