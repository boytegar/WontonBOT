import random
import string
import requests
import time
import json
from datetime import datetime, timedelta




def generate_random_string(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

class Wonton:

    def __init__(self):
        self.headers = {
            'authority': 'wonton.food',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://www.wonton.restaurant',
            'referer': 'https://www.wonton.restaurant/',
            'sec-ch-ua': 'Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129", "Microsoft Edge WebView2";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'x-tag':"w?1&w5^973]03ex3;g>04r2>fg<y9m3p&^55fv/jz/~tfh<j5c>fpj668/n"
        }

    def print_(self, word):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"[{now}] | {word}")

    def make_request(self, method, url, headers, json=None, data=None):
        retry_count = 0
        while True:
            time.sleep(2)
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, json=json)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json, data=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=json, data=data)
            else:
                raise ValueError("Invalid method.")
            
            if response.status_code >= 500:
                if retry_count >= 4:
                    self.print_(f"Status Code: {response.status_code} | {response.text}")
                    return None
                retry_count += 1
            elif response.status_code >= 400:
                self.print_(f"Status Code: {response.status_code} | {response.text}")
                return None
            elif response.status_code >= 200:
                return response


    def checkin(self, token):
        url = 'https://wonton.food/api/v1/checkin'
        headers = {**self.headers, 
        'Authorization': f'bearer {token}'}

        try:
            response = self.make_request('get',url, headers)
            if response is not None:
                data_checkin = response.json()
                if data_checkin is not None:
                    self.print_('Checkin Done')
                    self.print_(f"Last check-in date: {data_checkin.get('lastCheckinDay')}")
                    if data_checkin.get('newCheckin',False):
                        reward = next((config for config in data_checkin['configs'] if config['day'] == data_checkin['lastCheckinDay']), None)
                        if reward:
                            self.print_(f"Daily reward {data_checkin['lastCheckinDay']}:")
                            self.print_(f"- {reward['tokenReward']} WTON")
                            self.print_(f"- {reward['ticketReward']} ticket")
                    else:
                        self.print_('You checked in today.')
                return data_checkin
            
        except Exception as error:
            self.print_(f'Error Check-in: {error}')
            return None

    def check_farm_status(self, token):
        url = 'https://wonton.food/api/v1/user/farming-status'
        headers = {**self.headers, 'Authorization': f'bearer {token}'}

        try:
            res = self.make_request('get',url, headers)
            if res.status_code == 200:
                data = res.json()
                
                if not data:
                    return 'start'
                finishAt = data.get('finishAt')
                dt_object = datetime.fromisoformat(finishAt.replace("Z", "+00:00"))
                unix_time = int(dt_object.timestamp())
                remaining = unix_time - time.time()
                if remaining <= 0:
                    return data
                else:
                    self.print_(f'Remaining Farming Time : {round(remaining)} Seconds')
                    return 'wait'
                    
            else:
                self.print_(f'Error check farm: {res.status_code}')
                return None
        except Exception as error:
            self.print_(f'Error check farm: {error}')
            return None

    def claim_farming(self, token):
        url = 'https://wonton.food/api/v1/user/farming-claim'
        headers = {**self.headers, 'Authorization': f'bearer {token}'}

        try:
            res = self.make_request('post',url, headers, data={})
            if res is not None:
                data = res.json()
                self.print_('Farming Claimed...')
                return data
            
        except Exception as error:
            self.print_(f'Error Claim farming: {error}')
            return None

    def start_farming(self, token):
        url = 'https://wonton.food/api/v1/user/start-farming'
        headers = {**self.headers, 'Authorization': f'bearer {token}'}

        try:
            res = self.make_request('post',url, headers, data={})
            if res is not None:
                data = res.json()
                self.print_('Farming Start...')
                return data

        except Exception as error:
            self.print_(f'Error Farming: {error}')
            return None

    def start_game(self, token):
        url = 'https://wonton.food/api/v1/user/start-game'
        headers = {**self.headers, 'Authorization': f'bearer {token}'}

        try:
            res = self.make_request('post',url, headers, data={})
            if res is not None:
                data = res.json()
                self.print_('Start the game successfully')
                return data
        except Exception as error:
            self.print_(f'Error Start game: {error}')
            return None

    def finish_game(self, token, points, hasBonus):
        url = 'https://wonton.food/api/v1/user/finish-game'
        headers = {**self.headers, 'Authorization': f'bearer {token}'}
        data = {'points': points, 'hasBonus': hasBonus}

        try:
            res = self.make_request('post',url, headers, json=data)
            if res is not None:
                response = res.json()
                return response

        except Exception as error:
            self.print_(f'Error Finish Game: {error}')
            return None
        
    def get_task(self, token):
        url = 'https://wonton.food/api/v1/task/list'
        headers = {**self.headers, 'Authorization': f'bearer {token}'}
        try:
            res = self.make_request('get',url, headers)
            if res is not None:
                data = res.json()
                tasks = data['tasks']
                taskProgress = data['taskProgress']

                for task in tasks:
                    name = task.get('name')
                    if name in ['Join FunMe Channel', 'Join MasterChef Channel']:
                        self.print_(f"Task {name} Skip!!")
                        continue

                    rewardAmount = task.get('rewardAmount')
                    alls = f"Task : {name} | Reward : {rewardAmount}"
                    if task['status'] == 0:
                        payload = {'taskId': task['id']}
                        self.print_(f"{alls} Started")
                        time.sleep(1)
                        self.verify_task(token, payload, alls)
                    else:
                        self.print_(f"{alls} Done")

                if taskProgress >= 3:
                    self.get_task_progress(token)
            else:
                self.print_(f'Error Get Task: {res}')
        except Exception as error:
            self.print_(f'Error Get Task: {error}')

    def verify_task(self, token, payload, alls):
        url = 'https://wonton.food/api/v1/task/verify'
        headers = {**self.headers, 'Authorization': f'bearer {token}'}
        response = self.make_request('post',url, headers, json=payload)
        if response is not None:
            if response.status_code == 200:
                self.print_(f"Verification {alls}")
                time.sleep(1)
                self.claim_task(token, payload, alls)
            else:
                self.print_(f"Failed Verification {alls}")

    def claim_task(self, token, payload, alls):
        url = 'https://wonton.food/api/v1/task/claim'
        headers = {**self.headers, 'Authorization': f'bearer {token}'}
        response = self.make_request('post',url, headers, json=payload)
        if response is not None:
            if response.status_code == 200:
                self.print_(f"Claim {alls}")
            else:
                self.print_(f"Failed Claim {alls}")

    def get_task_progress(self, token):
        url = 'https://wonton.food/api/v1/task/claim-progress'
        headers = {**self.headers, 'Authorization': f'bearer {token}'}

        try:
            res = self.make_request('get',url, headers)
            if res.status_code == 200:
                data = res.json()
                items = data['items']

                self.print_('Claim WONTON successful, received')
                for item in items:
                    self.print_(f"Name: {item.get('name')} | Farming Power : {item.get('farmingPower')} | Token Value : {item.get('tokenValue')} WTON | {item.get('value')} TON")
            else:
                self.print_(f'Error Get: {res.status_code}')
        except Exception as error:
            self.print_(f'Error Get: {error}')

    def login(self, data):
        url = 'https://wonton.food/api/v1/user/auth'
        payload = {'initData': data, 'inviteCode': '', 'newUserPromoteCode': ''}

        try:
            response = self.make_request('post', url, self.headers, json=payload)
            if response is not None:
                data = response.json()
                return data

        except Exception as error:
            self.print_(f'Error Login: {error}')
            return None

    def get_user(self, token):
        url = 'https://wonton.food/api/v1/user'
        headers = {**self.headers, 'Authorization': f'bearer {token}'}

        try:
            response = self.make_request('get',url, headers)
            if response is not None:
                return response.json()

        except Exception as error:
            self.print_(f'Get user error : {error}')
            return None

    def clear_gift_task(self, token, types):
        url = f'https://wonton.food/api/v1/user/claim-task-gift?type={types}'
        headers = {**self.headers, 'Authorization': f'bearer {token}'}

        try:
            response = self.make_request('get',url, headers)
            if response is not None:
                jsons = response.json()
                self.print_(f"Claim gift Task {types} Done")
                items = jsons.get('items')
                for item in items:
                    self.print_(f"Name: {item.get('name')} | Farming Power : {item.get('farmingPower')} | Token Value : {item.get('tokenValue')} WTON | {item.get('value')} TON")
                return jsons

        except Exception as error:
            self.print_(f'Get user error : {error}')
            return None
    
    def get_list_wonton(self, token, selector_fusion):
        url = 'https://wonton.food/api/v1/shop/list'
        headers = {**self.headers, 'Authorization': f'bearer {token}'}
        try:
            response = self.make_request('get',url, headers)
            if response is not None:
                jsons = response.json()
                shopItems = jsons.get('shopItems',[])
                in_used = 0
                list_wonton = []
                data_item = {}
                ton = 0.0
                wton = 0
                for item in shopItems:
                    inventory = item.get('inventory')
                    inUse = item.get('inUse')
                    if inUse:
                        in_used = int(item.get('farmingPower'))
                        data_item = item
                    if inventory > 0 :
                        farmingPower = int(item.get('farmingPower',0))
                        value = float(item.get('value',0))
                        wton += farmingPower*inventory
                        ton += value*inventory
                        list_wonton.append(item)
                
                sorted_data = sorted(list_wonton, key=lambda x: int(x['farmingPower']), reverse=True)
                for data in sorted_data:
                    power = int(data.get('farmingPower'))
                    if power > in_used:
                        self.set_wonton(token, data)
                        data_item = data
                        break
                if selector_fusion == 'y':
                    self.get_list_fusion(token=token, list=shopItems)
                return {'ton': ton, 'wton':wton, 'data':data_item}

        except Exception as error:
            self.print_(f'Get user error : {error}')
            return None
    
    def set_wonton(self, token, item):
        url = 'https://wonton.food/api/v1/shop/use-item'
        id = item.get('id')
        payload = {'itemId': id}
        headers = {**self.headers, 
                   'Authorization': f'bearer {token}'
                   }
        try:
            response = self.make_request('post', url, headers, json=payload)
            if response is not None:
                if response.status_code == 200:
                    name = item.get('name','')
                    farmingPower = item.get('farmingPower','0')
                    self.print_(f"Set Farming Done | Name : {name}, Farming Power : {farmingPower}")

        except Exception as error:
            self.print_(f'Get user error : {error}')
            return None
    
    def get_list_fusion(self, token, list):
        url = 'https://wonton.food/api/v1/shop/fusion-items/list'
        headers = {**self.headers, 'Authorization': f'bearer {token}'}

        try:
            response = self.make_request('get',url, headers)
            if response is not None:
                jsons = response.json()
                items = jsons.get('items',[])
                fusion = True
                for index, item in enumerate(items):
                    requireItems = item.get('requireItems',[])
                    requireItemsAmount = item.get('requireItemsAmount',[])
                    for ids in requireItems:
                        data = next((item for item in list if item["internalId"] == ids), None)
                        inventory = data.get('inventory',0)
                        if inventory < requireItemsAmount[index]:
                            fusion = False
                            break

                    if fusion:
                        id = item.get('id')
                        payload = {"fusionId":id}
                        self.fusion_wonton(token=token, payload=payload)
                        break

        except Exception as error:
            self.print_(f'Get user error : {error}')
            return None
    
    def fusion_wonton(self, token, payload):
        url = 'https://wonton.food/api/v1/shop/fuse-item'
        headers = {**self.headers, 
                   'Authorization': f'bearer {token}'
                   }
        try:
            response = self.make_request('post', url, headers, json=payload)
            if response is not None:
                if response.status_code == 200:
                    
                    self.print_(f"Fusion wonton done")

        except Exception as error:
            self.print_(f'Get user error : {error}')
            return None




