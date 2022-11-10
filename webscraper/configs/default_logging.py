logging = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters":
    {
        "console":
        {
          "format": "%(name)-{auto_field_width}s | %(levelname)-8s | %(message)s"
        },
        "console_time":
        {
          "format": "%(asctime)s | %(levelname)-8s | %(message)s"
        },
        "only_msg":
        {
          "format": "%(message)s"
        },
        "simple":
        {
          "format": "%(levelname)-8s %(message)s"
        },
        "simple2":
        {
          "format": "%(levelname)-8s | %(message)s"
        },
        "verbose":
        {
          "format": "%(asctime)s | %(name)-{auto_field_width}s | %(levelname)-8s | %(message)s"
        }
    },

    "handlers":
    {
        "console":
        {
          "level": "WARNING",
          "class": "logging.StreamHandler",
          "formatter": "only_msg"
        },
        "console_only_msg":
        {
          "level": "INFO",
          "class": "logging.StreamHandler",
          "formatter": "only_msg"
        },
        "file":
        {
          "level": "INFO",
          "class": "logging.FileHandler",
          "filename": "debug.log",
          "mode": "a",
          "formatter": "simple",
          "delay": True
        }
    },

    "loggers":
    {
        # -----------------------------
        # Loggers using console handler
        # -----------------------------
        "":
        {
          "level": "DEBUG",
          "handlers": ["console"],
          "propagate": False
        },
    },

    "root":
    {
        "level": "INFO",
        "handlers": ["console"],
        "propagate": False
    }
}