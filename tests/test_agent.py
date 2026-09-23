import pytest
from backend.agent.agent_service import agent_service
from backend.database.db import SessionLocal, init_db

def setup_module():
    init_db()

def test_agent_out_of_scope_query():
    db = SessionLocal()
    try:
        res = agent_service.chat(db=db, query="What is quantum gravity in astrophysics?", document_id=None)
        assert res["is_grounded"] is False or "cannot find" in res["response"].lower()
    finally:
        db.close()
