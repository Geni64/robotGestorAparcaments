from flask import Flask, jsonify, request

app = Flask(__name__)

# Initial values
actuators_values = {
    "m1a": 0, "m1b": 0,
    "m2a": 0, "m2b": 0,
    "m3a": 0, "m3b": 0,
    "m4a": 0, "m4b": 0,
    "s1":  0, "s2":  0
}

@app.route('/get', methods=['GET'])
def send_bits():
    bits_value = ""
    for key in actuators_values:
        if key not in ("s1", "s2"):
            bits_value += str(actuators_values[key])
        else:
            bits_value += bin(actuators_values[key])[2:].zfill(8)

    return jsonify({"bits": bits_value})

@app.route('/set-orders', methods=['POST'])
def set_states():
    print("Headers:", request.headers)
    print("Raw data:", request.data)
    print("Is JSON?", request.is_json)

    if not request.is_json:
        return "Request content-type must be application/json", 400

    data = request.get_json()
    print("Parsed JSON:", data)

    for key in data:
        if key in actuators_values and type(data[key]) == int:
            actuators_values[key] = data[key]
    return jsonify(actuators_values)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
