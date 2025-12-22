"""
Seeder command for geography app (Countries and Cities).

Seeds the database with realistic country and city data.
"""

from typing import Any, List, Tuple

from apps.core.management.commands.base_seeder import BaseSeederCommand
from apps.geography.models import Country, City


class Command(BaseSeederCommand):
    """
    Seed geography data (countries and cities).

    Creates countries and their associated cities with realistic data.
    This is a foundation seeder with no dependencies.
    """

    help = 'Seed countries and cities data'

    def get_app_name(self) -> str:
        """Get the name of the app being seeded."""
        return 'Geography'

    def seed_data(self, **options: Any) -> int:
        """
        Seed countries and cities.

        Args:
            **options: Command options.

        Returns:
            Total number of objects created (countries + cities).
        """
        countries = self._create_countries()
        cities = self._create_cities(countries)

        return len(countries) + len(cities)

    def clear_data(self) -> None:
        """Clear all geography data."""
        City.objects.all().delete()
        Country.objects.all().delete()

    def _create_countries(self) -> List[Country]:
        """
        Create country data.

        Returns:
            List of created Country instances.
        """
        countries_data: List[Tuple[str, str]] = [
            ('Kazakhstan', 'KZ'),
            ('United States', 'US'),
            ('United Kingdom', 'GB'),
            ('Germany', 'DE'),
            ('France', 'FR'),
            ('Spain', 'ES'),
            ('Italy', 'IT'),
            ('Russia', 'RU'),
            ('Japan', 'JP'),
            ('South Korea', 'KR'),
            ('Canada', 'CA'),
            ('Australia', 'AU'),
            ('Brazil', 'BR'),
            ('Mexico', 'MX'),
            ('India', 'IN'),
            ('China', 'CN'),
            ('Turkey', 'TR'),
            ('Netherlands', 'NL'),
            ('Poland', 'PL'),
            ('Sweden', 'SE'),
        ]

        countries: List[Country] = []
        for name, code in countries_data:
            country, created = Country.objects.get_or_create(
                code=code,
                defaults={'name': name}
            )
            countries.append(country)

        self.stdout.write(f'  Created {len(countries)} countries')
        return countries

    def _create_cities(self, countries: List[Country]) -> List[City]:
        """
        Create city data for all countries.

        Args:
            countries: List of Country instances.

        Returns:
            List of created City instances.
        """
        cities_data: dict[str, List[str]] = {
            'KZ': ['Almaty', 'Astana', 'Shymkent', 'Karaganda', 'Aktobe', 'Taraz', 'Pavlodar'],
            'US': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'San Francisco', 'Seattle', 'Boston', 'Miami'],
            'GB': ['London', 'Manchester', 'Birmingham', 'Liverpool', 'Edinburgh', 'Glasgow', 'Bristol'],
            'DE': ['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne', 'Stuttgart', 'Dresden'],
            'FR': ['Paris', 'Marseille', 'Lyon', 'Toulouse', 'Nice', 'Bordeaux', 'Strasbourg'],
            'ES': ['Madrid', 'Barcelona', 'Valencia', 'Seville', 'Bilbao', 'Malaga'],
            'IT': ['Rome', 'Milan', 'Naples', 'Turin', 'Florence', 'Venice'],
            'RU': ['Moscow', 'Saint Petersburg', 'Novosibirsk', 'Yekaterinburg', 'Kazan'],
            'JP': ['Tokyo', 'Osaka', 'Kyoto', 'Yokohama', 'Nagoya', 'Sapporo'],
            'KR': ['Seoul', 'Busan', 'Incheon', 'Daegu', 'Daejeon'],
            'CA': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa'],
            'AU': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide'],
            'BR': ['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador'],
            'MX': ['Mexico City', 'Guadalajara', 'Monterrey', 'Cancún'],
            'IN': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai'],
            'CN': ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen', 'Chengdu'],
            'TR': ['Istanbul', 'Ankara', 'Izmir', 'Antalya'],
            'NL': ['Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht'],
            'PL': ['Warsaw', 'Krakow', 'Wroclaw', 'Gdansk'],
            'SE': ['Stockholm', 'Gothenburg', 'Malmö', 'Uppsala'],
        }

        country_dict: dict[str, Country] = {c.code: c for c in countries}
        cities: List[City] = []

        for country_code, city_names in cities_data.items():
            if country_code in country_dict:
                country = country_dict[country_code]
                for city_name in city_names:
                    city, created = City.objects.get_or_create(
                        name=city_name,
                        country=country
                    )
                    cities.append(city)

        self.stdout.write(f'  Created {len(cities)} cities')
        return cities
