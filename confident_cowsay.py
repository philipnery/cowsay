import shlex
from subprocess import Popen, PIPE


class NoneObject(object):
    def __init__(self, *args, **kwargs):
        pass

    def __unicode__(self):
        return ""

    def __repr__(self):
        return "NoneObject"

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
        return NoneObject()
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
    def __init__(self, logger=NoneObject()):
        self.logger = logger

    def say(self, message, options={}):
        width = options.get("width", 40)
        eyes = Maybe(options.get("strings")).get("eyes")
        destination = to_file(options.get("out")).name
        out = Maybe(options.get("out"))
        messages = to_list(message)
        command = "cowsay"
        command += " -W {}".format(width)
        command += " -e '{}'".format(eyes) if eyes else ""

        results = self.process_messages(messages, command)
        output = "\n".join(results)

        out.write(output)

        self.logger.info("Wrote to {}".format(destination))

        return output

    def process_messages(self, messages, command):
        results = []
        for message in messages:
            process = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE)
            try:
                process.stdin.write(message)
                process.stdin.close()

                result = process.stdout.read()
                results.append(result)

                status_code = process.wait()

                if status_code and 0 <= status_code <= 172:
                    raise ValueError("Command exited with status {}".format(status_code))
            except IOError:
                results.append(message)
        return results

    def process_message(self, message, command):
        process = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE)
        try:
            process.stdin.write(message)
            process.stdin.close()

            result = process.stdout.read()
            results.append(result)

            status_code = process.wait()

            if status_code and 0 <= status_code <= 172:
                raise ValueError("Command exited with status {}".format(status_code))
        except IOError:
            results.append(message)
