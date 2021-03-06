import os

from setuptools import setup

deps = [
    "boto3",
    "click",
    "click-aliases",
    "colorama",
    "databases[postgresql]",
    "fastapi",
    "fastapi-users",
    "gunicorn",
    "jinja2",
    "psycopg2-binary",
    "pydantic",
    "requests",
    "requests-toolbelt",
    "sqlalchemy",
]

setup(
    name="workspacesio",
    version="0.1.0",
    script_name="setup.py",
    python_requires=">3.7",
    zip_safe=False,
    install_requires=deps,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "fast-create-tables=workspacesio.dev_cli:main",
            "wio=workspacesio.cli:cli",
        ],
    },
)
