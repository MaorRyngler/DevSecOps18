from flask import Flask, jsonify, session, request
import boto3
from datetime import datetime, timedelta
import threading
import time
import functools
import logging
from botocore.exceptions import ClientError


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

# Store active credentials in memory
aws_credentials = {}

def clear_expired_credentials():
    """Clear expired AWS credentials from memory every minute"""
    while True:
        time.sleep(60)  # Check every minute
        current_time = datetime.utcnow().isoformat() + "Z"
        to_delete = []
        
        for session_id, creds in aws_credentials.items():
            if creds.get("expires_at", "") < current_time:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            if session_id in aws_credentials:
                logger.info(f"Removing expired credentials for session {session_id}")
                del aws_credentials[session_id]

# Start the credential clearing thread
cleanup_thread = threading.Thread(target=clear_expired_credentials, daemon=True)
cleanup_thread.start()

def require_auth(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('session_id')
        if not session_id or session_id not in aws_credentials:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    data = request.json
    required_fields = ["aws_access_key_id", "aws_secret_access_key"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required AWS credential: {field}"}), 400
    
    # Generate a unique session ID
    session_id = f"{datetime.utcnow().timestamp()}"
    expiry_time = datetime.utcnow() + timedelta(minutes=5)
    expires_at = expiry_time.isoformat() + "Z"
    
    # Store credentials in our secure memory store
    aws_credentials[session_id] = {
        "aws_access_key_id": data["aws_access_key_id"],
        "aws_secret_access_key": data["aws_secret_access_key"],
        "aws_region": data.get("aws_region", "us-west-2"),
        "expires_at": expires_at
    }
    
    # Store only the session ID in the Flask session
    session['session_id'] = session_id
    session.permanent = True
    
    logger.info(f"Login successful. Session expires at {expires_at}")
    return jsonify({"expires_at": expires_at})

def boto3_client(service):
    session_id = session.get('session_id')
    if not session_id or session_id not in aws_credentials:
        logger.error(f"No valid session found for service: {service}")
        return None
    
    creds = aws_credentials[session_id]
    try:
        client = boto3.client(
            service,
            aws_access_key_id=creds.get("aws_access_key_id"),
            aws_secret_access_key=creds.get("aws_secret_access_key"),
            region_name=creds.get("aws_region")
        )
        return client
    except Exception as e:
        logger.error(f"Error creating boto3 client for {service}: {str(e)}")
        return None

@app.route('/api/v1/s3/buckets', methods=['GET'])
@require_auth
def list_buckets():
    try:
        client = boto3_client("s3")
        if not client:
            return jsonify({"error": "Failed to create S3 client"}), 500
            
        response = client.list_buckets()
        buckets = [b['Name'] for b in response.get('Buckets', [])]
        return jsonify({
            "count": len(buckets), 
            "buckets": buckets
        })
    except Exception as e:
        logger.error(f"Error listing S3 buckets: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/ecs/clusters', methods=['GET'])
@require_auth
def list_and_describe_clusters():
    try:
        client = boto3_client("ecs")
        if not client:
            return jsonify({"error": "Failed to create ECS client"}), 500
        
        # Handle empty clusters case gracefully
        try:
            list_response = client.list_clusters()
            cluster_arns = list_response.get('clusterArns', [])
            
            if not cluster_arns:
                return jsonify({'message': 'No ECS clusters found', 'count': 0}), 200
            
            # For safety, process clusters in batches of 10 (AWS limit is 100)
            batched_clusters = []
            for i in range(0, len(cluster_arns), 10):
                batch = cluster_arns[i:i+10]
                describe_response = client.describe_clusters(clusters=batch)
                batched_clusters.extend(describe_response.get('clusters', []))
            
            # Return simplified cluster data to avoid potential serialization issues
            simplified_clusters = []
            for cluster in batched_clusters:
                simplified_clusters.append({
                    'clusterArn': cluster.get('clusterArn', ''),
                    'clusterName': cluster.get('clusterName', ''),
                    'status': cluster.get('status', ''),
                    'registeredContainerInstancesCount': cluster.get('registeredContainerInstancesCount', 0),
                    'runningTasksCount': cluster.get('runningTasksCount', 0),
                    'pendingTasksCount': cluster.get('pendingTasksCount', 0),
                    'activeServicesCount': cluster.get('activeServicesCount', 0),
                })
            
            return jsonify({
                'count': len(simplified_clusters),
                'clusters': simplified_clusters
            })
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'AccessDeniedException':
                logger.error(f"AWS ECS access denied: {str(e)}")
                return jsonify({'error': f"AWS ECS access denied: {str(e)}"}), 403
            else:
                logger.error(f"AWS ECS client error: {str(e)}")
                return jsonify({'error': f"AWS ECS client error: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Error listing ECS clusters: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)

