from flask import Flask
from lockboxweb.functions import update_boxes_to_warn

app = Flask(__name__)

@app.route('/warn_all')
def warn_all_boxes():
    boxes = update_boxes_to_warn()
    return boxes
