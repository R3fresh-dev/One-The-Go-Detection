"""Run ONLY on the disposable integration database, after API tests."""
import json
import os
from sqlalchemy import create_engine,text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from otgd.config import settings
from otgd.migrate import migrate


def main():
    cfg=settings()
    if cfg.environment!='test' or os.environ.get('OTGD_DISPOSABLE_DATABASE')!='true':raise RuntimeError('Explicit disposable test database is required')
    url=make_url(cfg.db_url())
    if url.get_backend_name()!='postgresql' or url.database!='otgd_ci':raise RuntimeError('Dedicated PostgreSQL integration database required')
    if not cfg.app_database_password:raise RuntimeError('Integration runtime-role password is required')
    migrate();migrate()
    admin=create_engine(url,pool_size=1,max_overflow=0)
    with admin.connect() as connection:
        width=connection.execute(text("SELECT character_maximum_length FROM information_schema.columns WHERE table_schema='public' AND table_name='system_state' AND column_name='key'")).scalar()
        assert width>=72, 'The subject HMAC lookup key is 72 characters'
    admin.dispose()
    app=create_engine(url.set(username=cfg.app_database_user,password=cfg.app_database_password),pool_size=1,max_overflow=0)
    with app.connect() as connection:
        assert connection.execute(text('SELECT count(*) FROM system_state')).scalar()>=1
    for statement in ["CREATE TABLE forbidden_runtime_ddl (id integer)","INSERT INTO operator_registry (id,kind,body,active) VALUES ('forbidden','qualification','{}',true)","INSERT INTO system_state (key,body) VALUES ('forbidden','{}')","UPDATE audit SET action='forbidden' WHERE false","DELETE FROM audit WHERE false"]:
        try:
            with app.begin() as connection:connection.execute(text(statement))
        except DBAPIError as error:
            if getattr(error.orig,'sqlstate',None)!='42501':raise
        else:raise RuntimeError('Runtime role unexpectedly has DDL/authority-write permission')
    print(json.dumps({'status':'passed','database':'actual_postgresql','migration_runs':2,'runtime_ddl':'denied','authority_write':'denied','audit_update_delete':'denied'}))

if __name__=='__main__':main()
