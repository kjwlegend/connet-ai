
"""Start the BFF service using the UAT environment profile."""

from scripts.start_dev import start


def main() -> None:
    start("uat")


if __name__ == "__main__":
    main()
