from flask import Flask, render_template, request, jsonify
from model_loader import model
import traceback

app = Flask(__name__)

@app.route('/')
def home():
    """Main landing page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for predictions"""
    try:
        # Get form data
        data = request.get_json()
        
        # Prepare input
        user_input = {
            'funding_total': float(data.get('funding_total', 500000)),
            'funding_rounds': int(data.get('funding_rounds', 2)),
            'startup_age': float(data.get('startup_age', 3)),
            'milestones': int(data.get('milestones', 2)),
            'relationships': int(data.get('relationships', 5)),
            'avg_participants': float(data.get('avg_participants', 2.5)),
            'category': data.get('category', 'software'),
            'region': data.get('region', 'US'),
            'has_vc': 1 if data.get('has_vc') else 0,
            'has_angel': 1 if data.get('has_angel') else 0,
            'has_series_a': 1 if data.get('has_series_a') else 0,
            'is_top500': 1 if data.get('is_top500') else 0,
        }
        
        # Make prediction
        result = model.predict(user_input)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 StartupIQ Analytics Platform")
    print("="*60)
    print("➜ Open browser: http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
