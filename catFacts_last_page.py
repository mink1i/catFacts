# catfacts_last_page.py
"""
Берём первую страницу с catfact.ninja/facts, считаем последнюю страницу,
запрашиваем её и печатаем самый короткий факт.
"""

import sys
from typing import Any, Dict, List, Optional
import requests

API_URL = "https://catfact.ninja/facts"

def fetch_json(url: str, params: Dict[str, Any] = None, timeout: int = 10) -> Dict[str, Any]:
    """Делаем GET-запрос и возвращаем распарсенный JSON. При ошибке — завершаем программу."""
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()      # бросит исключение при 4xx/5xx
        return r.json()
    except requests.RequestException as e:
        print("Ошибка сети или HTTP:", e)
        sys.exit(1)
    except ValueError as e:
        print("Ответ не в формате JSON:", e)
        sys.exit(1)

def safe_int(x: Any, default: int = 0) -> int:
    """Пытаемся привести к int, иначе возвращаем default."""
    try:
        return int(x)
    except Exception:
        return default

def get_shortest_fact(facts: List[Dict[str, Any]]) -> Optional[str]:
    """Из списка объектов (каждый имеет ключ 'fact') возвращаем самый короткий непустой факт."""
    texts = []
    for item in facts:
        t = (item.get("fact") or "").strip()
        if t:
            texts.append(t)
    if not texts:
        return None
    return min(texts, key=len)

def main():
    # 1) Первая страница
    first = fetch_json(API_URL)
    total = safe_int(first.get("total"))
    per_page = safe_int(first.get("per_page"), 1)
    if total <= 0:
        print("Сервер вернул неверный total:", first.get("total"))
        sys.exit(1)
    if per_page <= 0:
        per_page = 1

    # 2) Вычисляем последнюю страницу (целочисленное округление вверх)
    last_page = (total + per_page - 1) // per_page
    print(f"Всего фактов: {total}. На странице: {per_page}. Последняя страница: {last_page}")

    # 3) Данные с последней страницы
    last = fetch_json(API_URL, params={"page": last_page})
    facts = last.get("data", []) if isinstance(last.get("data", []), list) else []

    # 4) Самый короткий факт
    shortest = get_shortest_fact(facts)
    if shortest is None:
        print("Не найден непустой факт на последней странице.")
    else:
        print("\nСамый короткий факт на последней странице:")
        print(shortest)
        print("Длина (символов):", len(shortest))

if __name__ == "__main__":
    main()
