from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta, timezone
import logging
from sqlalchemy import func, distinct, case
import json
from app import db
from .models import LogEntry

main = Blueprint('main', __name__)

LIMIT = 10

# Helper Functions
def serialize_request(req):
    """ Serialize the request object to a JSON string. """
    return json.dumps({
        "method": req.method,
        "data": req.get_data(as_text=True),
        "args": req.args.to_dict()
    })

def serialize_response(resp):
    """ Serialize the response object to a JSON string. """
    return json.dumps({
        "status_code": resp.status_code,
        "data": resp.get_json()
    })

def validate_user_id(user_id):
    """ Validate user_id from the request """
    if not user_id:
        log_and_create_error("User ID is required.", 'Unknown', "Failure")
        return False
    return True

def log_and_create_error(message, user_id, status):
    """ Log error and create log entry in database """
    logging.error(f"{message} User ID: {user_id}")
    error_response = jsonify(error="An error occurred", message=message)
    create_log_entry(user_id, datetime.now(timezone.utc), status, message, serialize_request(request), serialize_response(error_response))
    return error_response

def create_log_entry(user_id, timestamp, status, error_message, serialized_request, serialized_response):
    """ Create a log entry in the database """
    log_entry = LogEntry(
        user_id=user_id, 
        timestamp=timestamp, 
        status=status, 
        error_message=error_message, 
        request=serialized_request, 
        response=serialized_response
    )
    db.session.add(log_entry)
    db.session.commit()

def get_time_range():
    """Extract and validate start and end time parameters from request."""
    start_time = request.args.get('startTime')
    end_time = request.args.get('endTime')

    if not start_time or not end_time:
        missing_params = []
        if not start_time:
            missing_params.append('startTime')
        if not end_time:
            missing_params.append('endTime')
        return None, f"Missing parameters: {', '.join(missing_params)}"

    # Convert to datetime objects, handling 'Z' timezone
    start_time = parse_iso_datetime(start_time)
    end_time = parse_iso_datetime(end_time)

    if start_time is None or end_time is None:
        return None, "Invalid datetime format in startTime or endTime."

    return (start_time, end_time), None

def parse_iso_datetime(iso_str):
    """Parse ISO format datetime string and error out if no timezone info is present."""
    try:
        # Check if 'Z' is in the string, indicating UTC timezone
        if 'Z' in iso_str:
            # Replace 'Z' with '+00:00' to make it compatible with fromisoformat
            iso_str = iso_str.replace('Z', '+00:00')

        parsed_datetime = datetime.fromisoformat(iso_str)

        # Error out if no timezone info is present
        if parsed_datetime.tzinfo is None:
            raise ValueError("No timezone information present in the ISO datetime string.")

        return parsed_datetime.astimezone(timezone.utc)
    except ValueError as e:
        logging.error(f"Invalid ISO datetime format: {iso_str}, Error: {e}")
        return None

def aggregate_activity_data(start_time, end_time, limit):
    """ Aggregate user activity data """
    # Get selected timezone name from request parameters
    selected_tz_name = request.args.get('selectedTzName', 'UTC')  # Default to 'UTC' if not provided
    logging.info(f"Selected tz name: {selected_tz_name}")
    logging.info(f"start time: {start_time}")
    entries = LogEntry.query.all()  # Or some other query
    for entry in entries:
        logging.info(f"Selected timestamp: {entry.timestamp}")
    # Ensure start_time and end_time are in UTC for filtering

    query = db.session.query(
            func.date(func.timezone(selected_tz_name, func.timezone('UTC', LogEntry.timestamp))).label('date'),
            func.count(LogEntry.user_id).label('total_calls'),
            func.count(distinct(LogEntry.user_id)).label('unique_users'),
            func.sum(case((LogEntry.status == 'Failure', 1), else_=0)).label('total_failures')
        ).filter(
            LogEntry.timestamp >= start_time, 
            LogEntry.timestamp <= end_time
        ).group_by(
            'date'
        ).limit(limit)

    results = query.all()

    # Convert Row objects to dictionaries
    data = [row._asdict() for row in results]
    return data

def get_pagination_params():
    """ Extract pagination parameters from request """
    first_id = request.args.get('firstId', type=int)
    return first_id

