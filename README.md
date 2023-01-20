# Trading bot for site buff
Telegram bot for trading on buff website. This parser looks for suitable skins to buy, buys if something is suitable and sends a message to tg about it.
Used for buying sking with rare float for craft or sell. Also, bot can send the found skin to the tg group for data analysis.
## How to use 
Configure json_skins.json file, add or remove skins for buying, example is given. Start main.py script, through tg start parsing via button parse, see /star command.
## Available parameters for skins filter
- float range - Float value. Float range in which skin will be bought. Float is variable wich show how much skin is scraped.
- price up - Float value. Upper price threshold for buying a skin.
- buy - Boolean value. Buy skin or not.
