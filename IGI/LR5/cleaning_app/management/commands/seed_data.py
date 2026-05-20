from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import random

from cleaning_app.models import (
    Article, Client, CompanyInfo, Employee, FAQ,
    Order, OrderService, PromoCode, Review,
    Service, ServiceType, Specialization, Vacancy,
)


class Command(BaseCommand):
    help = 'Seed database with demo data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        CompanyInfo.objects.get_or_create(
            title='КлинингПро',
            defaults={
                'description': 'Профессиональная клининговая компания. Работаем с 2015 года. '
                               'Более 1000 довольных клиентов по всему Минску.',
                'phone': '+375 (17) 123-45-67',
                'email': 'info@cleaningpro.by',
                'address': 'г. Минск, ул. Примерная, д. 1',
                'founded_year': 2015,
            }
        )

        specs = []
        for name, desc in [
            ('Уборка жилых помещений', 'Квартиры, дома, коттеджи'),
            ('Уборка коммерческих помещений', 'Офисы, магазины, склады'),
            ('Химчистка', 'Ковры, мягкая мебель, текстиль'),
            ('Специализированная уборка', 'После ремонта, пожара, потопа'),
        ]:
            s, _ = Specialization.objects.get_or_create(name=name, defaults={'description': desc})
            specs.append(s)

        types_data = [
            ('Стандартная уборка', '🧹', 'Регулярная уборка помещений'),
            ('Генеральная уборка', '✨', 'Полная глубокая уборка'),
            ('Уборка после ремонта', '🔨', 'Уборка строительного мусора и пыли'),
            ('Химчистка мебели', '🛋️', 'Чистка ковров и мягкой мебели'),
            ('Мытьё окон', '🪟', 'Профессиональная мойка окон'),
        ]
        service_types = []
        for name, icon, desc in types_data:
            st, _ = ServiceType.objects.get_or_create(name=name, defaults={'icon': icon, 'description': desc})
            service_types.append(st)

        services_data = [
            ('Уборка однокомнатной квартиры', service_types[0], 50, 'уборка'),
            ('Уборка двухкомнатной квартиры', service_types[0], 75, 'уборка'),
            ('Уборка трёхкомнатной квартиры', service_types[0], 100, 'уборка'),
            ('Генеральная уборка квартиры', service_types[1], 150, 'уборка'),
            ('Генеральная уборка офиса', service_types[1], 200, 'кв.м.'),
            ('Уборка после ремонта до 50 кв.м.', service_types[2], 120, 'объект'),
            ('Уборка после ремонта до 100 кв.м.', service_types[2], 200, 'объект'),
            ('Химчистка дивана', service_types[3], 80, 'единица'),
            ('Химчистка ковра до 10 кв.м.', service_types[3], 60, 'ковёр'),
            ('Химчистка кресла', service_types[3], 40, 'единица'),
            ('Мытьё окон (до 10 шт.)', service_types[4], 50, 'услуга'),
            ('Мытьё витражей', service_types[4], 90, 'кв.м.'),
            ('Уборка подъезда', service_types[0], 30, 'подъезд'),
        ]
        services = []
        for name, stype, price, unit in services_data:
            svc, _ = Service.objects.get_or_create(
                name=name,
                defaults={'service_type': stype, 'price': price, 'unit': unit,
                          'description': f'Профессиональная услуга: {name}. Качество гарантировано.'}
            )
            services.append(svc)

        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'first_name': 'Администратор', 'last_name': 'Системы',
                      'email': 'admin@cleaningpro.by', 'is_staff': True, 'is_superuser': True}
        )
        if _:
            admin_user.set_password('admin123')
            admin_user.save()

        employees = []
        emp_data = [
            ('emp1', 'Иван', 'Петров', 'ivan@cleaningpro.by', '+375 (29) 111-11-11', 'Старший клинер', specs[0], date(1988, 6, 15)),
            ('emp2', 'Мария', 'Сидорова', 'maria@cleaningpro.by', '+375 (29) 222-22-22', 'Специалист химчистки', specs[2], date(1992, 3, 20)),
            ('emp3', 'Алексей', 'Козлов', 'alexey@cleaningpro.by', '+375 (29) 333-33-33', 'Мойщик окон', specs[1], date(1985, 11, 5)),
        ]
        for username, first, last, email, phone, pos, spec, bdate in emp_data:
            u, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': first, 'last_name': last, 'email': email}
            )
            if created:
                u.set_password('emp123')
                u.save()
            emp, _ = Employee.objects.get_or_create(
                user=u,
                defaults={'phone': phone, 'position': pos, 'specialization': spec,
                          'birth_date': bdate, 'address': 'г. Минск',
                          'hire_date': date(2020, 1, 1)}
            )
            employees.append(emp)

        clients = []
        client_data = [
            ('client1', 'Анна', 'Иванова', 'anna@mail.by', '+375 (29) 444-44-44', date(1990, 5, 15), 'г. Минск, ул. Ленина, 10'),
            ('client2', 'Пётр', 'Смирнов', 'petr@mail.by', '+375 (29) 555-55-55', date(1985, 3, 20), 'г. Минск, пр. Победы, 5'),
            ('client3', 'Елена', 'Новикова', 'elena@mail.by', '+375 (44) 666-66-66', date(1995, 7, 10), 'г. Минск, ул. Советская, 3'),
            ('client4', 'Дмитрий', 'Федоров', 'dmitry@mail.by', '+375 (44) 777-77-77', date(1988, 12, 1), 'г. Минск, ул. Мира, 8', 'ООО ТехноСервис'),
            ('client5', 'Светлана', 'Морозова', 'svetlana@mail.by', '+375 (25) 888-88-88', date(1992, 9, 25), 'г. Минск, ул. Садовая, 12'),
        ]
        for item in client_data:
            username, first, last, email, phone, bdate, addr = item[:7]
            company = item[7] if len(item) > 7 else ''
            u, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': first, 'last_name': last, 'email': email}
            )
            if created:
                u.set_password('client123')
                u.save()
            cl, _ = Client.objects.get_or_create(
                user=u,
                defaults={'phone': phone, 'birth_date': bdate, 'address': addr,
                          'company_name': company,
                          'client_type': 'corporate' if company else 'individual'}
            )
            clients.append(cl)

        statuses = ['completed', 'completed', 'completed', 'in_progress', 'pending', 'confirmed', 'cancelled']
        today = date.today()
        for i, client in enumerate(clients):
            for j in range(2):
                status = statuses[(i + j) % len(statuses)]
                sched = today + timedelta(days=random.randint(-30, 30))
                order, created = Order.objects.get_or_create(
                    client=client,
                    address=client.address,
                    scheduled_date=sched,
                    defaults={
                        'employee': employees[i % len(employees)],
                        'status': status,
                        'total_price': 0,
                        'notes': f'Тестовый заказ {i+1}-{j+1}',
                    }
                )
                if created:
                    chosen = random.sample(services[:6], k=random.randint(1, 3))
                    for svc in chosen:
                        qty = random.randint(1, 3)
                        OrderService.objects.get_or_create(
                            order=order, service=svc,
                            defaults={'quantity': qty, 'price': svc.price}
                        )
                    order.recalculate_total()

        promos_data = [
            ('CLEAN10', 10, 'Скидка 10% для новых клиентов', today - timedelta(days=30), today + timedelta(days=60)),
            ('SUMMER20', 20, 'Летняя скидка 20%', today - timedelta(days=10), today + timedelta(days=90)),
            ('OFFICE15', 15, 'Скидка на уборку офисов', today - timedelta(days=5), today + timedelta(days=30)),
            ('OLD30', 30, 'Архивная акция', today - timedelta(days=100), today - timedelta(days=10)),
        ]
        for code, pct, desc, vfrom, vto in promos_data:
            PromoCode.objects.get_or_create(
                code=code,
                defaults={'discount_percent': pct, 'description': desc,
                          'valid_from': vfrom, 'valid_to': vto,
                          'is_active': vto >= today}
            )

        reviews_data = [
            ('Анна И.', clients[0], 5, 'Отличная работа! Квартира блестит, все чисто и аккуратно.'),
            ('Пётр С.', clients[1], 4, 'Хорошее качество уборки, пришли вовремя.'),
            ('Елена Н.', clients[2], 5, 'Очень довольна результатом! Рекомендую всем.'),
            ('Дмитрий Ф.', clients[3], 3, 'Нормально, но можно было лучше убрать углы.'),
            ('Светлана М.', clients[4], 5, 'Профессионалы своего дела! Уже третий раз заказываю.'),
        ]
        for name, client, rating, text in reviews_data:
            Review.objects.get_or_create(
                name=name,
                defaults={'client': client, 'rating': rating, 'text': text}
            )

        articles_data = [
            ('5 советов для поддержания чистоты',
             'Эксперты КлинингПро делятся секретами.',
             'Поддерживать чистоту в доме легко, если следовать простым правилам. '
             'Во-первых, убирайте каждый день понемногу. Во-вторых, используйте качественные средства. '
             'В-третьих, не забывайте о вентиляции. В-четвёртых, регулярно стирайте текстиль. '
             'В-пятых, заказывайте профессиональную уборку раз в квартал.'),
            ('Как подготовиться к генеральной уборке',
             'Подготовка — залог успеха.',
             'Генеральная уборка требует планирования. Заранее освободите шкафы, вынесите лишние вещи '
             'и подготовьте все необходимые средства. Профессиональная команда КлинингПро справится '
             'с любым объёмом работы быстро и качественно.'),
            ('Новые услуги компании в 2024 году',
             'Расширяем спектр услуг!',
             'В этом году мы добавили новые услуги: химчистку штор, мойку фасадов зданий '
             'и дезинфекцию помещений. Звоните нам для получения подробной информации.'),
        ]
        for title, summary, content in articles_data:
            Article.objects.get_or_create(
                title=title,
                defaults={'summary': summary, 'content': content, 'is_published': True}
            )

        faqs_data = [
            ('Что включает стандартная уборка?',
             'Стандартная уборка включает: подметание и мытьё полов, вытирание пыли со всех поверхностей, '
             'уборку санузла, вынос мусора, протирку зеркал.'),
            ('Сколько времени занимает уборка?',
             'Время зависит от площади и состояния помещения. Однокомнатная квартира — около 2 часов, '
             'трёхкомнатная — 4-5 часов. Генеральная уборка занимает на 50% больше времени.'),
            ('Нужно ли мне быть дома во время уборки?',
             'Нет, вы можете оставить ключи нашему сотруднику. Все сотрудники проверены и несут '
             'материальную ответственность.'),
            ('Какие средства вы используете?',
             'Мы используем профессиональную химию Kärcher, Pramol и Cleaneq, которая безопасна '
             'для людей, животных и экологии.'),
            ('Как применить промокод?',
             'Укажите промокод при создании заказа в поле "Примечания", и менеджер применит скидку '
             'при подтверждении заказа.'),
        ]
        for q, a in faqs_data:
            FAQ.objects.get_or_create(question=q, defaults={'answer': a})

        vacs_data = [
            ('Клинер (уборщик помещений)', 500, 800,
             'Требования: опыт работы от 1 года, ответственность, аккуратность. '
             'Обязанности: уборка жилых и коммерческих помещений по стандартам компании.'),
            ('Специалист по химчистке', 700, 1000,
             'Требования: знание химических средств, опыт работы с профессиональным оборудованием. '
             'Обязанности: химчистка ковров, мягкой мебели, штор.'),
            ('Менеджер по продажам', 800, 1200,
             'Требования: навыки продаж, коммуникабельность, знание ПК. '
             'Обязанности: работа с клиентами, оформление заказов, консультации.'),
        ]
        for title, sal_from, sal_to, desc in vacs_data:
            Vacancy.objects.get_or_create(
                title=title,
                defaults={'salary_from': sal_from, 'salary_to': sal_to,
                          'description': desc, 'is_active': True}
            )

        self.stdout.write(self.style.SUCCESS('Done! Seeded all demo data.'))
        self.stdout.write('Logins: admin/admin123, emp1/emp123, client1/client123 ... client5/client123')
