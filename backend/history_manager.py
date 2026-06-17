import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"


def save_prediction(
    prediction,
    confidence,
    risk
):

    if os.path.exists(
        HISTORY_FILE
    ):

        with open(
            HISTORY_FILE,
            "r"
        ) as f:

            history = json.load(
                f
            )

    else:

        history = []

    history.append({

        "date":
        datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        ),

        "prediction":
        prediction,

        "confidence":
        confidence,

        "risk":
        risk

    })

    with open(
        HISTORY_FILE,
        "w"
    ) as f:

        json.dump(
            history,
            f,
            indent=4
        )


def get_history():

    if not os.path.exists(
        HISTORY_FILE
    ):
        return []

    with open(
        HISTORY_FILE,
        "r"
    ) as f:

        return json.load(
            f
        )