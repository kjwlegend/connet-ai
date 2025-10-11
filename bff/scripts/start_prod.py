
"""Start the BFF service using the production environment profile."""

from scripts.start_dev import start


def main() -> None:
    start("prod")


if __name__ == "__main__":
    main()
