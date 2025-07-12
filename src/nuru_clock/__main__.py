from .client import ClockAPI
import trio


def main():
    clock_api = ClockAPI("Nuru Clock")
    trio.run(clock_api.clock_game)


if __name__ == "__main__":
    main()