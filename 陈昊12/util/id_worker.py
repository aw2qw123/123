# import pysnowflake

import snowflake.client


def get_id():
    return snowflake.client.get_guid()
