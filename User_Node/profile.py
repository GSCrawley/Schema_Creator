from flask_jwt_extended import get_jwt_identity
import requests
from flask import jsonify

def profile_data(cloud_url, user):
    try:
        current_user = get_jwt_identity()
        url = f'{cloud_url}/profile'
        data = {'identity': current_user}
        response = requests.post(url, json=data)
        current_user_info = response.json()
        current_user_data = current_user_info[0]['User'][0]['attributes']
        patient.name = current_user_data['first_name']
        patient.DOB = current_user_data['DOB']
        # Other user profile display info...
        return jsonify({'first_name': f'{user.name}', 'DOB': f'{user.DOB}'}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400
