import base64
import json
import os
import random
import sys
import time
from urllib.parse import parse_qs, unquote
import requests
from datetime import datetime, timedelta

from wonton import Wonton

def print_(word):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"[{now}] | {word}")

def gets(id):
        tokens = json.loads(open("tokens.json").read())
        if str(id) not in tokens.keys():
            return None
        return tokens[str(id)]

def save(id, token):
        tokens = json.loads(open("tokens.json").read())
        tokens[str(id)] = token
        open("tokens.json", "w").write(json.dumps(tokens, indent=4))

def delete_all():
    open("tokens.json", "w").write(json.dumps({}, indent=4))

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def load_query():
    try:
        with open('wonton_query.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        return queries
    except FileNotFoundError:
        print("File wonton_query.txt not found.")
        return [  ]
    except Exception as e:
        print("Failed get Query :", str(e))
        return [  ]

def parse_query(query: str):
    parsed_query = parse_qs(query)
    parsed_query = {k: v[0] for k, v in parsed_query.items()}
    user_data = json.loads(unquote(parsed_query['user']))
    parsed_query['user'] = user_data
    return parsed_query

def print_delay(delay):
    print()
    while delay > 0:
        now = datetime.now().isoformat(" ").split(".")[0]
        hours, remainder = divmod(delay, 3600)
        minutes, seconds = divmod(remainder, 60)
        sys.stdout.write(f"\r[{now}] | Waiting Time: {round(hours)} hours, {round(minutes)} minutes, and {round(seconds)} seconds")
        sys.stdout.flush()
        time.sleep(1)
        delay -= 1
    print_("Waiting Done, Starting....\n")
       
def main():
    selector_task = input("auto clear task y/n : ").strip().lower()
    selector_game = input("auto play game y/n : ").strip().lower()
    selector_fusion = input("auto fusion wonton y/n : ").strip().lower()
    selector_max = input("basic score wonton *80-100 = y, basic score wonton *50-80 = n : ").strip().lower()
    while True:
        delete_all()
        start_time = time.time()
        delay = 3*3750
        clear_terminal()
        queries = load_query()
        sum = len(queries)
        wonton = Wonton()
        tickets = []
        ton = 0.0
        wton = 0
        for index, query in enumerate(queries, start=1):
            users = parse_query(query).get('user')
            id = users.get('id')
            print_(f"SxG======= Account {index}/{sum} [ {users.get('username')} ] ========SxG")
            print_('generate token...')
            data_login = wonton.login(query)
            ticketCount = data_login.get('ticketCount')
            token = data_login.get('tokens').get('accessToken')
            data_user = data_login.get('user',{})
            tokenBalance = data_user.get('tokenBalance','0')
            withdrawableBalance = data_user.get('withdrawableBalance','0')
            if data_user is not None:
                print_(f"WTON Balance: {tokenBalance}")
                print_(f"TON Balance: {withdrawableBalance}")
                print_(f"Ticket Count: {(data_login['ticketCount'])}")
                wton += int(tokenBalance)
                ton += float(withdrawableBalance)
                wonton.checkin(token)
            
            hasClaimedOkx = data_user.get('hasClaimedOkx',True)
            hasClaimedBinance = data_user.get('hasClaimedBinance',True)
            hasClaimedHackerLeague = data_user.get('hasClaimedHackerLeague',True)
            hasClaimedBitMart = data_user.get('hasClaimedBitMart',True)

            # if hasClaimedOkx == False:
            #     wonton.clear_gift_task(token, "OKX_WALLET")
            
            if hasClaimedBinance == False:
                wonton.clear_gift_task(token, "BINANCE_SIGN_UP")
            
            if hasClaimedHackerLeague == False:
                wonton.clear_gift_task(token, "HACKER_LEAGUE")
                
            if hasClaimedBitMart == False:
                wonton.clear_gift_task(token, "BITMART_SIGN_UP")

            data_farming = wonton.check_farm_status(token)
            if data_farming is not None:
                if data_farming == 'start':
                    wonton.start_farming(token)
                elif data_farming == 'wait':
                    print()
                else:
                    wonton.claim_farming(token)
                    wonton.start_farming(token)

            data_list = wonton.get_list_wonton(token, selector_fusion)
            if data_list is not None:
                stats = data_list.get('data').get('stats')[2]
                ton += float(data_list.get('ton'))
                wton += int(data_list.get('wton'))

            tickets.append({'ticket': ticketCount, 'stats':int(stats)})
        

        for index, query in enumerate(queries):
            mid_time = time.time()
            remaining_time = delay - (mid_time-start_time)
            if remaining_time <= 0:
                break
            users = parse_query(query).get('user')
            id = users.get('id')
            print_(f"SxG======= Account {index+1}/{sum} [ {users.get('username')} ] ========SxG")
            data = tickets[index]
            token = gets(id)

            print_('generate token...')
            data_login = wonton.login(query)
            token = data_login.get('tokens').get('accessToken')
            
            if selector_task == 'y':
                print_('Staring Task...')
                wonton.get_task(token)
            if selector_game == 'y':
                print_('Staring Play Game...')
                ticket = data.get('ticket',0)
                if ticket == 0:
                    print_('No have Ticket To Play')
                else:
                    print_(f'Remaining ticket : {ticket}')
                    stats = data.get('stats')
                    while ticket > 0:
                        
                        game_data = wonton.start_game(token)
                        if game_data:
                            hasBonus = game_data.get('bonusRound',False)
                            print_(f'Bonus Round: {hasBonus}')
                            time.sleep(random.randint(20,25))
                            stats = data.get('stats')
                            rand = random.randint(60, 100)
                            points = rand*stats
                            if selector_max =='y':
                                rand = random.randint(113,151)
                                points = rand*stats
                            finish_data = wonton.finish_game(token, points, hasBonus)
                            if finish_data is not None:
                                ticket -= 1
                                print_(f'Playing game done reward : {points} points')
                                if hasBonus:
                                    print_("Bonus Reward !!")
                                    items = finish_data.get('items',[])
                                    for item in items:
                                        print_(f"Name: {item.get('name')} | Farming Power : {item.get('farmingPower')} | Token Value : {item.get('tokenValue')} WTON | {item.get('value')} TON")
        print()
        print_("============================================")
        print_(f"Total Balance | Wton : {wton} | TON : {ton}")
        print_("============================================")
        end_time = time.time()
        total = delay - (end_time-start_time)
        if total > 0:
            print_delay(total)

if __name__ == "__main__":
     main()