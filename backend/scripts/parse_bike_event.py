import os
import sys
import sqlite3
import asyncio
import json
import re
import hashlib
from urllib.parse import urlparse
from playwright.async_api import async_playwright

DB_PATH = "bikescore.db"
DEFAULT_EVENT_URL = "https://results.zone/6tomilinskij-velomarafon-2025"


def init_db():
    """Создаёт нормализованную структуру из 3 таблиц в SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS riders (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            rating_road REAL DEFAULT 1000.0,
            rating_gravel REAL DEFAULT 1000.0,
            rating_mtb REAL DEFAULT 1000.0,
            races_road INTEGER DEFAULT 0,
            races_gravel INTEGER DEFAULT 0,
            races_mtb INTEGER DEFAULT 0,
            last_trend REAL DEFAULT 0.0,
            is_kids BOOLEAN DEFAULT 0,
            gender TEXT DEFAULT 'M',
            city TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Add index if it doesn't exist
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_riders_id ON riders (id)")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS races (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            category TEXT,
            k_factor REAL DEFAULT 1.0,
            external_id INTEGER UNIQUE,
            event_name TEXT,
            title TEXT,
            discipline TEXT,
            gender_group TEXT,
            age_group TEXT,
            is_rating_eligible BOOLEAN DEFAULT 1,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            race_id INTEGER NOT NULL,
            rider_id TEXT NOT NULL,
            time_sec REAL NOT NULL,
            status TEXT DEFAULT 'FIN',
            place INTEGER,
            delta REAL,
            bib TEXT,
            time_str TEXT,
            FOREIGN KEY (race_id) REFERENCES races (id) ON DELETE CASCADE,
            FOREIGN KEY (rider_id) REFERENCES riders (id) ON DELETE CASCADE,
            UNIQUE(race_id, rider_id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_results_race_id ON results (race_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_results_rider_id ON results (rider_id)")

    conn.commit()
    conn.close()


def is_url_already_parsed(target_url: str) -> bool:
    """Проверяет, скачивалось ли мероприятие ранее."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    clean_url = target_url.rstrip("/")
    cursor.execute("SELECT COUNT(*) FROM races WHERE source_url LIKE ?", (f"{clean_url}%",))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def is_bike_race(race_name: str) -> bool:
    """Исключает явно беговые заезды (TRAIL/RUN)."""
    name_lower = race_name.lower()
    if re.search(r'\b(trail|run|трейл|бег|скакан|ходьба)\b', name_lower):
        return False
    return True


def detect_discipline(title: str) -> str:
    t = title.lower()
    if "гревел" in t or "грэвел" in t or "gravel" in t or "велокросс" in t:
        return "гревел"
    elif "шоссе" in t or "road" in t:
        return "шоссе"
    return "мтб"


def detect_age_group(title: str) -> tuple[str, int]:
    if re.search(r'дети|детские|до\s+\d+\s+лет|беговел|child', title, re.IGNORECASE):
        return "дети", 0
    return "взрослые", 1


def detect_gender_group(title: str) -> str:
    t = title.lower()
    if "женщины" in t or "девушки" in t or " ж " in t:
        return "Ж"
    elif "мужчины" in t or " м " in t:
        return "М"
    return "Все"


def parse_time_to_seconds(time_str: str) -> int:
    if not time_str:
        return 0
    clean_str = str(time_str).strip()
    parts = clean_str.split(':')
    try:
        parts = [float(p) for p in parts]
        if len(parts) == 3:
            return int(parts[0] * 3600 + parts[1] * 60 + parts[2])
        elif len(parts) == 2:
            return int(parts[0] * 60 + parts[1])
        elif len(parts) == 1:
            return int(parts[0])
    except ValueError:
        return 0
    return 0


def parse_item_to_dict(item):
    """Преобразует JSON-элемент финишера в универсальный словарь."""
    if not isinstance(item, dict):
        return None

    name = item.get("name") or item.get("full_name")
    if not name and "athlete" in item and isinstance(item["athlete"], dict):
        name = item["athlete"].get("full_name") or item["athlete"].get("name")

    if not name:
        return None

    place = item.get("rank_abs") or item.get("place") or item.get("pos")
    time_str = item.get("result") or item.get("status_time") or item.get("result_time", "")
    
    time_sec = item.get("result_time")
    if not time_sec or not isinstance(time_sec, (int, float)):
        time_sec = parse_time_to_seconds(str(time_str))

    return {
        "place": int(place) if place and str(place).isdigit() else None,
        "name": str(name).strip(),
        "bib": str(item.get("bib", "")),
        "gender": item.get("gender"),
        "city": item.get("city"),
        "time_str": str(time_str),
        "time_sec": int(time_sec)
    }


