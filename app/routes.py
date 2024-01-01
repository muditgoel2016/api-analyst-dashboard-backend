from quart import Blueprint, jsonify, request
from datetime import datetime, timezone
import logging
import json
# from .batch_processor import message_queue
from sqlalchemy import select, func, distinct, case
from .models import LogEntry
from .database import async_session
from dateutil.parser import parse

main = Blueprint('main', __name__)

LIMIT = 10

# Helper Functions
async def serialize_request(req):
    """ Serialize the request object to a JSON string. """
    request_data = await req.get_data(as_text=True)
    return json.dumps({
        "method": req.method,
        "data": request_data,
        "args": req.args.to_dict()
    })

async def serialize_response(resp):
    """ Serialize the response object to a JSON string. """
    response_data = await resp.get_json()
    return json.dumps({
        "status_code": resp.status_code,
        "data": response_data
    })

async def log_and_create_error(session, message, user_id, status):
    """ Log error and create log entry in database """
    logging.error(f"{message} User ID: {user_id}")
    error_response = jsonify(error="An error occurred", message=message)

    # Call the serialize functions and await their results
    serialized_request = await serialize_request(request)
    serialized_response = await serialize_response(error_response)

    # Await the create_log_entry coroutine
    await create_log_entry(session, user_id, datetime.now(timezone.utc), status, message, serialized_request, serialized_response)
    # await queue_log_entry(session, user_id, datetime.now(timezone.utc), status, message, serialized_request, serialized_response)

    return error_response

# async def queue_log_entry(session, user_id, timestamp, status, error_message, serialized_request, serialized_response):
#     """ Queue a log entry for batch processing """

#     # Convert timestamp to offset-naive UTC datetime if it's offset-aware
#     if timestamp.tzinfo is not None and timestamp.tzinfo.utcoffset(timestamp) is not None:
#         timestamp = timestamp.replace(tzinfo=None)

#     message_queue = current_app.config['message_queue']

#     await message_queue.put({
#         "user_id": user_id,
#         "timestamp": timestamp,
#         "status": status,
#         "error_message": error_message,
#         "request": serialized_request,
#         "response": serialized_response
#     })

async def create_log_entry(session, user_id, timestamp, status, error_message, serialized_request, serialized_response):
    """ Create a log entry in the database asynchronously """

    # Convert timestamp to offset-naive UTC datetime if it's offset-aware
    if timestamp.tzinfo is not None and timestamp.tzinfo.utcoffset(timestamp) is not None:
        timestamp = timestamp.replace(tzinfo=None)

    log_entry = LogEntry(
        user_id=user_id, 
        timestamp=timestamp, 
        status=status, 
        error_message=error_message, 
        request=serialized_request, 
        response=serialized_response
    )
    session.add(log_entry)
    await session.commit()

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
    """Parse ISO format datetime string and convert to offset-naive UTC datetime."""
    try:
        # Check if 'Z' is in the string, indicating UTC timezone
        if 'Z' in iso_str:
            iso_str = iso_str.replace('Z', '+00:00')
        parsed_datetime = datetime.fromisoformat(iso_str)
        if parsed_datetime.tzinfo is not None:
            # Convert to UTC and then make it offset-naive
            parsed_datetime = parsed_datetime.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed_datetime
    except ValueError as e:
        logging.error(f"Invalid ISO datetime format: {iso_str}, Error: {e}")
        return None

async def aggregate_activity_data(session, start_time, end_time, limit):
    """Aggregate user activity data asynchronously."""
    selected_tz_name = request.args.get('selectedTzName', 'UTC')
    logging.info(f"Selected tz name: {selected_tz_name}")

    # Define the expressions
    date_expr = func.date(func.timezone(selected_tz_name, func.timezone('UTC', LogEntry.timestamp)))
    total_calls_expr = func.count(LogEntry.user_id)
    unique_users_expr = func.count(distinct(LogEntry.user_id))
    total_failures_expr = func.sum(case((LogEntry.status == 'Failure', 1), else_=0))

    # Construct the query
    query = select(
        date_expr.label('date'),
        total_calls_expr.label('total_calls'),
        unique_users_expr.label('unique_users'),
        total_failures_expr.label('total_failures')
    ).where(
        LogEntry.timestamp >= start_time,
        LogEntry.timestamp <= end_time
    ).group_by(
        date_expr
    ).limit(limit)

    result = await session.execute(query)
    data = [{
        'date': row.date,
        'total_calls': row.total_calls,
        'unique_users': row.unique_users,
        'total_failures': row.total_failures
    } for row in result.all()]
    return data

