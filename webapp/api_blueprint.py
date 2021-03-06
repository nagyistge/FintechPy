import flask
from webapp.data_access import fintech_stock_query_services as fsqs

api_bp = flask.Blueprint('api', __name__, url_prefix="/api")

_api = api_bp


@_api.route('/q1/aggregate')  # TODO: Only used for url_for in the makeChart JS, need to fix an alternative
@_api.route('/q1/aggregate/<int:setid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>/<sort_order>/<top_n>',
            methods=['GET', 'POST'])
def q1_aggregate(setid, direction, percent, from_yr, to_yr, sort_order, top_n):
    sectors_to_filter_by = None

    if flask.request.method == 'POST':
        sectors_to_filter_by = flask.request.json['sectors_to_filter_by']

    return flask.jsonify(
        fsqs.get_the_number_of_times_stockentities_were_upordown_bypercent_in_year_range(setid, direction,
                                                                                         float(percent),
                                                                                         from_yr, to_yr,
                                                                                         sort_order, top_n,
                                                                                         sectors_to_filter_by))


# @_api.route('/q1/aggregate_post', methods=['POST'])
# def q1_aggregate_post():
#     sectors_to_filter_by = flask.request.json['sectors_to_filter_by']
#     abc=sectors_to_filter_by
#     return "something"

@_api.route('/q1/individual')  # TODO: Only used for url_for in the makeChart JS, need to fix an alternative
@_api.route('/q1/individual/<int:setid>/<int:seid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>')
def q1_individual(setid, seid, direction, percent, from_yr, to_yr):
    return flask.jsonify(
        fsqs.get_the_number_of_times_a_single_stockentity_was_upordown_bypercent_in_year_range(setid, seid,
                                                                                               direction,
                                                                                               float(percent),
                                                                                               from_yr, to_yr))


@_api.route("/test")
def testapi():
    # resp = flask.Response()
    # resp = flask.jsonify(fsqs.get_the_number_of_times_stockentities_were_upordown_bypercent_in_year_range(1, 10, 1993, 2016))
    # resp.headers['Access-Control-Allow-Origin'] = '*'
    return "What the fuck"
