from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, time, base64, hmac, hashlib, json, os, uuid, pytz

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
        self.account_proxies = {}

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
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def decode_token(self, token: str):
        try:
            header, payload, signature = token.split(".")
            decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            email = parsed_payload.get("email")

            return email
        except Exception as e:
            return None
    
    def generate_wss_url(self, node_id):
        t = datetime.now()
        e = int(datetime(
            t.year, 
            t.month, 
            t.day, 
            t.hour, 
            t.minute, 
            t.second, 
            t.microsecond
        ).timestamp() * 1000)

        secret_key = b"|`8S%QN9v&/J^Za"
        message = json.dumps({"nodeId": node_id}, separators=(',', ':')) + str(e)

        hmac_obj = hmac.new(secret_key, message.encode(), hashlib.sha256)
        r = hmac_obj.hexdigest()

        return f"wss://api.mygate.network/socket.io/?nodeId={node_id}&signature={r}&timestamp={e}&version=2&EIO=4&transport=websocket"

    def generate_node_id(self):
        node_id = str(uuid.uuid4())
        return node_id
    
    def generate_activation_date(self):
        activation_date = datetime.utcnow().isoformat() + "Z"
        return activation_date
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
    
    def print_message(self, account, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    async def user_confirm(self, token: str, email: str, proxy=None, retries=5):
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
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(email, proxy, Fore.RED, f"GET User Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
        
    async def user_today_earning(self, token: str, email: str, proxy=None, retries=5):
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
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(email, proxy, Fore.RED, f"GET Today Earning Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                
    async def user_season_earning(self, token: str, email: str, proxy=None, retries=5):
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
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(email, proxy, Fore.RED, f"GET Season Earning Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                    
    async def all_node_data(self, token: str, email: str, proxy=None, retries=5):
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
                    await asyncio.sleep(5)
                    continue

                return self.print_message(email, proxy, Fore.RED, f"GET All Node Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                
    async def single_node_data(self, token: str, email: str, _id: str, proxy=None, retries=5):
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
                    await asyncio.sleep(5)
                    continue

                return self.print_message(email, proxy, Fore.RED, f"GET Node ID {_id} Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                
    async def register_new_node(self, token: str, email: str, id: str, activation_date: str, proxy=None, retries=5):
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
                        if result and result['data'] is not None:
                            return result['data']
                        return None
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(email, proxy, Fore.RED, f"Register New Node Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                
    async def social_media_tasks(self, token: str, email: str, task_type: str, proxy=None, retries=5):
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
                    await asyncio.sleep(5)
                    continue

                return self.print_message(email, proxy, Fore.RED, f"Complete Social Media Tasks Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")

    async def task_lists(self, token: str, email: str, type: str, proxy=None, retries=5):
        url = f"https://api.mygate.network/api/front/achievements/{type}"
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
                    await asyncio.sleep(5)
                    continue

                return self.print_message(email, proxy, Fore.RED, f"GET Available Tasks Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")

    async def submit_tasks(self, token: str, email: str, type: str, task_id: str, proxy=None, retries=5):
        url = f"https://api.mygate.network/api/front/achievements/{type}/{task_id}/submit"
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
                    await asyncio.sleep(5)
                    continue

                return self.print_message(email, proxy, Fore.RED, f"Complete Available Tasks Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
            
    async def process_user_earning(self, token: str, email: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            today_earning = await self.user_today_earning(token, email, proxy)
            season_earning = await self.user_season_earning(token, email, proxy)
            if today_earning and season_earning:
                today_point = today_earning['data']
                season_point = season_earning['data']

                self.print_message(email, proxy, Fore.WHITE, 
                    f"Earning Today {today_point} PTS"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}Earning Season {season_point} PTS{Style.RESET_ALL}"
                )
            
            await asyncio.sleep(1 * 60 * 60)
            
    async def process_complete_mission(self, token: str, email: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            await self.user_confirm(token, email, proxy)

            for task_type in ["follow-x", "follow-telegram"]:
                await self.social_media_tasks(token, email, task_type, proxy)

            for type in ["daily-check-in", "ambassador"]:
                tasks = await self.task_lists(token, email, type, proxy)
                if tasks:
                    completed = False
                    for task in tasks:
                        task_id = task['_id']
                        title = task['name']
                        description = task['description']
                        status = task['status']

                        reward = 0
                        reward_type = "N/A"
                        if type == "daily-check-in":
                            reward = task['point']
                            reward_type = "Points"
                        elif type == "ambassador":
                            reward = task['experience']
                            reward_type = "EXP"


                        if task and status == 'UNCOMPLETED':
                            submit = await self.submit_tasks(token, email, type, task_id, proxy)
                            if submit and submit.get('message') == "OK":
                                self.print_message(email, proxy, Fore.WHITE, 
                                    f"Task {title}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}{description}{Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}{reward} {reward_type}{Style.RESET_ALL}"
                                )
                            else:
                                self.print_message(email, proxy, Fore.WHITE, 
                                    f"Task {title} "
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {description} {Style.RESET_ALL}"
                                    f"{Fore.RED + Style.BRIGHT}Isn't Completed{Style.RESET_ALL}"
                                )
                            await asyncio.sleep(1)

                        else:
                            completed = True

                    if completed:
                        if type == "daily-check-in":
                            self.print_message(email, proxy, Fore.GREEN, "Already Check-In Today")
                        elif type == "ambassador":
                            self.print_message(email, proxy, Fore.GREEN, "All Available Tasks Is Completed")
                
            await asyncio.sleep(12 * 60 * 60)

    async def process_register_node(self, token: str, email: str, proxy=None):
        node_id = self.generate_node_id()
        activation_date = self.generate_activation_date()
        new_node = await self.register_new_node(token, email, node_id, activation_date, proxy)
        if new_node:
            self.print_message(email, proxy, Fore.GREEN, 
                "Register New Node Success "
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Node ID: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{node_id}{Style.RESET_ALL}"
            )

            return node_id

    async def process_loads_node_data(self, token: str, email: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None

        nodes = None
        while nodes is None:
            nodes = await self.all_node_data(token, email, proxy)
            if not nodes:
                proxy = self.rotate_proxy_for_account(email) if use_proxy else None
                continue

            list_nodes = nodes.get("items", [])
            node_ids = []

            if isinstance(list_nodes, list) and len(list_nodes) == 0:
                new_node_id = await self.process_register_node(token, email, proxy)
                if new_node_id:
                    return [{"node_id":new_node_id}]

            if use_proxy:
                for node in list_nodes:
                    node_id = node['id']
                    _id = node['_id']
                    node_ids.append({"node_id":node_id, "id":_id})

            else:
                node_id = list_nodes[0]['id']
                _id = list_nodes[0]['_id']
                node_ids.append({"node_id":node_id, "id":_id})
            
            return node_ids
    
    async def get_node_earning(self, token: str, email: str, node_id: str, _id: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            node = await self.single_node_data(token, email, _id, proxy)
            if node:
                today_earn = node['todayEarn']
                season_earn = node['seasonEarn']
                uptime = node['uptime']

                self.print_message(email, proxy, Fore.WHITE, 
                    f"Node ID {node_id}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Earning:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} Today {today_earn} PTS {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} Season {season_earn} PTS {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Uptime: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{uptime}{Style.RESET_ALL}"
                )

            await asyncio.sleep(1 * 60 * 60)
    
    async def connect_websocket(self, token: str, email: str, node_id: str, use_proxy: bool):
        wss_url = self.generate_wss_url(node_id)
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
            proxy = self.get_next_proxy_for_account(node_id) if use_proxy else None
            connector = ProxyConnector.from_url(proxy) if proxy else None
            session = ClientSession(connector=connector, timeout=ClientTimeout(total=120))
            try:
                async with session.ws_connect(wss_url, headers=headers) as wss:

                    self.print_message(email, proxy, Fore.WHITE, 
                        f"Node ID {node_id}"
                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT}Websocket Is Connected{Style.RESET_ALL}"
                    )

                    registered = False
                    ping_time = None
                    
                    while True:
                        try:
                            if ping_time is not None and int(time.time()) - ping_time > (10 * 60):
                                self.print_message(email, proxy, Fore.WHITE, 
                                    f"Node ID {node_id}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                    f"{Fore.YELLOW + Style.BRIGHT}Reconnecting...{Style.RESET_ALL}"
                                )

                                wss_url = self.generate_wss_url(node_id)
                                break

                            response = await wss.receive_str()
                            if response and not registered:
                                self.print_message(email, proxy, Fore.WHITE, 
                                    f"Node ID {node_id} "
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT} Received Message: {Style.RESET_ALL}"
                                    f"{Fore.BLUE + Style.BRIGHT}{response}{Style.RESET_ALL}"
                                )

                                await wss.send_str(message)
                                self.print_message(email, proxy, Fore.WHITE, 
                                    f"Node ID {node_id} "
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT} Sent Message: {Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT}{message}{Style.RESET_ALL}"
                                )
                                registered = True

                            elif response and registered:
                                if response in ["41", "2"]:
                                    await wss.send_str("3")
                                    print(
                                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                                        f"{Fore.BLUE + Style.BRIGHT}Node Connection Estabilished{Style.RESET_ALL}",
                                        end="\r",
                                        flush=True
                                    )
                                    
                                    if ping_time is None:
                                        ping_time = int(time.time())

                                else:
                                    self.print_message(email, proxy, Fore.WHITE, 
                                        f"Node ID {node_id} "
                                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.CYAN + Style.BRIGHT} Received Message: {Style.RESET_ALL}"
                                        f"{Fore.BLUE + Style.BRIGHT}{response}{Style.RESET_ALL}"
                                    )
                                
                        except Exception as e:
                            self.print_message(email, proxy, Fore.WHITE, 
                                f"Node ID {node_id} "
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT} Websocket Connection Closed: {Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                            )
                            await asyncio.sleep(5)

                            wss_url = self.generate_wss_url(node_id)
                            break

            except Exception as e:
                self.print_message(email, proxy, Fore.WHITE, 
                    f"Node ID {node_id} "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Websocket Not Connected: {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                proxy = self.rotate_proxy_for_account(node_id) if use_proxy else None
                await asyncio.sleep(5)

                wss_url = self.generate_wss_url(node_id)

            except asyncio.CancelledError:
                self.print_message(email, proxy, Fore.WHITE, 
                    f"Node ID {node_id}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Websocket Closed{Style.RESET_ALL}"
                )
                break
            finally:
                await session.close()

    async def process_send_ping(self, token: str, email: str, use_proxy: bool):
        nodes = await self.process_loads_node_data(token, email, use_proxy)
        if nodes:
            tasks = []
            for node in nodes:
                node_id = node['node_id']

                if "id" in node:
                    _id = node['id']
                    tasks.append(asyncio.create_task(self.get_node_earning(token, email, node_id, _id, use_proxy)))

                tasks.append(asyncio.create_task(self.connect_websocket(token, email, node_id, use_proxy)))

            await asyncio.gather(*tasks)
        
    async def process_accounts(self, token: str, email: str, use_proxy: bool):
        tasks = []
        tasks.append(asyncio.create_task(self.process_user_earning(token, email, use_proxy)))
        tasks.append(asyncio.create_task(self.process_complete_mission(token, email, use_proxy)))
        tasks.append(asyncio.create_task(self.process_send_ping(token, email, use_proxy)))
        await asyncio.gather(*tasks)

    async def main(self):
        try:
            with open('tokens.txt', 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]

            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for token in tokens:
                    if token:
                        email = self.decode_token(token)
                        if email:
                            tasks.append(asyncio.create_task(self.process_accounts(token, email, use_proxy)))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'tokens.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

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