"""Script to create DB tables."""
from postgres_client import PostgresClient


def main():
    """Program entrypoint."""
    client = PostgresClient()
    client.create_tables()


if __name__ == "__main__":
    main()
