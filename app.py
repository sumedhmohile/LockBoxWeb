from flask import Flask
from lockboxweb.functions import update_boxes_to_warn, update_boxes_to_unlock

app = Flask(__name__)

@app.route('/warn_all')
def warn_all_boxes():
    boxes = update_boxes_to_warn()
    return boxes

@app.route('/unlock_all')
def unlock_all_boxes():
    boxes = update_boxes_to_unlock()
    return boxes