import re
import time
import requests
from collections import Counter
from hyperloglog import HyperLogLog
import pandas as pd

def download_log_file(url):
    """Завантажує лог-файл за URL і повертає вміст як список рядків."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.splitlines()
    else:
        raise Exception(f"Не вдалося завантажити файл. Код помилки: {response.status_code}")

def parse_ip_addresses(log_lines):
    """Витягує IP-адреси з рядків лог-файлу, ігноруючи некоректні рядки."""
    ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    ip_addresses = []
    for line in log_lines:
        match = ip_pattern.search(line)
        if match:
            ip_addresses.append(match.group())
    return ip_addresses

def exact_count_unique_ips(ip_addresses):
    """Точний підрахунок унікальних IP-адрес за допомогою set."""
    return len(set(ip_addresses))

def approximate_count_unique_ips(ip_addresses):
    """Наближений підрахунок унікальних IP-адрес за допомогою HyperLogLog."""
    hll = HyperLogLog(0.01)  # Задаємо похибку 1%
    for ip in ip_addresses:
        hll.add(ip)
    return len(hll)

def compare_methods(log_file_url):
    """Порівнює точний і наближений підрахунок унікальних IP-адрес."""
    print("Завантаження лог-файлу...")
    log_lines = download_log_file(log_file_url)

    print("Парсинг IP-адрес...")
    ip_addresses = parse_ip_addresses(log_lines)

    print("Виконання точного підрахунку...")
    start_time = time.time()
    exact_count = exact_count_unique_ips(ip_addresses)
    exact_time = time.time() - start_time

    print("Виконання наближеного підрахунку за допомогою HyperLogLog...")
    start_time = time.time()
    approx_count = approximate_count_unique_ips(ip_addresses)
    approx_time = time.time() - start_time

    # Формування таблиці результатів
    results = pd.DataFrame({
        "Метод": ["Точний підрахунок", "HyperLogLog"],
        "Унікальні елементи": [exact_count, approx_count],
        "Час виконання (сек.)": [exact_time, approx_time]
    })

    print("Результати порівняння:")
    print(results)

if __name__ == "__main__":
    LOG_FILE_URL = "https://drive.google.com/uc?id=13NUCSG7l_z2B7gYuQubYIpIjJTnwOAOb"
    compare_methods(LOG_FILE_URL)
