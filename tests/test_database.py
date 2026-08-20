import unittest

from app.core.database import SessionLocal


class DatabaseSessionTest(unittest.TestCase):
    def test_committed_entities_remain_loaded_for_response_mapping(self):
        self.assertFalse(SessionLocal.kw["expire_on_commit"])


if __name__ == "__main__":
    unittest.main()
