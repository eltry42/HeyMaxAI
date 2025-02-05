from dotenv import load_dotenv
load_dotenv(override=True)

from controller import run_bot_polling
from db import setup_db, shutdown_db

def main():
    print("Starting Process...")
    setup_db()
    run_bot_polling()
    shutdown_db()
    print("Process Terminated")

if __name__ == '__main__':
    main()