import argparse
import asyncio
from moto import testrunner
from moto.server import app
from types import SimpleNamespace


def get_args() -> SimpleNamespace:
    parser = argparse.ArgumentParser(
        description='Runs a checkup test based on your environment',
        prog='status_cli')

    parser.add_argument('--service-file', type=str, default='services.yml',
                        help='Which services file to use. Default: "services.yml"')
    parser.add_argument('--hosts-file', type=str, default='hosts.yml',
                        help='Which host file to use. Default: "hosts.yml"')

    parser.add_argument('--exec', type=str, default='all_tests',
                        choices=['all_tests', 'server'])

    args = parser.parse_args()

    return args


def main():
    loop = asyncio.get_event_loop()
    args = get_args()

    if args.exec == 'all_tests':
        loop.run_until_complete(testrunner.run_all_tests(hosts_filepath=args.hosts_file,
                                                         services_filepath=args.service_file))
    elif args.exec == 'server':
        app.run(debug=False, host='0.0.0.0')


if __name__ == '__main__':
    main()
