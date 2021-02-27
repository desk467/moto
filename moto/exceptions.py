class ServiceNotFound(Exception):
    def __init__(self, service_name):
        super().__init__(self, f'Service "{service_name}" not found.')
        self.service_name = service_name