def get_or_create_rider(cursor, name: str, gender: str = None, city: str = None) -> str:
    clean_name = name.strip()
    # Try finding an existing rider by name (or we could rely strictly on the hash)
    # The requirement seems to point to hash-based id generation for unique consistency.
    rider_id = "r_" + hashlib.md5(clean_name.encode('utf-8')).hexdigest()[:8]

    cursor.execute("SELECT id FROM riders WHERE id = ?", (rider_id,))
    row = cursor.fetchone()
    if row:
        # If city wasn't filled but is available now, we could update it
        if city:
            cursor.execute("UPDATE riders SET city = ? WHERE id = ? AND (city IS NULL OR city = '')", (city, rider_id))
        return row[0]

    cursor.execute("INSERT INTO riders (id, name, gender, city) VALUES (?, ?, ?, ?)", (rider_id, clean_name, gender, city))
    return rider_id


def save_event_to_db(race_id_ext, event_name, race_title, source_url, participants):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    full_title = f"{event_name} — {race_title}"
    discipline = detect_discipline(race_title)
    age_group, is_rating_eligible = detect_age_group(race_title)
    gender_group = detect_gender_group(race_title)

    cursor.execute("""
        INSERT INTO races (external_id, event_name, title, discipline, gender_group, age_group, is_rating_eligible, source_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(external_id) DO UPDATE SET
            event_name=excluded.event_name,
            title=excluded.title,
            discipline=excluded.discipline,
            gender_group=excluded.gender_group,
            age_group=excluded.age_group,
            is_rating_eligible=excluded.is_rating_eligible,
            source_url=excluded.source_url
    """, (race_id_ext, event_name, full_title, discipline, gender_group, age_group, is_rating_eligible, source_url))

    cursor.execute("SELECT id FROM races WHERE external_id = ?", (race_id_ext,))
    db_race_id = cursor.fetchone()[0]

    cursor.execute("DELETE FROM results WHERE race_id = ?", (db_race_id,))

    added_count = 0
    for p in participants:
        rider_id = get_or_create_rider(cursor, name=p["name"], gender=p.get("gender"), city=p.get("city"))

        cursor.execute("""
            INSERT OR REPLACE INTO results (race_id, rider_id, place, bib, time_str, time_sec)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (db_race_id, rider_id, p["place"], p["bib"], p["time_str"], p["time_sec"]))
        added_count += 1

    conn.commit()
    conn.close()
    return full_title, age_group, added_count


async def fetch_all_participants_playwright(page, race_url):
    """
    Открывает страницу и совершает клики по элементам пагинации Vue.js
    или делает гибридный вызов AJAX-запросов через Playwright context.
    """
    await page.goto(race_url, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(2000)

    participants = []

    # 1. Попытка забрать через Playwright APIRequestContext (напрямую у драйвера браузера)
    page_num = 1
    clean_url = race_url.rstrip('/')

    while True:
        try:
            # Делаем AJAX запрос с заголовоком XMLHttpRequest напрямую через сессию браузера
            response = await page.request.get(
                f"{clean_url}?page={page_num}&per_page=50",
                headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}
            )
            
            if response.status != 200:
                break
                
            text = await response.text()
            if not text.startswith(("{", "[")):
                break

            data = json.loads(text)
            rows = data.get("heats", []) or data.get("results", []) if isinstance(data, dict) else data

            if not rows:
                break

            added_this_page = 0
            for item in rows:
                p = parse_item_to_dict(item)
                if p and not any(existing['name'] == p['name'] for existing in participants):
                    participants.append(p)
                    added_this_page += 1

            print(f"      🔹 Стр. {page_num}: выкачано {added_this_page} участников через AJAX")

            if len(rows) < 50:
                break

            page_num += 1
        except Exception:
            break

    # 2. Если AJAX не отдался, переходим к симуляции кликов по визуальной пагинации
    if len(participants) == 0:
        current_page = 1
        while True:
            await page.wait_for_timeout(1000)
            rows = await page.query_selector_all("table tbody tr, .heats_table tbody tr")
            
            new_on_page = 0
            for row in rows:
                try:
                    cells = [(await c.inner_text()).strip() for c in await row.query_selector_all("td")]
                    if len(cells) < 2 or any(h in cells[0].lower() for h in ["место", "place"]):
                        continue

                    place_match = re.search(r'^\d+$', cells[0])
                    place = int(cells[0]) if place_match else None
                    name = next((c for c in cells[1:] if re.search(r'[А-Яа-яA-Za-z]{2,}\s+[А-Яа-яA-Za-z]{2,}', c)), "")
                    time_str = next((c for c in cells[1:] if re.search(r'\d+:\d+', c)), "")

                    if name and not any(p['name'] == name for p in participants):
                        participants.append({
                            "place": place,
                            "name": name,
                            "bib": "",
                            "gender": None,
                            "city": "",
                            "time_str": time_str,
                            "time_sec": parse_time_to_seconds(time_str)
                        })
                        new_on_page += 1
                except Exception:
                    continue

            # Попытка кликнуть следующий элемент пагинации
            pagination_links = await page.query_selector_all(".pagination li:not(.disabled) a, .pagination button:not(:disabled)")
            clicked = False
            
            for link in pagination_links:
                txt = (await link.inner_text()).strip()
                if txt in ["»", "Next", ">", str(current_page + 1)]:
                    await link.click()
                    await page.wait_for_timeout(2000)
                    current_page += 1
                    clicked = True
                    break

            if not clicked or new_on_page == 0:
                break

    return participants


async def run_pipeline_async(target_url: str, force_update: bool = False):
    init_db()

    if not force_update and is_url_already_parsed(target_url):
        print(f"\n⚠️ Мероприятие по ссылке '{target_url}' уже есть в базе данных!")
        user_choice = input("Хотите обновить существующие протоколы заново? (y/N): ").strip().lower()
        if user_choice not in ['y', 'yes', 'д', 'да']:
            print("🛑 Импорт отменён.")
            return

    parsed_uri = urlparse(target_url)
    base_url = f"{parsed_uri.scheme}://{parsed_uri.netloc}"

    print(f"\n🗄️ База данных SQLite готова: '{DB_PATH}'")
    print(f"🌐 Загрузка браузером: {target_url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2500)

        html_main = await page.content()
        match = re.search(r'(?:window\.)?general\.event\s*=\s*(\{.*?\});', html_main, re.DOTALL)
        if not match:
            print("❌ Метаданные мероприятия (general.event) не найдены.")
            await browser.close()
            return

        event_data = json.loads(match.group(1))
        event_name = event_data.get("name", "Событие")
        races = event_data.get("races", [])

        bike_races = [r for r in races if is_bike_race(r.get("name", ""))]

        print(f"📌 Мероприятие: '{event_name}'")
        print(f"🔍 Найдено заездов: {len(bike_races)}")

        for idx, race in enumerate(bike_races):
            race_title = race.get("name")
            race_id_ext = race.get("id")
            rel_url = race.get("self")
            
            clean_rel = rel_url.rstrip("/")
            if not clean_rel.endswith("/results"):
                clean_rel += "/results"
            
            race_url = f"{base_url}{clean_rel}"

            print(f"\n🚴 [{idx + 1}/{len(bike_races)}] Выкачивание ВСЕХ участников: '{race_title}'")
            print(f"   🔗 URL: {race_url}")

            # Забираем всех финишеров со всех страниц
            participants = await fetch_all_participants_playwright(page, race_url)

            full_title, age_group, count = save_event_to_db(
                race_id_ext, 
                event_name, 
                race_title, 
                target_url,
                participants
            )
            print(f"   ✓ Полное название: {full_title}")
            print(f"   ✓ Категория: [{age_group.upper()}] | ВСЕГО участников сохранено в БД: {count}")

        await browser.close()

    print("\n🎉 Успех! Все финишёры со всех страниц сохранены в SQLite.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1].strip()
    else:
        user_input = input(f"Введите ссылку на мероприятие (по умолчанию: {DEFAULT_EVENT_URL}): ").strip()
        url = user_input if user_input else DEFAULT_EVENT_URL

    asyncio.run(run_pipeline_async(url))