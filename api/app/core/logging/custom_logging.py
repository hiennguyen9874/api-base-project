from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import loguru
from casbin.util.log import configure_logging
from loguru import logger


class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        0: "NOTSET",
    }

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while (
            frame.f_code.co_filename == logging.__file__
            or "sentry_sdk/integrations" in frame.f_code.co_filename
        ):
            frame = frame.f_back  # type: ignore
            depth += 1

        log = logger.bind()
        log.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def patcher(record: loguru.Record) -> None:
    # https://github.com/Delgan/loguru/issues/504#issuecomment-917365972
    exception = record["exception"]
    if exception is not None:
        fixed = Exception(str(exception.value))
        record["exception"] = exception._replace(value=fixed)


class CustomizeLogger:
    # https://medium.com/1mgofficial/how-to-override-uvicorn-logger-in-fastapi-using-loguru-124133cdcd4e

    @classmethod
    def make_logger(cls, config_path: Path) -> loguru.Logger:
        config = cls.load_logging_config(config_path)
        logging_config = config.get("logger")
        return cls.customize_logging(
            logging_config.get("path"),  # type: ignore
            level=logging_config.get("level"),  # type: ignore
            retention=logging_config.get("retention"),  # type: ignore
            rotation=logging_config.get("rotation"),  # type: ignore
            format=logging_config.get("format"),  # type: ignore
        )

    @classmethod
    def customize_logging(
        cls, filepath: Path, level: str, rotation: str, retention: str, format: str
    ) -> loguru.Logger:
        """Return customized logger object.

        :param level: Logging level.
        :param diagnose: Diagnose status.
        :param colorize: Coloring status.
        :param log_format: Log format string.
        :return: customized logger object.
        """
        # Remove all existing loggers.
        logger.remove()

        # Create a basic Loguru logging config
        logger.add(sys.stdout, enqueue=True, backtrace=True, level=level.upper(), format=format)
        logger.add(
            str(filepath),
            rotation=rotation,
            retention=retention,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=format,
        )

        # Prepare to incorporate python standard logging
        logging.basicConfig(handlers=[InterceptHandler()], level=0)

        seen = set()
        for logger_name in [
            *logging.root.manager.loggerDict.keys(),
            "gunicorn",
            "gunicorn.access",
            "gunicorn.error",
            "uvicorn",
            "uvicorn.access",
            "uvicorn.error",
            "casbin",
            "casbin.policy",
            "casbin.enforcer",
            "casbin.role",
            "elastic_transport",
            "elastic_transport.transport",
            "ray",
            "ray.data",
            "ray.tune",
            "ray.rllib",
            "ray.train",
            "ray.serve",
        ]:
            if logger_name not in seen:
                seen.add(logger_name.split(".")[0])
                mod_logger = logging.getLogger(logger_name)

                if logger_name in [
                    "elasticsearch",
                    "elastic_transport",
                    "elastic_transport.transport",
                ]:
                    mod_logger.setLevel(logging.WARNING)
                    mod_logger.handlers = [InterceptHandler(level="WARNING")]
                else:
                    mod_logger.handlers = [InterceptHandler(level=level.upper())]

                mod_logger.propagate = False

        logger.configure(
            patcher=patcher,
            extra={
                "otel_spanid": "?",
                "otel_traceid": "?",
            },
        )

        return logger.bind(method=None)

    @classmethod
    def load_logging_config(cls, config_path: Path) -> dict[str, dict[str, str]]:
        config = None
        with open(config_path) as config_file:
            config = json.load(config_file)
        return config


def make_customize_logger(path: Path) -> loguru.Logger:
    configure_logging()
    return CustomizeLogger.make_logger(path)
