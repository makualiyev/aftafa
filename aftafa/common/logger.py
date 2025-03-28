import logging
import json
from typing import Literal
import sys


class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.

    @param dict fmt_dict: Key: logging format attribute pairs. Defaults to {"message": "message"}.
    @param str time_format: time.strftime() format string. Default: "%Y-%m-%dT%H:%M:%S"
    @param str msec_format: Microsecond formatting. Appended at the end. Default: "%s.%03dZ"

    Copyright (c) https://stackoverflow.com/questions/50144628/python-logging-into-file-as-a-dictionary-or-json
    """
    def __init__(self, fmt_dict: dict = None, time_format: str = "%Y-%m-%dT%H:%M:%S", msec_format: str = "%s.%03dZ"):
        self.fmt_dict = fmt_dict if fmt_dict is not None else {"message": "message"}
        self.default_time_format = time_format
        self.default_msec_format = msec_format
        self.datefmt = None

    def usesTime(self) -> bool:
        """
        Overwritten to look for the attribute in the format dict values instead of the fmt string.
        """
        return "asctime" in self.fmt_dict.values()

    def formatMessage(self, record) -> dict:
        """
        Overwritten to return a dictionary of the relevant LogRecord attributes instead of a string. 
        KeyError is raised if an unknown attribute is provided in the fmt_dict. 
        """
        return {fmt_key: record.__dict__[fmt_val] for fmt_key, fmt_val in self.fmt_dict.items()}

    def format(self, record) -> str:
        """
        Mostly the same as the parent's class method, the difference being that a dict is manipulated and dumped as JSON
        instead of a string.
        """
        record.message = record.getMessage()
        
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            message_dict["exc_info"] = record.exc_text

        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict, default=str)
    

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="logs/ok.log",
    format="""{"asctime" : "%(asctime)s", "args": "%(args)s", "created" : "%(created)s", "exc_info" : "%(exc_info)s", "exc_text" : "%(exc_text)s", "filename" : "%(filename)s", "funcName" : "%(funcName)s", "levelname" : "%(levelname)s", "levelno" : "%(levelno)s", "lineno" : "%(lineno)s", "module" : "%(module)s", "msecs" : "%(msecs)s", "message" : "%(message)s", "msg" : "%(msg)s", "name" : "%(name)s", "pathname" : "%(pathname)s", "process" : "%(process)s", "processName" : "%(processName)s", "relativeCreated" : "%(relativeCreated)s", "stack_info" : "%(stack_info)s", "thread" : "%(thread)s", "threadName" : "threadName"}""",
    datefmt='%m/%d/%Y %H:%M:%S',
    encoding="utf-8",
    level=logging.DEBUG
)

stream_handler = logging.StreamHandler(stream=sys.stdout)
stream_formatter = logging.Formatter(
    fmt="""{"asctime" : "%(asctime)s", "args": "%(args)s", "created" : "%(created)s", "exc_info" : "%(exc_info)s", "exc_text" : "%(exc_text)s", "filename" : "%(filename)s", "funcName" : "%(funcName)s", "levelname" : "%(levelname)s", "levelno" : "%(levelno)s", "lineno" : "%(lineno)s", "module" : "%(module)s", "msecs" : "%(msecs)s", "message" : "%(message)s", "msg" : "%(msg)s", "name" : "%(name)s", "pathname" : "%(pathname)s", "process" : "%(process)s", "processName" : "%(processName)s", "relativeCreated" : "%(relativeCreated)s", "stack_info" : "%(stack_info)s", "thread" : "%(thread)s", "threadName" : "threadName"}\n""",
    datefmt="%m/%d/%Y %H:%M:%S"
)
stream_handler.setFormatter(stream_formatter)

json_handler = logging.FileHandler("logs/log.jsonl", mode="a", encoding="utf-8")
json_formatter = JsonFormatter(
    {
        "asctime" : "asctime",
        "args": "args",
        "created" : "created",
        "exc_info" : "exc_info",
        "exc_text" : "exc_text",
        "filename" : "filename",
        "funcName" : "funcName",
        "levelname" : "levelname",
        "levelno" : "levelno",
        "lineno" : "lineno",
        "module" : "module",
        "msecs" : "msecs",
        "message" : "message",
        "msg" : "msg",
        "name" : "name",
        "pathname" : "pathname",
        "process" : "process",
        "processName" : "processName",
        "relativeCreated" : "relativeCreated",
        "stack_info" : "stack_info",
        "thread" : "thread",
        "threadName" : "threadName"
    }
)
json_handler.setFormatter(json_formatter)
logger.addHandler(json_handler)
logger.addHandler(stream_handler)
