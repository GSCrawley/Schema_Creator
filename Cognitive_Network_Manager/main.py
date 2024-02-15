from flask import Flask, jsonify, request
app = Flask(__name__)

# Simulated storage for user preferences and task status
user_preferences = {}
task_status = {}

@app.route('/user/preferences', methods=['POST'])
def set_user_preferences():
    data = request.json
    user_id = data['user_id']
    preferences = data['preferences']
    user_preferences[user_id] = preferences
    # Here, you would have logic to communicate preferences to the Knowledge Acquisition Node
    return jsonify({'message': 'Preferences updated successfully'}), 200

@app.route('/task/status', methods=['GET'])
def get_task_status():
    user_id = request.args.get('user_id')
    status = task_status.get(user_id, 'No task found for this user')
    return jsonify({'user_id': user_id, 'status': status}), 200

if __name__ == '__main__':
    app.run(debug=True)
