from multiprocessing import Process, Queue, Pipe

import scraping
import tele_buff_bot


def run_scraper(queue, flag_queue):
    scraper = scraping.SkinScraper(queue, flag_queue)
    scraper.start_scraping()


def run_buff_bot(queue, flag_queue):
    buffbot = tele_buff_bot.BuffTeleBot(queue, flag_queue)
    buffbot.start_bot()


def run_shit_bot_2_0():
    # Queue will transfer skin message to telebot
    message_queue = Queue()

    # flag Queue
    flag_queue = Queue()

    buffbot_p = Process(target=run_buff_bot, args=(message_queue, flag_queue))
    buffbot_p.start()

    scraper_p = Process(target=run_scraper, args=(message_queue, flag_queue))
    scraper_p.start()

    buffbot_p.join()
    scraper_p.join()

    print('\nrun_buff_bot done!\n')


if __name__ == '__main__':
    run_shit_bot_2_0()
