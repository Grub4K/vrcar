from __future__ import annotations


def parse_args():
    import argparse

    root_parser = argparse.ArgumentParser("vrcar")
    parsers = root_parser.add_subparsers(dest="mode", required=True)

    parser = parsers.add_parser(
        "server",
        help="run the vrcar server",
    )
    parser.add_argument(
        "-b",
        "--bind",
        metavar="ADDRESS",
        default="0.0.0.0",
        help="the address to bind to (default: all addresses)",
    )
    parser.add_argument(
        "--camera-port",
        metavar="PORT",
        type=int,
        default=12_345,
        help="the camera stream port (default: %(default)s)",
    )
    parser.add_argument(
        "--controls-port",
        metavar="PORT",
        type=int,
        default=23_456,
        help="the controls port (default: %(default)s)",
    )

    parser = parsers.add_parser(
        "client",
        help="run the vrcar pygame demo client",
    )
    parser.add_argument(
        "address",
        help="the address to connect to",
    )
    parser.add_argument(
        "--camera-port",
        metavar="PORT",
        type=int,
        default=12_345,
        help="the camera stream port (default: %(default)s)",
    )
    parser.add_argument(
        "--controls-port",
        metavar="PORT",
        type=int,
        default=23_456,
        help="the controls port (default: %(default)s)",
    )

    return root_parser.parse_args()


def main():
    import logging

    import vrcar
    import vrcar.log

    logger = logging.getLogger(vrcar.__name__)

    vrcar.log.setup(name_length=30, debug=True)
    logger.info(f"{vrcar.__name__} v{vrcar.__version__}")

    args = parse_args()

    if args.mode == "server":
        import vrcar.server

        vrcar.server.run(args.bind, args.camera_port, args.controls_port)

    elif args.mode == "client":
        import vrcar.client

        vrcar.client.run(args.address, args.camera_port, args.controls_port)


if __name__ == "__main__":
    main()
