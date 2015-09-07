import logging
import os
import shlex
from subprocess import Popen, PIPE


class Cow(object):
    def __init__(self, options={}):
        self.logger = options.get("logger", logging.getLogger(__name__))
        self.status_code = 0

    def say(self, message, options={}):
        command = "cowsay"
        if "strings" in options and "eyes" in options["strings"]:
            command += " -e '{}'".format(options["strings"]["eyes"])

        if isinstance(message, list):
            messages = message
        elif message is None:
            messages = []
        else:
            messages = [message]

        results = []
        for message in messages:
            process = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE)
            try:
                process.stdin.write(message)
                process.stdin.close()

                result = process.stdout.read()
                results.append(result)

                self.status_code = process.wait()
            except OSError:
                pass
        output = "\n".join(results)

        if "out" in options:
            options["out"].write(output)

        if isinstance(options.get("out"), file):
            destination = os.path.abspath(options["out"].name)
        else:
            destination = "return value"
        self.logger.info("Wrote to {}".format(destination))

        if self.status_code < 0 or self.status_code > 172:
            raise ValueError("Command exited with status {}".format(self.status_code))

        return output
