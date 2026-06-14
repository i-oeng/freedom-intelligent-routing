import unittest

from sqlalchemy import create_engine, text

from main import TicketAnalysis, resolve_image_path
from router import route_ticket


class AttachmentPathTests(unittest.TestCase):
    def test_resolves_sample_data_attachment(self):
        image_path = resolve_image_path("order_error.png")

        self.assertIsNotNone(image_path)
        self.assertTrue(image_path.name.endswith("order_error.png"))

    def test_returns_none_for_missing_attachment(self):
        self.assertIsNone(resolve_image_path("missing-file.png"))


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE tickets (
                    id INTEGER PRIMARY KEY,
                    segment TEXT,
                    country TEXT,
                    city TEXT,
                    street TEXT
                )
            """))
            conn.execute(text("""
                CREATE TABLE managers (
                    id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    role TEXT,
                    skills TEXT,
                    unit_name TEXT,
                    current_load INTEGER
                )
            """))
            conn.execute(text("""
                CREATE TABLE business_units (
                    id INTEGER PRIMARY KEY,
                    office_name TEXT,
                    address TEXT
                )
            """))
            conn.execute(text("""
                INSERT INTO tickets (id, segment, country, city, street)
                VALUES
                    (2, 'Mass', 'USA', NULL, NULL),
                    (3, 'Mass', 'USA', NULL, NULL)
            """))
            conn.execute(text("""
                INSERT INTO managers (id, full_name, role, skills, unit_name, current_load)
                VALUES
                    (1, 'Manager Low', 'Специалист', 'RU', 'Астана', 0),
                    (2, 'Manager High', 'Специалист', 'RU', 'Астана', 4),
                    (3, 'Almaty Low', 'Специалист', 'RU', 'Алматы', 0),
                    (4, 'Almaty High', 'Специалист', 'RU', 'Алматы', 4)
            """))

    def test_routes_to_lowest_load_hub_manager(self):
        ai_data = {"ticket_type": "Консультация", "language": "RU"}

        name, office, manager_id = route_ticket(2, self.engine, ai_data)

        self.assertEqual(name, "Manager Low")
        self.assertEqual(office, "Астана")
        self.assertEqual(manager_id, 1)

        with self.engine.connect() as conn:
            current_load = conn.execute(
                text("SELECT current_load FROM managers WHERE id = 1")
            ).scalar_one()
        self.assertEqual(current_load, 1)

    def test_odd_ticket_still_routes_to_lowest_load_manager(self):
        ai_data = {"ticket_type": "Консультация", "language": "RU"}

        name, office, manager_id = route_ticket(3, self.engine, ai_data)

        self.assertEqual(name, "Almaty Low")
        self.assertEqual(office, "Алматы")
        self.assertEqual(manager_id, 3)


class TicketAnalysisValidationTests(unittest.TestCase):
    def test_normalizes_near_miss_ticket_type(self):
        analysis = TicketAnalysis.model_validate({
            "ticket_type": "Нерабочеспособность приложения",
            "sentiment": "негативный",
            "priority": 12,
            "language": "ru",
            "summary": "Ошибка при отправке приказа.",
        })

        self.assertEqual(analysis.ticket_type, "Неработоспособность приложения")
        self.assertEqual(analysis.sentiment, "Негативный")
        self.assertEqual(analysis.priority, 10)
        self.assertEqual(analysis.language, "RU")


if __name__ == "__main__":
    unittest.main()
