import calendar
from datetime import timedelta, datetime

from notion.block import *
from notion.client import NotionClient


def test(k):
    d = datetime.now()
    current_date = d.date()
    current_day = d.day
    fake_date = d.replace(day=current_day+k).date()

    token_v2 = os.environ.get("TOKEN")
    test_board_url = os.environ.get("URL")
    date_url = os.environ.get("DATE_URL")
    fake_date_url = os.environ.get("FAKE_DATE_URL")

    # token = "42ec7db22a5a08057e5b3126fc64dc59d34331d004301c4de456e206561bf520017c6238259bc042ae60e6106537ef15b62834e264bec886fa98964545817187e8c84eac012dac3cbca4850804ca"
    # test_board = "https://www.notion.so/8c8a8b27231c41eeb650231958dd5374?v=812fb88401084234a3d75ad2082626e6"
    # date_u = "https://www.notion.so/Test-task-figured-out-f8d4427a4a4a4daebbd6b9d4054882e3#5c2c77fcf4e841bd9cffc31f65c74e3f"
    # fake_date_u = "https://www.notion.so/Test-task-figured-out-f8d4427a4a4a4daebbd6b9d4054882e3#7f665c214b314163b6d6ea39a7e0af8a"

    client = NotionClient(token_v2)

    time_widget = client.get_block(date_url)
    time_widget.title_plaintext = str(current_date)
    fake_time_widget = client.get_block(fake_date_url)
    fake_time_widget.title_plaintext = str(fake_date)

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
    return k + 1


k = 0

k = test(k)