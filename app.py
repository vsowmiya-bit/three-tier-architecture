import os
from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

# Fetch RDS configuration from environment variables
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'admin')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'admin1234')
DB_NAME = os.environ.get('DB_NAME', 'webappdb')

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "tier": "application"}), 200

@app.route('/api/feedback', methods=['POST'])
def add_feedback():
    data = request.get_json()
    name = data.get('name')
    message = data.get('message')

    if not name or not message:
        return jsonify({"message": "Name and message are required"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "INSERT INTO feedback (name, message) VALUES (%s, %s)"
            cursor.execute(sql, (name, message))
        connection.commit()
        connection.close()
        return jsonify({"message": "Feedback inserted successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, message, created_at FROM feedback ORDER BY id DESC")
            records = cursor.fetchall()
        connection.close()
        return jsonify(records), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
