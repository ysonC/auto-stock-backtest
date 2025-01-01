from flask import Flask, request, render_template, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello, World!"

# @app.route('/fetch', methods=['POST'])
# def fetch_stocks():
#     stock_id = request.form['stock_id']

#     # Replace this with a call to your stock download and processing script
#     stock_data = [{'date': '2025-01-01', 'price': 123.45, 'per': 15.2}]  # Mocked data

#     return jsonify({
#         'message': f'Stock data fetched for {stock_id}!',
#         'data': stock_data
#     })


if __name__ == '__main__':
    app.run(debug=True)
