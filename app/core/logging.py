import logging, sys, json

def configure_logging():
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            base = {
                "level": record.levelname,
                "msg": record.getMessage(),
                "name": record.name,
            }
            if record.exc_info:
                base["exc_info"] = self.formatException(record.exc_info)
            return json.dumps(base)
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(h)