def get_pagination_params():
    """ Extract pagination parameters from request """
    first_id = request.args.get('firstId', type=int)
    return first_id

async def fetch_logs(session, start_time, end_time, first_id, limit):
    """Fetch detailed logs with pagination and return next first id asynchronously."""
    log_query = select(LogEntry).where(
        LogEntry.timestamp >= start_time, 
        LogEntry.timestamp <= end_time
    )
    if first_id:
        log_query = log_query.where(LogEntry.id >= first_id)
    log_query = log_query.order_by(LogEntry.id)

    result = await session.execute(log_query.limit(limit + 1))
    logs = result.scalars().all()

    next_first_id = None
    if len(logs) > limit:
        next_first_id = logs[-1].id
        logs = logs[:-1]

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

async def fetch_aggregate_stats(session, start_time, end_time):
    """Fetch aggregate statistics and total log count asynchronously."""

    # Define the expressions
    unique_users_expr = func.count(distinct(LogEntry.user_id))
    total_calls_expr = func.count(LogEntry.id)
    total_failures_expr = func.sum(case((LogEntry.status == 'Failure', 1), else_=0))

    # Construct the query
    query = select(
        unique_users_expr.label('unique_users'),
        total_calls_expr.label('total_calls'),
        total_failures_expr.label('total_failures')
    ).where(
        LogEntry.timestamp >= start_time, 
        LogEntry.timestamp <= end_time
    )

    result = await session.execute(query)
    stats_result = result.one()
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

# Async route handlers
@main.route('/api/hello-world', methods=['POST'])
async def hello_world():
    timestamp = datetime.now(timezone.utc)
    user_id = 'Unknown'  # Default value for user_id
    try:
        async with async_session() as session:
            json_data = await request.get_json()  # Correct way to get JSON data
            if not json_data:
                return await log_and_create_error(session, "No JSON payload provided.", 'Unknown', "Failure"), 400
            user_id = json_data.get('user_id') 

            if not user_id:
                return await log_and_create_error(session, "User ID is required.", 'Unknown', "Failure"), 400

            response_data = jsonify({"message": "Hello, World!", "user_id": user_id})
            serialized_request = await serialize_request(request)
            serialized_response = await serialize_response(response_data)
            await create_log_entry(session, user_id, timestamp, "Success", None, serialized_request, serialized_response)
            # await queue_log_entry(session, user_id, timestamp, "Success", None, serialized_request, serialized_response)
            logging.info(f"Success - Timestamp: {timestamp}, User ID: {user_id}")
            return response_data, 200
    except Exception as e:
        error_message = f"Exception: {str(e)}"
        logging.error(error_message + f" - Timestamp: {timestamp}, User ID: {user_id}", exc_info=True)
        error_response = jsonify(error="An error occurred", message=error_message)
        async with async_session() as session:
            serialized_request = await serialize_request(request)
            serialized_response = await serialize_response(error_response)
            await create_log_entry(session, user_id, timestamp, "Failure", error_message, serialize_request, serialize_response)
            # await queue_log_entry(session, user_id, timestamp, "Failure", error_message, serialize_request, serialize_response)
            await session.rollback()  # Explicit rollback in case of an exception
        return error_response, 500

@main.route('/api/activity', methods=['GET'])
async def user_activity():
    time_range, error = get_time_range()
    if error:
        return jsonify(error="Invalid time range", message=error), 400

    start_time, end_time = time_range
    if not is_valid_time_range(start_time, end_time):
        return jsonify(error="Invalid time range", message="Start time must be earlier than end time."), 400

    async with async_session() as session:
        data = await aggregate_activity_data(session, start_time, end_time, 10000)
        return jsonify(data), 200

@main.route('/api/combined-analytics', methods=['GET'])
async def combined_analytics():
    time_range, error = get_time_range()
    if error:
        return jsonify(error="Invalid time range", message=error), 400

    start_time, end_time = time_range
    if not is_valid_time_range(start_time, end_time):
        return jsonify(error="Invalid time range", message="Start time must be earlier than end time."), 400

    async with async_session() as session:
        logs, next_first_id = await fetch_logs(session, start_time, end_time, get_pagination_params(), LIMIT)
        total_stats = await fetch_aggregate_stats(session, start_time, end_time)

    combined_response = {"logs": logs, "total": total_stats, "next_first_id": next_first_id}
    return jsonify(combined_response), 200
