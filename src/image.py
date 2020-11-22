import random

from datetime import datetime
from .colours import RANDOM_SPREAD, pallet_randomiser

class ImageMetadata():
    def __init__(self):
        random_mask, mask_path = self.generate_mask()
        selected_pallet, pallet_name, randomised_pallet = pallet_randomiser()

        self.mask_path = mask_path
        self.mask_image = random_mask
        self.cb_type1 = selected_pallet[12]
        self.cb_type2 = selected_pallet[13]
        self.ncb = selected_pallet[14]
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.random_spread = RANDOM_SPREAD
        self.pallet_used = pallet_name
        self.baseline = list(selected_pallet[:12])
        self.colour_list = randomised_pallet
        self.COLORS_ON = [i for i in randomised_pallet[0:6]]
        self.COLORS_OFF = [i for i in randomised_pallet[6:12]]

    def generate_mask(self):
        masks = ["A", "B", "C", "D", "E", "1", "2", "3", "4", "5", "No Image"]
        random_mask = random.choice(masks)
        mask_path = './static/masks/'+random_mask+".png"
        return random_mask, mask_path
