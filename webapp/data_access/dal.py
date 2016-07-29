from webapp.data_access import _get_open_db_connection, _close_db_connection, _fetch_all
from webapp.data_access.mappings_and_enums import STOCK_ENTITY_TYPE_TABLE_NAME

def get_all_events():
    return [dict(text=r[0], value=r[1]) for r in _fetch_all("""
                        select ec.name_en || ' - ' || e.name_en, e.starts_on from events e
                        inner join event_categories ec on e.event_category_id = ec.id
                      """)]

# print(get_all_events())

