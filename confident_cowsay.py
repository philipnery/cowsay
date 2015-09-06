import contextlib
import shlex
from subprocess import Popen, PIPE


class NullObject(object):
    def __init__(self, *args, **kwargs):
        pass

    def __unicode__(self):
        return ""

    def __repr__(self):
        return "NullObject"

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        return self

    def __setattr__(self, name, value):
        return self

    def __delattr__(self, name):
        return self

    def __bool__(self):
        return False

    __str__ = __unicode__
    __nonzero__ = __bool__


def Maybe(value):
    if value is None:
        return NullObject()
    else:
        return value


class NullSink:
    def __init__(self, *args, **kwargs):
        pass

    def name(self):
        return "return value"


def to_list(obj=None):
    if isinstance(obj, list):
        return obj
    elif obj:
        return [obj]
    else:
        return []


def to_file(obj):
    if isinstance(obj, file):
        return obj
    else:
        return NullSink()


class Cow:
    def __init__(self, logger=NullObject()):
        self.logger = logger
        self.status_code = 0

    def say(self, message, options={}):
        width = options.get("width", 40)
        eyes = Maybe(options.get("strings")).get("eyes")
        destination = to_file(options.get("out")).name
        out = Maybe(options.get("out"))
        messages = to_list(message)
        command = "cowsay"
        command += " -W {}".format(width)
        command += " -e '{}'".format(eyes) if eyes else ""

        results = []
        for message in messages:
            with self.checked_popen(shlex.split(command), stdin=PIPE, stdout=PIPE) as process:
                process.stdin.write(message)
                process.stdin.close()

                result = process.stdout.read()
                results.append(result)
        output = "\n".join(results)
        out.write(output)

        self.logger.info("Wrote to {}".format(destination))
        return output

    @contextlib.contextmanager
    def check_for_child_exit_status(self):
        yield
        if self.status_code > 172:
            raise ValueError("Command exited with status {}".format(self.status_code))

    @contextlib.contextmanager
    def checked_popen(self, *args, **kwargs):
        with self.check_for_child_exit_status():
            process = Popen(*args, **kwargs)
            try:
                yield process
                self.status_code = process.wait()
            except OSError:
                pass
