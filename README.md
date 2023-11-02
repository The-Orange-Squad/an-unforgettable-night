# an-unforgettable-night / Orange Nightmare Discord Bot

Orange Nightmare is a game Discord bot designed specifically for The Orange Squad Discord server. This README provides an overview of the Orange Nightmare Discord bot and its functionality.

## Features

- **Infection Game**: Orange Nightmare hosts an infection-based game where one random member is infected with the "MoneyVirus." The objective of the game is to identify the infected person correctly.

- **Slash Commands**: The bot provides slash commands for interacting with the game:
  - `/search`: Search for a specific pattern within the guild members and receive the percentage of infected members that match the pattern.
  - `/guess`: Attempt to guess the identity of the infected person.

- **Transfer Mechanism**: The infected person can transfer the infection to someone else using the "Transfer" button.

- **Game Rules**: The bot enforces game rules, including a one-hour timer. If the infected person remains unidentified for one hour, they automatically win the game.

- **User Stats**: Orange Nightmare keeps track of user statistics, including the number of successful guesses and searches made, wins and losses as the infected person or guesser, and the successful guess rate.

- **Latency Check**: You can use the `/ping` command to check the bot's latency.

- **User Stats Lookup**: Use the `/user_stats` command to view the game statistics of a specific user.

## Usage

To use Orange Nightmare in your Discord server, follow these steps:

1. Make sure you have Python installed.

2. Install the required packages by running:

   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file and add your Discord bot token. You can obtain this token by creating a bot on the Discord Developer Portal.

   ```
   DISCORD_TOKEN=your_bot_token_here
   ```

4. Customize the bot for your server by modifying the `main.py` file as needed. You can replace the guild and channel IDs and set the desired game rules.

5. Run the bot by executing the `main.py` script:

   ```
   python main.py
   ```

6. Once the bot is running, invite it to your Discord server and set the necessary permissions.

7. Start the game and enjoy!

## Commands

- `/search <pattern>`: Search for a specific pattern in guild members and receive the percentage of infected members matching the pattern.

- `/guess <user>`: Guess the identity of the infected person.

- `/help`: Display the rules of the game.

- `/ping`: Check the bot's latency.

- `/user_stats <user>`: View the game statistics of a specific user.

## Acknowledgments

This bot was built using Py-cord, a Python Discord API wrapper.

Feel free to customize and extend the bot's functionality to suit your Discord server's needs.

Enjoy the game! If you have any questions or need assistance, please submit a new issue. I will be more than happy to help you out.

## Our Discord Server

Join The Orange Squad Discord server to play the game and have fun with other members!

[The Orange Squad Discord Server](https://discord.gg/XkjPDcSfNz)