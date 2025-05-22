import requests
from users.models import User

def fetch_random_users(count=10):
    created = 0
    attempts = 0
    max_attempts = 10

    while created < count and attempts < max_attempts:
        attempts += 1
        to_fetch = min(500, count - created)
        response = requests.get(f"https://randomuser.me/api/?results={to_fetch}")
        response.raise_for_status()
        users = response.json()["results"]

        for user_data in users:
            if created >= count:
                break

            try:
                User.objects.create(
                    gender=user_data["gender"],
                    first_name=user_data["name"]["first"],
                    last_name=user_data["name"]["last"],
                    phone=user_data["phone"],
                    email=user_data["email"],
                    location=user_data["location"]["city"],
                    picture=user_data["picture"]["medium"],
                )
                created += 1
            except Exception:
                continue

    print(f"Загружено {created} новых пользователей (запрошено {count}).")
