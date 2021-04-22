class DomainName(str):
    def __getattr__(self, item):
        return DomainName(item + '.' + self)