def fetch_logs(start_time, end_time, first_id, limit):
    """ Fetch detailed logs with pagination and return next first id """
    log_query = db.session.query(LogEntry)
    log_query = log_query.filter(LogEntry.timestamp >= start_time, LogEntry.timestamp <= end_time)
    if first_id:
        log_query = log_query.filter(LogEntry.id >= first_id)
    log_query = log_query.order_by(LogEntry.id)

    # Fetching one extra record
    logs = log_query.limit(limit + 1).all()

    next_first_id = None
    # Check if an extra record was fetched
    if len(logs) > limit:
        next_first_id = logs[-1].id
        logs = logs[:-1]  # Exclude the extra record from the returned list

    serialized_logs = [{
        'id': entry.id,
        'user_id': entry.user_id,
        'timestamp': entry.timestamp.isoformat(),
        'status': entry.status,
        'error_message': entry.error_message,
        'request': entry.request,
        'response': entry.response
    } for entry in logs]

    return serialized_logs, next_first_id

def fetch_aggregate_stats(start_time, end_time):
    """ Fetch aggregate statistics and total log count """
    stats_query = db.session.query(
        func.count(distinct(LogEntry.user_id)).label('unique_users'),
        func.count(LogEntry.id).label('total_calls'),
        func.sum(case((LogEntry.status == 'Failure', 1), else_=0)).label('total_failures'),
    ).filter(LogEntry.timestamp >= start_time, LogEntry.timestamp <= end_time)

    stats_result = stats_query.one()
    return {
        "calls": stats_result.total_calls,
        "failures": stats_result.total_failures,
        "unique_users": stats_result.unique_users,
        "total_logs": stats_result.total_calls
    }

def is_valid_time_range(start_time, end_time):
    """ Check if the start time is earlier than the end time and log the values. """
    logging.info(f"Start time: {start_time}, Type: {type(start_time)}")
    logging.info(f"End time: {end_time}, Type: {type(end_time)}")
    return start_time < end_time

# ============== End-points =====================
@main.route('/api/hello-world', methods=['POST'])
def hello_world():
    if not request.json:
        return log_and_create_error("No JSON payload provided.", 'Unknown', "Failure"), 400
    
    user_id = request.json.get('user_id')
    timestamp = datetime.now(timezone.utc).isoformat()

    if not validate_user_id(user_id):
        return log_and_create_error("User ID is required.", 'Unknown', "Failure"), 400

    try:
        response_data = jsonify({"message": "Hello, World!", "user_id": user_id})
        create_log_entry(user_id, timestamp, "Success", None, serialize_request(request), serialize_response(response_data))
        logging.info(f"Success - Timestamp: {timestamp}, User ID: {user_id}")
        return response_data, 200
    except Exception as e:
        db.session.rollback()
        error_message = f"Exception: {str(e)}"
        logging.error(error_message + f" - Timestamp: {timestamp}, User ID: {user_id}", exc_info=True)
        error_response = jsonify(error="An error occurred", message=error_message)
        create_log_entry(user_id, timestamp, "Failure", error_message, serialize_request(request), serialize_response(error_response))
        return error_response, 500

    finally:
        db.session.close()

@main.route('/api/activity', methods=['GET'])
def user_activity():
    time_range, error = get_time_range()
    if error:
        return jsonify(error="Invalid time range", message=error), 400

    start_time, end_time = time_range
    if not is_valid_time_range(start_time, end_time):
        return jsonify(error="Invalid time range", message="Start time must be earlier than end time."), 400

    data = aggregate_activity_data(start_time, end_time, 10000)
    return jsonify(data), 200

@main.route('/api/combined-analytics', methods=['GET'])
def combined_analytics():
    time_range, error = get_time_range()
    if error:
        return jsonify(error="Invalid time range", message=error), 400

    start_time, end_time = time_range
    if not is_valid_time_range(start_time, end_time):
        return jsonify(error="Invalid time range", message="Start time must be earlier than end time."), 400

    logs, next_first_id = fetch_logs(start_time, end_time, get_pagination_params(), LIMIT)
    total_stats = fetch_aggregate_stats(start_time, end_time)

    combined_response = {"logs": logs, "total": total_stats, "next_first_id": next_first_id}
    return jsonify(combined_response), 200
