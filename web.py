from flask import Flask, request, jsonify, render_template
from app import check_and_download_stocks, clean_downloaded_stocks, check_chromedriver

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_stock', methods=['POST'])
def fetch_stock():
    stock_number = request.form.get('stock_number')
    
    if not stock_number:
        return jsonify({'error': 'Stock number is required'}), 400
    
    try:
        check_chromedriver()

        # Use the provided functions to check and download the stock
        check_and_download_stocks([stock_number])
        clean_result = clean_downloaded_stocks([stock_number])
        
        # Convert the cleaned result to a dictionary for easier display
        cleaned_data = clean_result.to_dict(orient='records')
        return jsonify({'message': 'Stock data fetched and cleaned successfully!', 'data': cleaned_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
