import calendar
from datetime import timedelta, datetime
import pytz
from flask import Flask, request
from notion.block import *
from notion.client import NotionClient
from notion_helpers import *

timezone = "Europe/Kiev"

app = Flask(__name__)


@app.route("/test", methods=["GET"])
def test():
    d = datetime.datetime.now()
    current_date = d.date()

    token_v2 = os.environ.get("TOKEN")
    test_board_url = os.environ.get("URL")
    date_url = os.environ.get("DATE_URL")

    client = NotionClient(token_v2)

    time_widget = client.get_block(date_url)
    time_widget.title_plaintext = str(current_date)

    test_board = client.get_collection_view(test_board_url)

    filter_params = {
        "filters":
            [
                {
                    "filter":
                        {
                            "value":
                                {
                                    "type": "exact",
                                    "value": "DONE"
                                },
                            "operator": "enum_is"
                        },
                    "property": "Status",
                },

            ],
        "operator": "and",
    }
    test_board = test_board.build_query(filter=filter_params)
    result = test_board.execute()

    for task in result:
        if "Daily" in task.get_property("periodicity"):
            task.set_property("status", "TO DO")
            task.set_property("set_date", current_date)
            task.set_property("due_date", task.get_property("set_date").start + timedelta(days=1))

        elif "1t/w" in task.get_property("periodicity"):
            task.set_property("status", "TO DO")

            if task.get_property("set_date") is None:
                task.set_property("set_date", current_date)

            while task.get_property("set_date").start < current_date:
                task.set_property("set_date", task.get_property("set_date").start + timedelta(days=7))
            task.set_property("due_date", task.get_property("set_date").start + timedelta(days=1))

        elif "1t/m" in task.get_property("periodicity"):
            task.set_property("status", "TO DO")

            if task.get_property("set_date") is None:
                task.set_property("set_date", current_date)

            temp_set_date = task.get_property("set_date").start
            while temp_set_date < current_date:
                month_days = calendar.mdays[temp_set_date.month]
                temp_set_date += timedelta(days=month_days)
            task.set_property("set_date", temp_set_date)
            task.set_property("due_date", task.get_property("set_date").start + timedelta(days=7))
    return "Hello"


if __name__ == "__main__":

    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    app.run()
