import asyncio
import logging
from app.models import LogEntry
from .database import async_session

BATCH_SIZE = 5
BATCH_INTERVAL = 1  # Time in seconds
BATCH_TIME_LIMIT = 10  # Time limit for batch collection in seconds

async def batch_procesor(message_queue):
    logging.info("Batch processor started.")

    try:
        while True:
            batch = await get_batch(message_queue)
            if batch:
                logging.info(f"Processing batch with {len(batch)} messages.")
                await process_batch(batch)
            await asyncio.sleep(BATCH_INTERVAL)
    except asyncio.CancelledError:
        logging.info("Batch processor stopping...")
    except Exception as e:
        logging.error(f"Batch processor encountered an error: {e}")
    finally:
        logging.info("Batch processor stopped.")

    return message_queue

async def get_batch(message_queue):
    batch = []
    start_time = asyncio.get_running_loop().time()

    while len(batch) < BATCH_SIZE:
        timeout = BATCH_TIME_LIMIT - (asyncio.get_running_loop().time() - start_time)
        if timeout <= 0:
            logging.info("Batch time limit exceeded.")
            break  # Time limit exceeded, process whatever is in the batch

        try:
            message = await asyncio.wait_for(message_queue.get(), timeout=timeout)
            batch.append(message)
        except asyncio.TimeoutError:
            logging.info("Batch time limit reached.")
            break  # Time limit reached, process the batch

    return batch

async def process_batch(batch):
    async with async_session() as session:
        for message in batch:
            log_entry = LogEntry(
                user_id=message["user_id"],
                timestamp=message["timestamp"],
                status=message["status"],
                error_message=message["error_message"],
                request=message["request"],
                response=message["response"]
            )
            session.add(log_entry)
        await session.commit()
        logging.info("Batch committed to the database.")
