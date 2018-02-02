import argparse


def get_arguments():

    arg_parser = argparse.ArgumentParser(
        description="lamp client, controlled remotely",
        add_help=True)

    arg_parser.add_argument(
        '--host',
        dest='host',
        default='127.0.0.1',
        help='host name')

    arg_parser.add_argument(
        '--port',
        dest='port',
        default=9999,
        type=int,
        help='port number')

    arg_parser.add_argument(
        '--retry',
        dest='retry_count',
        default=3,
        type=int,
        help='connection retry count')

    args = arg_parser.parse_args()

    if ':' in args.host:
        args.host, port = args.host.split(':', 1)
        args.port = int(port)

    return args
