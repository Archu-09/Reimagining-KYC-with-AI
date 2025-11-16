"""Alembic env for autogenerate using the project's SQLAlchemy `Base`.

This file lets you run alembic commands from the `backend` folder. It expects
`DATABASE_URL` to be set in the environment or uses `app.db.DATABASE_URL`.
"""
from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config, pool

from alembic import context

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = os.getenv('DATABASE_URL') or config.get_main_option('sqlalchemy.url')
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = os.getenv('DATABASE_URL') or configuration.get('sqlalchemy.url')
    connectable = engine_from_config(configuration, prefix='sqlalchemy.', poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
