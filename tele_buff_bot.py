from multiprocessing import Queue

import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import types


class BuffTeleBot:
    buff_bot: AsyncTeleBot
    message_queue: Queue
    running_flag_q: Queue

    def __init__(self, message_q=None, flag_queue=None):
        self.buff_bot = AsyncTeleBot("bot key")
        self.message_queue = message_q
        self.running_flag_q = flag_queue

        @self.buff_bot.message_handler(commands=['start', 'help'])
        async def send_welcome(message):
            await self.buff_bot.send_message(chat_id=message.chat.id, text="Howdy, how are you doing?",
                                             reply_markup=self.help_markup())

        @self.buff_bot.callback_query_handler(func=lambda call: call.data.startswith('help_'))
        async def help_callback_query(call):
            if call.data == 'help_parse':
                await start_parsing(call.message.chat.id)
            elif call.data == 'help_status':
                await self.send_parse_status(call.message.chat.id)
            elif call.data == 'help_stop':
                await stop_parsing(call.message.chat.id)
            elif call.data == 'help_about':
                await self.send_group_message(
                    "Trading bot for buff.163, uses selenium as a parser. Automatically buy a skin with given parameters(float,price).\n",
                    "Telebot and parser work in different process, means u can have as many parsers as ur system allows. Telebot works asynchronously\n",
                    "Parser can be easily upgraded to use proxy avoiding being detected by buff.163 as bot, for buying skins with float 0.0001 - (usually in the first 1000 in the world)")

        @self.buff_bot.message_handler(commands=['send'])
        async def send_start_message(message):
            await print("sending test message")
            await self.buff_bot.send_message(chat_id=message.chat.id, text="test message")

        @self.buff_bot.message_handler(commands=['parse'])
        async def start_parsing(chat_id):
            await self.buff_bot.send_message(chat_id=chat_id, text="starting parsing process")
            self.running_flag_q.put(True)

        @self.buff_bot.message_handler(commands=['stop'])
        async def stop_parsing(chat_id):
            await self.buff_bot.send_message(chat_id=chat_id, text="stop parsing process")
            self.running_flag_q.get()

    async def send_parse_status(self, chat_id):
        if not self.running_flag_q.empty():
            await self.buff_bot.send_message(chat_id=chat_id, text="it is busy 🤓")
        else:
            await self.buff_bot.send_message(chat_id=chat_id, text="nah, it is sleep 🛏")

    async def send_group_message(self, message):
        try:
            await self.buff_bot.send_message(chat_id=1, text=message)
        except Exception:
            await self.buff_bot.send_message(chat_id=1, text=message)

    async def send_skins(self):
        while True:
            if not self.message_queue.empty():
                qsize = self.message_queue.qsize()
                for i in range(qsize):
                    await self.send_group_message(self.message_queue.get())
            await asyncio.sleep(2)

    async def bot_polling(self):
        task_1 = asyncio.create_task(self.send_skins())
        task_2 = asyncio.create_task(self.buff_bot.polling())

        await task_1
        await task_2

    @staticmethod
    def help_markup():
        # in case of adding buttons by if/else
        buttons = []

        buttons.append(types.InlineKeyboardButton("Status 🤓", callback_data="help_status"))
        buttons.append(types.InlineKeyboardButton("Parse 🤓", callback_data="help_parse"))
        buttons.append(types.InlineKeyboardButton("Stop parse 😳", callback_data="help_stop"))
        buttons.append(types.InlineKeyboardButton("About 🫥😎", callback_data="help_about"))

        help_message_markup = types.InlineKeyboardMarkup()
        for button in buttons:
            help_message_markup.add(button)

        return help_message_markup

    def start_bot(self):
        print('starting buffTeleBot\n')
        asyncio.run(self.bot_polling())


if __name__ == '__main__':
    bot = BuffTeleBot()
    bot.start_bot()
