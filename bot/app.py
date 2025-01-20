from dotenv import load_dotenv
# from db import setup_db
from controller import run_bot_polling 

load_dotenv(override=True)

def main():
    # setup_db()
    run_bot_polling()

if __name__ == '__main__':
    main()