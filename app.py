import pytz
from flask import Flask, request

from notion_helpers import *

timezone = "Europe/Kiev"

app = Flask(__name__)


if __name__ == "__main__":

    app.debug = True
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host="0.0.0.0", port=port)
    app.run()
