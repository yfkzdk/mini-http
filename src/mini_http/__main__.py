"""CLI entry."""

from .server import run_server


def main():
    import argparse
    p = argparse.ArgumentParser(prog="mini-http")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--root", default="www")
    args = p.parse_args()
    run_server(args.host, args.port, args.root)


if __name__ == "__main__":
    main()
