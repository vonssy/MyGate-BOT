from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    WSMsgType
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, uuid, hashlib, hmac, time, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class MyGate:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://app.mygate.network",
            "Referer": "https://app.mygate.network/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}MyGate - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_auto_proxies(self):
        url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url) as response:
                    response.raise_for_status()
                    content = await response.text()
                    with open('proxy.txt', 'w') as f:
                        f.write(content)

                    self.proxies = content.splitlines()
                    if not self.proxies:
                        self.log(f"{Fore.RED + Style.BRIGHT}No proxies found in the downloaded list!{Style.RESET_ALL}")
                        return
                    
                    self.log(f"{Fore.GREEN + Style.BRIGHT}Proxies successfully downloaded.{Style.RESET_ALL}")
                    self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
                    self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
                    await asyncio.sleep(3)
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed to load proxies: {e}{Style.RESET_ALL}")
            return []
        
    async def load_manual_proxy(self):
        try:
            if not os.path.exists('manual_proxy.txt'):
                print(f"{Fore.RED + Style.BRIGHT}Proxy file 'manual_proxy.txt' not found!{Style.RESET_ALL}")
                return

            with open('manual_proxy.txt', "r") as f:
                proxies = f.read().splitlines()

            self.proxies = proxies
            self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed to load manual proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        
        return f"http://{proxies}" # Change with yours proxy schemes if your proxy not have schemes [http:// or socks5://]

    def get_next_proxy(self):
        if not self.proxies:
            self.log(f"{Fore.RED + Style.BRIGHT}No proxies available!{Style.RESET_ALL}")
            return None

        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.check_proxy_schemes(proxy)
    
    def generate_signature(self, id: str):
        secret_key = "|`8S%QN9v&/J^Za".encode('utf-8')
        timestamp = int(time.time() * 1000)
        data = json.dumps({"nodeId": id})
        message = f"{data}{timestamp}".encode('utf-8')
        signature = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
        
        return signature, timestamp
    
    def generate_node_id(self):
        id = str(uuid.uuid4())
        return id
    
    def generate_activation_date(self):
        activation_date = datetime.utcnow().isoformat() + "Z"
        return activation_date
    
    def hide_token(self, token: str):
        hide_token = token[:3] + '*' * 3 + token[-3:]
        return hide_token
    
    async def users_data(self, token: str, proxy=None, retries=5):
        url = "https://api.mygate.network/api/front/users/me"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
        
    async def users_confirm(self, token: str, proxy=None, retries=5):
        url = "https://api.mygate.network/api/front/referrals/referral/9OqMCE"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "0",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        if response.status == 400:
                            return None
                        
                        response.raise_for_status()
                        await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
        
    async def users_today_earning(self, token: str, proxy=None, retries=5):
        url = "https://api.mygate.network/api/front/user-transactions/TODAY/earn"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                
    async def users_season_earning(self, token: str, proxy=None, retries=5):
        url = "https://api.mygate.network/api/front/user-transactions/ALL/earn"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                    
    async def users_all_nodes_data(self, token: str, proxy=None, retries=5):
        url = "https://api.mygate.network/api/front/nodes"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                
    async def users_nodes_data(self, token: str, _id: str, proxy=None, retries=5):
        url = f"https://api.mygate.network/api/front/nodes/{_id}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                
    async def users_node_register(self, token: str, id: str, activation_date: str, proxy=None, retries=5):
        url = "https://api.mygate.network/api/front/nodes"
        data = json.dumps({"id":id, "status":"Good", "activationDate":activation_date})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                
    async def social_media_tasks(self, token: str, task_type: str, proxy=None, retries=5):
        url = f"https://api.mygate.network/api/front/achievements/{task_type}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "0",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None

    async def ambassador_tasks(self, token: str, proxy=None, retries=5):
        url = "https://api.mygate.network/api/front/achievements/ambassador"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']['items']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None

    async def submit_tasks(self, token: str, task_id: str, proxy=None, retries=5):
        url = f"https://api.mygate.network/api/front/achievements/ambassador/{task_id}/submit"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "0",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                
    async def process_loads_users_earning(self, token: str, name: str, proxy=None):
        while True:
            today_point = 0
            season_point = 0
            today_earning = await self.users_today_earning(token, proxy)
            if today_earning:
                today_point = today_earning['data']

            season_earning = await self.users_season_earning(token, proxy)
            if season_earning:
                season_point = season_earning['data']

            self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Earning {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}Today {today_point} PTS{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}Season {season_point} PTS{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
            )
            
            await asyncio.sleep(600)
                
    async def process_loads_nodes_data(self, token: str, name: str, proxy=None):
        nodes = await self.users_all_nodes_data(token, proxy)
        if not nodes:
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} GET Node Data Failed {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
            )
            return []

        list_nodes = nodes.get("items", [])
        node_ids = []

        if isinstance(list_nodes, list) and len(list_nodes) == 0:
            id = self.generate_node_id()
            activation_date = self.generate_activation_date()

            node = await self.users_node_register(token, id, activation_date, proxy)
            if not node:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Node ID {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{id}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}Register Failed{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                )
                return []

            self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Node ID {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{id}{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}Registered Successfully{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
            )
            return [{"node_id":id}]

        for node in list_nodes:
            node_ids.append({"node_id":node['id'], "_id":node['_id']})

        return node_ids

    async def process_loads_nodes_earning(self, token: str, name: str, node_ids: list, proxy=None):
        while True:
            for node in node_ids:
                if 'node_id' in node and '_id' in node:
                    id = node['node_id']
                    _id = node['_id']

                    nodes_data = await self.users_nodes_data(token, _id, proxy)
                    if nodes_data:
                        today_earn = nodes_data['todayEarn']
                        season_earn = nodes_data['seasonEarn']
                        uptime = nodes_data['uptime']
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Node ID {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{id}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Earning{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} Today {today_earn} PTS {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} Season {season_earn} PTS {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Uptime {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{uptime}{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                        )
                    else:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Node ID {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{id}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}GET Eearning Data Failed{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                        )
                else:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} No _id in Node Data {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                await asyncio.sleep(3)
            
            await asyncio.sleep(600)
                
    async def process_users_tasks_completion(self, token: str, name: str, proxy=None):
        while True:
            for task_type in ["follow-x", "follow-telegram"]:
                await self.social_media_tasks(token, task_type, proxy)

            tasks = await self.ambassador_tasks(token, proxy)
            if tasks:
                completed = False
                for task in tasks:
                    task_id = task['_id']
                    status = task['status']

                    if task and status == 'UNCOMPLETED':
                        submit = await self.submit_tasks(token, task_id, proxy)
                        if submit and submit['message'] == 'OK':
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Ambassador Task {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{task['name']}{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{task['description']}{Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Reward {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{task['experience']} EXP{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Ambassador Task {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{task['name']}{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{task['description']}{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Isn't Completed {Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                            )
                        await asyncio.sleep(1)

                    else:
                        completed = True

                if completed:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} All Available Ambassador Task Is Completed {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} GET Ambassador Tasks Data Failed {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                )
            await asyncio.sleep(86400)

    async def connect_websocket(self, token: str, name: str, id: str, use_proxy: bool, proxy=None, retries=5):
        signature, timestamp = self.generate_signature(id)
        wss_url = f"wss://api.mygate.network/socket.io/?nodeId={id}&signature={signature}&timestamp={timestamp}&version=2&EIO=4&transport=websocket"
        headers = {
            "Accept-encoding": "gzip, deflate, br, zstd",
            "Accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-control": "no-cache",
            "Connection": "Upgrade",
            "Host": "api.mygate.network",
            "Origin": "chrome-extension://hajiimgolngmlbglaoheacnejbnnmoco",
            "Pragma": "no-cache",
            "Sec-Websocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Sec-Websocket-Key": "+XFqg8JtrjOUgzPPhmZBTQ==",
            "Sec-Websocket-Version": "13",
            "Upgrade": "websocket",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }
        message = f'40{{"token":"Bearer {token}"}}'

        while True:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            session = ClientSession(connector=connector, timeout=ClientTimeout(total=60))

            try:
                for attempt in range(retries):
                    try:
                        async with session.ws_connect(wss_url, headers=headers) as wss:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Proxy {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT}Websocket Is Connected{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                            )
                            
                            await wss.send_str(message)
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Node ID {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{id}{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT}Sending Message:{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {message} {Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                            )

                            async for msg in wss:
                                if msg.type == WSMsgType.TEXT:
                                    if msg.data in ["2", "41"]:
                                        await wss.send_str("3")
                                        print(
                                            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                                            f"{Fore.BLUE + Style.BRIGHT}All Nodes Connection Estabilished{Style.RESET_ALL}",
                                            end="\r",
                                            flush=True
                                        )
                                    else:
                                        self.log(
                                            f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                            f"{Fore.CYAN + Style.BRIGHT} Node ID {Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT}{id}{Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                            f"{Fore.GREEN + Style.BRIGHT}Received Message:{Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT} {msg.data} {Style.RESET_ALL}"
                                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                                        )
                                elif msg.type in [WSMsgType.CLOSED, WSMsgType.ERROR]:
                                    self.log(
                                        f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.CYAN + Style.BRIGHT} Node ID {Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT}{id}{Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                        f"{Fore.YELLOW + Style.BRIGHT}Webscoket Connection Closed. Reconnecting...{Style.RESET_ALL}"
                                        f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                                    )
                                    await wss.close()
                                    break
                            
                    except Exception as e:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Node ID {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{id}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT}Webscoket GET Error:{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} {e} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                        if attempt < retries - 1:
                            await asyncio.sleep(5)
                            continue

                        text = "Retrying..."
                        if use_proxy:
                            text = "Retrying With Next Proxy..."

                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Node ID {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{id}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}Websocket Not Connected{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT}{text}{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                        )
                        if use_proxy:
                            proxy = self.get_next_proxy()

            except asyncio.CancelledError:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Node ID {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{id}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}Websocket Closed{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                )
                break
            finally:
                await session.close()

    async def question(self):
        while True:
            try:
                print("1. Run With Auto Proxy")
                print("2. Run With Manual Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Auto Proxy" if choose == 1 else 
                        "With Manual Proxy" if choose == 2 else 
                        "Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Selected.{Style.RESET_ALL}")
                    await asyncio.sleep(1)
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")
        
    async def process_accounts(self, token: str, use_proxy: bool):
        proxy = None
        if use_proxy:
            proxy = self.get_next_proxy()

        user = None
        while user is None:
            user = await self.users_data(token, proxy)
            if not user:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {self.hide_token(token)} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Proxy {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}GET User Data Failed{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                )
                await asyncio.sleep(1)

                if not use_proxy:
                    return

                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}Try With The Next Proxy,{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Wait... {Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )

                proxy = self.get_next_proxy()
                continue
            
            name = user['name']

            await self.users_confirm(token, proxy)

            asyncio.create_task(self.process_loads_users_earning(token, name, proxy)) # Call Every 10 Minutes

            asyncio.create_task(self.process_users_tasks_completion(token, name, proxy)) # Call Every 1 Day

            node_ids = await self.process_loads_nodes_data(token, name, proxy)
            if node_ids:
                asyncio.create_task(
                    self.process_loads_nodes_earning(token, name, node_ids, proxy)
                )  # Call Every 10 Minutes

                await asyncio.gather(
                    *(
                        self.connect_websocket(token, name, node['node_id'], use_proxy, self.get_next_proxy())
                        for node in node_ids
                    )
                )

    async def main(self):
        try:
            with open('tokens.txt', 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]

            use_proxy_choice = await self.question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            if use_proxy and use_proxy_choice == 1:
                await self.load_auto_proxies()
            elif use_proxy and use_proxy_choice == 2:
                await self.load_manual_proxy()
            
            while True:
                tasks = []
                for token in tokens:
                    token = token.strip()

                    if token:
                        tasks.append(self.process_accounts(token, use_proxy))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except (Exception, FileNotFoundError) as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            return

if __name__ == "__main__":
    try:
        bot = MyGate()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] MyGate - BOT{Style.RESET_ALL}                                       "                              
        )