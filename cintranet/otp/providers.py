#import oath

class Provider(object):
    def __init__(self, name, url, key=None, generator=None, meta=None):
        self.name = name
        self.generator = generator
        #if not generator and key:
            #self.generator = lambda: oath.from_b32key(key).generate()
        self.meta = meta or {}
        self.url = url

    def generate(self):
        return self.generator()

PROVIDERS = [
    # REDACTED #
]