# app.py

from flask import Flask, request, jsonify
from automata_logic import regex_to_nfa, NFA # Import our logic function and class

# Create an instance of the Flask application
app = Flask(__name__)



@app.route('/api/regex-to-nfa', methods=['POST'])
def convert_regex_to_nfa():
    """
    API endpoint to convert a regex string to an NFA.
    Accepts a POST request with a JSON body like: {"regex": "a"}
    """
    # 1. Get the JSON data from the incoming request
    data = request.get_json()

    # 2. Validate the input
    if not data or 'regex' not in data:
        return jsonify({"error": "Invalid request: 'regex' key is missing."}), 400 # Bad Request

    regex_string = data['regex']

    try:
        # 3. Call the core logic from our other file
        nfa_object = regex_to_nfa(regex_string)

        # 4. Convert the result to a dictionary and return it as a JSON response
        return jsonify(nfa_object.to_dict()), 200 # OK

    except ValueError as e:
        # Handle the specific error we defined in our logic for invalid input
        return jsonify({"error": str(e)}), 400 # Bad Request
    except Exception as e:
        # Handle any other unexpected errors
        return jsonify({"error": "An unexpected error occurred."}), 500 # Internal Server Error

# This block allows us to run the app directly with `python app.py`
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)