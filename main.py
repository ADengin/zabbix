import requests
import time

# -- Підключаємо дані доступу до системи моніторингу
with open("access.txt", "r", encoding="utf-8") as file:
    for line in file:
        key, value = line.strip().split("=", 1)  # Ділимо тільки по першому "="
        config[key] = value.strip('"')  # Видаляємо лапки


# === Налаштування підключення до Zabbix ===
ZABBIX_URL = config["ZABBIX_URL"]
ZABBIX_AUTH_TOKEN = config["ZABBIX_AUTH_TOKEN"]

def zabbix_api_request(method, params):
    headers = {'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "auth": ZABBIX_AUTH_TOKEN,
        "id": 1
    }
    response = requests.post(ZABBIX_URL, json=payload, headers=headers)
    return response.json()

# 1. Отримуємо список вузлів з їх статусом доступності
hosts_response = zabbix_api_request('host.get', {
    "output": ["hostid", "name", "available"],
    "filter": {"status": 1}
})

if 'result' not in hosts_response:
    print("Error: No result in response", hosts_response)
    exit(1)

hosts = hosts_response['result']
one_year_ago = int(time.time()) - (365 * 24 * 3600)
old_hosts = []

for host in hosts:
    host_id = host['hostid']
    host_name = host['name']
    print(host)
#    available = int(host['available'])
#
#    # Якщо вузол вже більше року "недоступний"
#    if available == 2:
#        print(f"Host {host_name} (ID: {host_id}) is unavailable. Checking last data received...")
#
#        # 2. Перевіряємо останні отримані дані (history.get)
#        history_response = zabbix_api_request('history.get', {
#            "hostids": host_id,
#            "output": ["clock"],
#            "sortfield": "clock",
#            "sortorder": "DESC",
#            "limit": 1
#        })
#
#        if 'result' in history_response and history_response['result']:
#            last_data_time = int(history_response['result'][0]['clock'])
#            if last_data_time < one_year_ago:
#                old_hosts.append(host_id)
#                print(f"Host {host_name} hasn't received data since {time.strftime('%Y-%m-%d', time.gmtime(last_data_time))}. Marked for deletion.")
#        else:
#            # Взагалі немає даних, можна видаляти
#            old_hosts.append(host_id)
#            print(f"Host {host_name} has never received data. Marked for deletion.")