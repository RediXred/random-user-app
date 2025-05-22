import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import User
from django.core.cache import cache

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write('Fetching users...')
        target = 1000
        users_created = 0
        batch_size = 100

        while users_created < target:
            response = requests.get(f'https://randomuser.me/api/?results={batch_size}')
            if response.status_code != 200:
                self.stderr.write('Failed to fetch users')
                break

            results = response.json().get('results', [])
            new_users = []

            for item in results:
                if users_created + len(new_users) >= target:
                    break

                user = User(
                    gender=item['gender'],
                    first_name=item['name']['first'],
                    last_name=item['name']['last'],
                    phone=item['phone'],
                    email=item['email'],
                    location=', '.join([
                        item['location']['city'],
                        item['location']['state'],
                        item['location']['country']
                    ]),
                    picture=item['picture']['thumbnail'],
                )

                new_users.append(user)

            with transaction.atomic():
                User.objects.bulk_create(new_users)

            users_created += len(new_users)

            self.stdout.write(f'Progress: {users_created}/{target} users added.')

        cache.clear()
        self.stdout.write(self.style.SUCCESS(f'{users_created} users saved.'))
