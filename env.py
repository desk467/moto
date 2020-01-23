import yaml
from collections import defaultdict


def load_hosts(filepath):
    def generate_section_hosts_pair():
        with open(filepath, 'r') as hosts_file:
            hosts_dict = yaml.load(hosts_file.read(), Loader=yaml.SafeLoader)

            for section, hosts in hosts_dict.items():
                for host in hosts:
                    yield (section, host)

    hosts = defaultdict(list)

    for section, host in generate_section_hosts_pair():
        hosts[section].append(host)
        hosts[host].append(section)

    return hosts


def load_services(filepath):
    with open(filepath, 'r') as services_file:
        return yaml.load(services_file.read(), Loader=yaml.SafeLoader)
