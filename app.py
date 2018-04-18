from configuration import config

import requests
from flask import Flask, request, jsonify
import googlemaps
from datetime import datetime

app = Flask(__name__)


@app.route("/routes", methods=["GET"])
def find_route():
    key = request.args.get("key")
    origin = request.args.get("origin")
    destination = request.args.get("destination")

    # origin = "5.5985513, -0.2234973"
    # destination = "5.606176, -0.248757"

    gmaps = googlemaps.Client(key=key)

    now = datetime.now()

    stops, total_path, status, message = trosky_api(origin, destination)

    if status == 202:
        # stops = remove_duplicate(stops)
        # chunks = [waypoints[x:x + 23] for x in range(0, len(waypoints), 23)]

        final_data = {"status": status,
                      "routes": [],
                      "stops": stops,
                      "message": message}

        for path in total_path:

            start = path.get("path")[0]
            end = path.get("path")[-1]
            path_list = path.get("path")
            if path.get("bus_id") is 0:
                pass

                # arr = []
                # directions_result = gmaps.directions(origin =start,
                #                                      destination=end,
                #                                      mode="walking",
                #                                      departure_time=now)
                # arr.append(directions_result[0])
                # final_data["routes"].append(arr)

            else:

                arr = []

                if len(path.get("path")) <= 23:
                    directions_result = gmaps.directions(origin=start,
                                                         destination=end,
                                                         waypoints=path_list,
                                                         departure_time=now)
                    arr.append(directions_result[0])
                else:
                    sub_paths = [path_list[x:x + 23] for x in range(0, len(path_list), 23)]

                    for i in sub_paths:
                        directions_result = gmaps.directions(origin=start,
                                                             destination=end,
                                                             waypoints=i,
                                                             departure_time=now)
                        arr.append(directions_result[0])

                final_data["routes"].append(arr)


            # if path.get("bus_name") is "Walkable":
            #
            #     directions_result = gmaps.directions(origin=origin,
            #                                          destination=destination,
            #                                          mode="walking",
            #                                          departure_time=now)
            #
            #     final_data["routes"].append(directions_result[0])
            #
            # else:
            #
            #     directions_result = gmaps.directions(origin=origin,
            #                                          destination=destination,
            #                                          mode="transit",
            #                                          departure_time=now)
            #     print(directions_result)
            #     final_data["routes"].append(directions_result[0])

        return jsonify(final_data)

    return jsonify({"status": status,
                    "routes": [],
                    "stops": stops,
                    "message": message})


@app.route("/closeBusStops", methods=["GET"])
def get_close_bus_stops():
    """Getting close bus stops.

    This route returns a list of the closest to a particular location
    @:param origin: location you want to get the closest bus stops from
    :return: Json List of 4 buse stops
    """
    origin = request.args.get("origin")

    url = "https://cryptic-mountain-86599.herokuapp.com/getClosestStops?location={}".format(origin)
    response = requests.get(url)
    response = response.json()

    bus_stops = {"status": response.get("status"),
                 "message": response.get("message"),
                 "busStop": []}

    for stop in response.get("busStops"):
        temp = {"stop_location": stop.get("busStopLocation"),
                "stop_name": stop.get("busStopName")}
        bus_stops["busStop"].append(temp)

    return jsonify(bus_stops)


def trosky_api(origin, destination):
    trosky_url = "https://cryptic-mountain-86599.herokuapp.com/getRoute?origin={}&destination={}".format(origin,
                                                                                                         destination)
    r = requests.get(trosky_url)
    r = r.json()

    route_path = []
    stops = []

    message = r.get("message")
    status = r.get("status")

    if status == 202:

        buses = r.get("buses")

        for path in r.get("paths"):

            bus_id = path.get("busId")

            if bus_id is 0:
                bus_name = "WALKING"
            else:
                bus_name = buses[bus_id - 1].get("busName")

            first_stop_location = path.get("busStopsList")[0].get("busStopLocation")
            first_stop_name = path.get("busStopsList")[0].get("busStopName")

            # last_stop_location = path.get("busStopsList")[-1].get("busStopLocation")
            # last_stop_name = path.get("busStopsList")[-1].get("busStopName")

            single_path = []
            for bus_stop in path.get("busStopsList"):
                single_path.append(bus_stop.get("busStopLocation"))

            single_path = {"bus_id": bus_id,
                           "path": single_path,
                           }

            route_path.append(single_path)

            stop = {"bus_name": bus_name,
                    "stop_location": first_stop_location,
                    "stop_name": first_stop_name}

            stops.append(stop)

        last_path = r.get("paths")[-1]

        last_stop = {"bus_name": "WALKING",
                    "stop_location": last_path.get("busStopsList")[-1].get("busStopLocation"),
                    "stop_name": last_path.get("busStopsList")[-1].get("busStopName")}

        stops.append(last_stop)

    return stops, route_path, status, message


def remove_duplicate(raw_data):
    list = []
    result = []

    for item in raw_data:
        if item["stop_location"] not in list:
            result.append(item)
            list.append(item["stop_location"])

    return result


if __name__ == "__main__":
    app.run(debug=True)

    # if len(i) <= 23:
    #     directions_result = gmaps.directions(origin=i[0],
    #                                          destination=i[-1],
    #                                          waypoints=i,
    #                                          departure_time=now)
    #     final_data["routes"].append(directions_result[0])
    # else:
    #     chunks = [i[x:x + 23] for x in range(0, len(waypoints), 23)]
    #
    #     for j in chunks:
    #         directions_result = gmaps.directions(origin=i[0],
    #                                              destination=i[-1],
    #                                              waypoints=i,
    #                                              departure_time=now)
    #     final_data["routes"].append(directions_result[0])

    # for i in chunks:
    #     directions_result = gmaps.directions(origin=i[0],
    #                                          destination=i[-1],
    #                                          waypoints=i,
    #                                          departure_time=now)
    #     final_data["routes"].append(directions_result[0])
