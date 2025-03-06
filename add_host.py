# version - 0.1a
# Add host to zabbix Server via API
# Anatolii Dienhin
# anatoliydengin@gmail.com

import requests
import json
import socket

# -- Dict config
config = {}

# -- Підключаємо дані доступу до системи моніторингу
with open("access.txt", "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        if line.startswith("#") or not line:  # Ігноруємо коментарі та порожні рядки
            continue
        key, value = line.split("=", 1)  # Ділимо лише по першому "="
        config[key.strip()] = value.strip().strip('"')  # Видаляємо пробіли та лапки

# -- Підключаємо специфікацію вузла до системи моніторингу
with open("for_zabbix.txt", "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line.startswith("#") or not line:  # Ігноруємо коментарі та порожні рядки
                continue
            key, value = line.split("=", 1)  # Ділимо лише по першому "="
            config[key.strip()] = value.strip().strip('"')  # Видаляємо пробіли та лапки

# === Налаштування підключення до Zabbix ===
ZABBIX_URL = config["ZABBIX_URL"]
ZABBIX_TOKEN = config["ZABBIX_AUTH_TOKEN"]

# === Отримання зміниних про вузол для Zabbix ===
ip = requests.get('https://api.ipify.org').content.decode('utf8')

# === Дані для нового вузла ===
visibl = config["visible_name"]
if not visibl:
    visibl = input("Компанію не знайдено, введіть нову назву компаії: ")
host_name = socket.gethostname()  # Ім'я вузла
visible_name = f"{visibl}Windows.RDS.Server.uCloud.NOT-AO"  # Видиме ім'я (відображається у Zabbix UI)
group_id = config["group_id"]  # ID групи 
template_id = config["template_id"]  # ID шаблону (наприклад, "Template OS Linux")
ip_address = ip  # IP вузла

# === Запит для створення вузла ===
payload = {
    "jsonrpc": "2.0",
    "method": "host.create",
    "params": {
        "host": host_name,
        "name": visible_name,  
        "interfaces": [
            {
                "type": 1,  # 1 = Zabbix Agent
                "main": 1,
                "useip": 1,
                "ip": ip_address,
                "dns": "",
                "port": "10050"
            }
        ],
        "groups": [{"groupid": group_id}],
        "templates": [{"templateid": template_id}]
    },
    "auth": ZABBIX_TOKEN,  # 🛠 Використовуємо API-токен
    "id": 1
}

response = requests.post(ZABBIX_URL, json=payload, headers={"Content-Type": "application/json"})
result = response.json()

if "result" in result:
    print(f"✅ Вузол '{host_name}' успішно створений! (ID: {result['result']['hostids'][0]})")
else:
    print(f"❌ Помилка: {result}")
