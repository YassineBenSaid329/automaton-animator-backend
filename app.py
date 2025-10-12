# app.py

from flask import Flask, request, jsonify
# --- NEW: Import the single, clean entry point from our new 'logic' package ---
from logic import regex_to_nfa

app = Flask(__name__)

@app.route('/api/regex-to-nfa', methods=['POST'])
def convert_regex_to_nfa_endpoint():
    data = request.get_json()
    if not data or 'regex' not in data:
        return jsonify({"error": "Invalid request: 'regex' key is missing."}), 400

    regex_string = data['regex']

    try:
        # One simple, clean call to our robust, multi-stage logic package.
        nfa_object = regex_to_nfa(regex_string)
        # The .to_dict() method is part of the NFA class, which is correctly returned.
        return jsonify(nfa_object.to_dict()), 200

    except ValueError as e:
        # This now cleanly catches both empty strings and any RegexSyntaxError
        # that our logic package has converted to a ValueError.
        return jsonify({"error": str(e)}), 400
    except Exception:
        # For any other unexpected crash, log it for the developer
        # and return a generic 500 error to the user.
        # import traceback
        # traceback.print_exc()
        return jsonify({"error": "An unexpected server error occurred."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)