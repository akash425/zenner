"""
Simple Flask API to serve analytics results from MongoDB.
"""
import sys
from pathlib import Path
from flask import Flask, jsonify

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add paths for imports
project_root = Path(__file__).parent.parent.parent
shared_path = project_root / 'shared'

# Ensure shared path is in sys.path
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

# Also add project root for config.ini access
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from mongo.mongo_client import get_manager
from config.config import Config

app = Flask(__name__)

# Initialize configuration
try:
    config = Config()
except FileNotFoundError as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)


def get_analytics_collection():
    """Get analytics collection from MongoDB."""
    manager = get_manager()
    db_name = config.get_database_name()
    collection_name = config.get_analytics_collection_name()
    return manager.get_collection(collection_name, db_name)


@app.route('/analytics/top-devices', methods=['GET'])
def get_top_devices():
    """Get top active devices."""
    try:
        collection = get_analytics_collection()
        result = collection.find_one({'analytics_type': 'top_active_devices'})
        
        if result and 'results' in result:
            return jsonify({
                'success': True,
                'data': result['results'],
                'computed_at': result.get('computed_at')
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No data available'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/analytics/weak-devices', methods=['GET'])
def get_weak_devices():
    """Get weak signal devices."""
    try:
        collection = get_analytics_collection()
        result = collection.find_one({'analytics_type': 'weak_signal_devices'})
        
        if result and 'results' in result:
            return jsonify({
                'success': True,
                'data': result['results'],
                'computed_at': result.get('computed_at')
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No data available'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/analytics/gateway-stats', methods=['GET'])
def get_gateway_stats():
    """Get gateway environment statistics."""
    try:
        collection = get_analytics_collection()
        result = collection.find_one({'analytics_type': 'gateway_environment_stats'})
        
        if result and 'results' in result:
            return jsonify({
                'success': True,
                'data': result['results'],
                'computed_at': result.get('computed_at')
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No data available'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/analytics/duplicates', methods=['GET'])
def get_duplicates():
    """Get devices with duplicate records."""
    try:
        collection = get_analytics_collection()
        result = collection.find_one({'analytics_type': 'duplicate_devices'})
        
        if result and 'results' in result:
            return jsonify({
                'success': True,
                'data': result['results'],
                'computed_at': result.get('computed_at')
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No data available'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/analytics/high-temperature', methods=['GET'])
def get_high_temperature():
    """Get high temperature records."""
    try:
        collection = get_analytics_collection()
        result = collection.find_one({'analytics_type': 'high_temperature_records'})
        
        if result:
            return jsonify({
                'success': True,
                'data': {
                    'result_count': result.get('result_count', 0),
                    'output_file': result.get('output_file'),
                    'parameters': result.get('parameters', {})
                },
                'computed_at': result.get('computed_at')
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No data available'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

