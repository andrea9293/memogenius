import multiprocessing
import uvicorn
from app.telegram_bot import setup_telegram_bot
from app.main import app as fastapi_app

def run_fastapi():
    """Runs the FastAPI server."""
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)

def run_telegram():
    """Runs the Telegram bot."""
    app = setup_telegram_bot()
    app.run_polling()

def run_scheduler():
    """Runs the reminder scheduler."""
    import app.scheduler  # Import here only to start the scheduler
    # Process remains active while scheduler is running
    import time
    while True:
        time.sleep(1)

if __name__ == "__main__":
    # Create processes
    fastapi_process = multiprocessing.Process(target=run_fastapi)
    telegram_process = multiprocessing.Process(target=run_telegram)
    scheduler_process = multiprocessing.Process(target=run_scheduler)

    # Start processes
    fastapi_process.start()
    telegram_process.start()
    scheduler_process.start()

    try:
        fastapi_process.join()
        telegram_process.join()
        scheduler_process.join()
    except KeyboardInterrupt:
        print("\nShutdown in progress...")
        fastapi_process.terminate()
        telegram_process.terminate()
        scheduler_process.terminate()
        fastapi_process.join()
        telegram_process.join()
        scheduler_process.join()
        print("Application terminated.")
