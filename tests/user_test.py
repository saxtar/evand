import contextlib
import pytest
from app.app import create_app
from config import TestConfig
from app.models import base



@pytest.fixture
def app_empty_db():
    app = create_app(TestConfig)
    meta = base.metadata
    from app import db
    print(db)
    with app.app_context():
        yield app
        with contextlib.closing(db.get_bind().connect()) as con:          
            trans = con.begin()
            for table in reversed(meta.sorted_tables):
                con.execute(table.delete())
            trans.commit()

def test_create_user(app_empty_db):
    with app_empty_db.test_client() as c:
        rv = c.post('/register', json={
            'name': 'flask@example.com', 'password': 'secret'
        })
        assert rv.status == "201 CREATED"
