import logging
import os
import shlex
from subprocess import Popen, PIPE


class Cow:
    def __init__(self, options={}):
        self.logger = options.get("logger", logging.getLogger(__name__))
        self.last_status_code = None

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

                self.last_status_code = process.wait()
            except IOError:
                results.append(message)
        output = "\n".join(results)

        if isinstance(options.get("out"), file):
            options["out"].write(output)

        if isinstance(options.get("out"), file):
            destination = os.path.abspath(options["out"].name)
        else:
            destination = "return value"
        self.logger.info("Wrote to {}".format(destination))

        if self.last_status_code and 0 <= self.last_status_code <= 172:
            raise ValueError("Command exited with status {}".format(self.last_status_code))

        return output
