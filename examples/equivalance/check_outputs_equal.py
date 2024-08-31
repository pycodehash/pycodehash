"""Script to check that the output of both implementations is the same."""

import pandas as pd
from sample1 import func
from sample2 import create_df_mapping

if __name__ == "__main__":
    events = {
        "status": ["SUCCEEDED", "SUCCEEDED", "FAILED", "FAILED", "SUCCEEDED", "SUCCEEDED", "FAILED"],
        "errcode": [None, None, 106, 54, None, None, 201],
        "errmsg": [
            None,
            None,
            "Coffee Machine Not Refilled",
            "Unidentified Flying Burrito Has Crashed into System",
            None,
            None,
            "Productivity Levels Critical",
        ],
    }
    df = pd.DataFrame(events)

    mapping1 = func(df, "errcode", "errmsg")
    assert mapping1 == {
        106: "Coffee Machine Not Refilled",
        54: "Unidentified Flying Burrito Has Crashed into System",
        201: "Productivity Levels Critical",
    }

    mapping2 = create_df_mapping(df, "errcode", "errmsg")
    assert mapping2 == {
        106: "Coffee Machine Not Refilled",
        54: "Unidentified Flying Burrito Has Crashed into System",
        201: "Productivity Levels Critical",
    }
