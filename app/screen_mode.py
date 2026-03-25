
from st_screen_stats import ScreenData

MARGIN = 20
WIDTH_CUTOFF = 767.5 + MARGIN

def get_screen_mode():
    scr_data_obj = ScreenData(setTimeout = 1000)
    screen_data = scr_data_obj.st_screen_data(on_change = None, default = None, key = 'scr_data_obj', interval = 0.3)
    screen_width = screen_data['screen']['width']
    
    if screen_width > WIDTH_CUTOFF + MARGIN:
        return('desktop')
    elif screen_width < WIDTH_CUTOFF - MARGIN:
        return('mobile')
    else:
        return('desktop')


