# Basic Verify Bot

This is a basic Discord bot designed for server verification. Originally made for **Ditpo**, but it's open for everyone to use! 🎉

---

## Features

- Sends a verification message with a button.
- Creates private verification channels for users.
- Allows server staff to verify users manually.
- Automatically assigns the "Verified" role upon successful verification.  (you can change this but it's kinda hidden)
- Configurable settings for staff role, allowed users, and verification channels.

---

## Setup Instructions

### Prerequisites

1. **Python 3.8+**  
   Make sure Python is installed on your system. You can download it from [python.org](https://www.python.org/).

2. **Discord Bot Token**  
   Create a bot on the [Discord Developer Portal](https://discord.com/developers/applications) and copy the token.

3. **Dependencies**  
   Install the required Python packages by running:
   ```bash
   pip install discord.py

---

### Installation

1. Clone this repository or download the source code.
   ```bash
   git clone https://github.com/7wlr/verification-bot.git
   cd verification-bot
   ```

2. Open the `bot` code file and replace placeholders:
   - Replace `BOT_TOKEN` with your bot's token.
   - Replace `STAFF_ROLE_ID` with the ID of your server's staff role.
   - Replace `ALLOWED_USER_ID` with your user ID (or someone who hosts the bot).

3. Run the bot:
   ```bash
   python bot.py
   ```

---

### Commands

| Command                | Description                              | Example                                    |
|------------------------|------------------------------------------|--------------------------------------------|
| `/setchannel`          | Sets the verification channel.           | `/setchannel <channel_id>`                |
| `/sendverification`    | Sends the verification message.          | `/sendverification`                       |
| `/verify`              | Verifies a user and assigns a role.      | `/verify @username`                       |

---

### File Structure

```
.
├── bot_data.json
├── main.py
└── README.md
```

---

### Notes

- Ensure the bot has the following permissions:
  - Manage Channels
  - Manage Roles
  - Send Messages
  - Read Messages
  - Use Slash Commands
- The bot will automatically create verification channels for each user.

---

## Contribution

Contributions are welcome! Feel free to fork this repository and submit a pull request.

---

### Credits

- **Developer**: Made by 7wlr.  

Enjoy using this bot! If you run into any issues, feel free to open an issue or contribute a fix.
---
---

### Repository Stars

[![Stars](https://img.shields.io/github/stars/7wlr/verification-bot?style=social)](https://github.com/7wlr/verification-bot/stargazers)
