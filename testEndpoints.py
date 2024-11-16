from flask import Flask, jsonify, Response

app = Flask(__name__)

@app.route('/test-anniversary', methods=['GET'])
def test_aniversary():
    chek_users_for_anniversaries()
    return jsonify({'message': 'Test de aniversario enviado - Emails aniversario enviado'}), 200
  
  
  @app.route('/test-inactivity', methods=['GET'])
def test_inactivity():
    check_users_for_inactivity()
    return jsonify({'message': 'Test de inactividad enviado -Emails inactividad enviado'}), 200