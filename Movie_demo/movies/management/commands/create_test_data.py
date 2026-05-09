from django.core.management.base import BaseCommand
from movies.models import Cinema, MovieSchedule, Movie
from datetime import datetime, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = '创建测试影院和场次数据'

    def handle(self, *args, **options):
        # 创建测试影院
        cinemas_data = [
            {
                'name': '万达影城(王府井店)',
                'address': '北京市东城区王府井大街255号',
                'city': '北京',
                'phone': '010-12345678',
                'latitude': 39.9042,
                'longitude': 116.4074
            },
            {
                'name': '华谊兄弟影院(三里屯店)',
                'address': '北京市朝阳区三里屯路19号',
                'city': '北京',
                'phone': '010-87654321',
                'latitude': 39.9369,
                'longitude': 116.4609
            },
            {
                'name': '博纳国际影城(朝阳大悦城店)',
                'address': '北京市朝阳区朝阳北路101号',
                'city': '北京',
                'phone': '010-11223344',
                'latitude': 39.9289,
                'longitude': 116.4883
            }
        ]

        created_cinemas = []
        for cinema_data in cinemas_data:
            cinema, created = Cinema.objects.get_or_create(
                name=cinema_data['name'],
                defaults=cinema_data
            )
            if created:
                self.stdout.write(f'创建影院: {cinema.name}')
            created_cinemas.append(cinema)

        # 获取一些电影用于创建场次
        movies = Movie.objects.all()[:3]
        if not movies:
            self.stdout.write('没有电影数据，请先添加一些电影')
            return

        # 创建场次
        base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        
        for cinema in created_cinemas:
            for movie in movies:
                # 为每个电影在每个影院创建3个场次
                for i in range(3):
                    start_time = base_time + timedelta(hours=i*3, days=0)
                    end_time = start_time + timedelta(hours=2)
                    
                    schedule, created = MovieSchedule.objects.get_or_create(
                        movie=movie,
                        cinema=cinema,
                        start_time=start_time,
                        defaults={
                            'end_time': end_time,
                            'price': Decimal('45.00'),
                            'available_seats': 100,
                            'total_seats': 100
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'创建场次: {movie.title} - {cinema.name} - {start_time}')

        self.stdout.write(self.style.SUCCESS('测试数据创建完成！')) 