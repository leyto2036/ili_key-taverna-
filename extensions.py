"""Shared Flask extensions, separated to avoid model/app import cycles."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
