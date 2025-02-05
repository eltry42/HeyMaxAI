import db

def setup_user(chat_id, user_id, username, first_name, last_name):
    print(f"Setting up user {chat_id} {user_id} {username} {first_name} {last_name}...")
    # if user id in database, update user details
    # else, insert user details

def filter_messages(keywords, offset):
    filter_keywords = list(map(lambda x: f"%{x}%", keywords))
    msg = db.get_messages(filter_keywords, offset)

    full_msg = "Here are the content for the keywords: " + ", ".join(keywords) + "\n\n" + msg if msg else None
    return full_msg