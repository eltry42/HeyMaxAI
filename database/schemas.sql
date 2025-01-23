CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    chat_id BIGINT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Channels (
    channel_id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    scrape_status BOOLEAN DEFAULT FALSE,
    last_scraped_at TIMESTAMP
);

CREATE TABLE ScrapedMessages (
    message_id SERIAL PRIMARY KEY,
    channel_id INT REFERENCES Channels(channel_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    media_url TEXT,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE BotInteractions (
    interaction_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    command TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    upvote INT DEFAULT 0,
    downvote INT DEFAULT 0
);
