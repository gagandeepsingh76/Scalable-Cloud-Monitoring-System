from __future__ import with_statement
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
	fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.database import Base
from app import models  # noqa: F401 - ensure models are imported for autogenerate

target_metadata = Base.metadata


def get_url() -> str:
	return os.getenv(
		"DATABASE_URL",
		"postgresql+psycopg2://monitor:monitorpass@localhost:5432/monitoring",
	)


def run_migrations_offline() -> None:
	url = get_url()
	context.configure(
		url=url,
		target_metadata=target_metadata,
		literal_binds=True,
		compare_type=True,
	)

	with context.begin_transaction():
		context.run_migrations()


def run_migrations_online() -> None:
	configuration = config.get_section(config.config_ini_section)
	configuration["sqlalchemy.url"] = get_url()
	engine = engine_from_config(
		configuration,
		prefix="sqlalchemy.",
		poolclass=pool.NullPool,
	)

	with engine.connect() as connection:
		context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

		with context.begin_transaction():
			context.run_migrations()


if context.is_offline_mode():
	run_migrations_offline()
else:
	run_migrations_online()

