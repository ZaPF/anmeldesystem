#!/usr/bin/env python3
from flask_script import Manager
from app import create_app, check_sanity

app = create_app()
manager = Manager(app)

@manager.command
def sanity():
    """
    Run a number of sanity checks and attempt to automatically
    fix any inconsistencies.
    """
    check_sanity()

if __name__ == "__main__":
    manager.run()
