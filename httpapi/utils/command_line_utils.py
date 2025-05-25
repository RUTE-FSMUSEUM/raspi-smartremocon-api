# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

import argparse
from awscrt import io
from uuid import uuid4

class CommandLineUtils:
    def __init__(self, description) -> None:
        self.parser = argparse.ArgumentParser(description="Send and receive messages through and MQTT connection.")
        self.commands = {}
        self.parsed_commands = None

    def register_command(self, command_name, example_input, help_output, required=False, type=None, default=None, choices=None, action=None):
        self.commands[command_name] = {
            "name":command_name,
            "example_input":example_input,
            "help_output":help_output,
            "required": required,
            "type": type,
            "default": default,
            "choices": choices,
            "action": action
        }

    def remove_command(self, command_name):
        if command_name in self.commands.keys():
            self.commands.pop(command_name)

    """
    Returns the command if it exists and has been passed to the console, otherwise it will print the help for the sample and exit the application.
    """
    def get_command_required(self, command_name, command_name_alt = None):
        if(command_name_alt != None):
            if hasattr(self.parsed_commands, command_name_alt):
                if(getattr(self.parsed_commands, command_name_alt) != None):
                    return getattr(self.parsed_commands, command_name_alt)

        if hasattr(self.parsed_commands, command_name):
            if(getattr(self.parsed_commands, command_name) != None):
                return getattr(self.parsed_commands, command_name)

        self.parser.print_help()
        print("Command --" + command_name + " required.")
        exit()

    """
    Returns the command if it exists, has been passed to the console, and is not None. Otherwise it returns whatever is passed as the default.
    """
    def get_command(self, command_name, default=None):
        if hasattr(self.parsed_commands, command_name):
            result = getattr(self.parsed_commands, command_name)
            if (result != None):
                return result
        return default

    def get_args(self):
        # if we have already parsed, then return the cached parsed commands
        if self.parsed_commands is not None:
            return self.parsed_commands

        # add all the commands
        for command in self.commands.values():
            if not command["action"] is None:
                self.parser.add_argument("--" + command["name"], action=command["action"], help=command["help_output"],
                    required=command["required"], default=command["default"])
            else:
                self.parser.add_argument("--" + command["name"], metavar=command["example_input"], help=command["help_output"],
                    required=command["required"], type=command["type"], default=command["default"], choices=command["choices"])

        self.parsed_commands = self.parser.parse_args()
        # Automatically start logging if it is set
        if self.parsed_commands.verbosity:
            io.init_logging(getattr(io.LogLevel, self.parsed_commands.verbosity), 'stderr')

        return self.parsed_commands
    
    def add_common_mqtt_commands(self):
        self.register_command(
            CommandLineUtils.m_cmd_endpoint,
            "<str>",
            "The endpoint of the mqtt server not including a port.",
            False,
            str)
        self.register_command(
            CommandLineUtils.m_cmd_ca_file,
            "<path>",
            "Path to AmazonRootCA1.pem (optional, system trust store used by default)",
            False,
            str)
        self.register_command(
            CommandLineUtils.m_cmd_is_ci,
            "<str>",
            "If present the sample will run in CI mode (optional, default='None')",
            False,
            str)
        
    def add_common_proxy_commands(self):
        self.register_command(
            CommandLineUtils.m_cmd_proxy_host,
            "<str>",
            "Host name of the proxy server to connect through (optional)",
            False,
            str)
        self.register_command(
            CommandLineUtils.m_cmd_proxy_port,
            "<int>",
            "Port of the http proxy to use (optional, default='8080')",
            type=int,
            default=8080)

    def add_common_topic_message_commands(self):
        self.register_command(
            CommandLineUtils.m_cmd_topic,
            "<str>",
            "Topic to publish, subscribe to (optional, default='test/topic').",
            default="test/topic")
        self.register_command(
            CommandLineUtils.m_cmd_message,
            "<str>",
            "The message to send in the payload (optional, default='Hello World!').",
            default="Hello World! ")

    def add_common_logging_commands(self):
        self.register_command(
            CommandLineUtils.m_cmd_verbosity,
            "<Log Level>",
            "Logging level.",
            default=io.LogLevel.NoLogs.name,
            choices=[
                x.name for x in io.LogLevel])

    def add_common_key_cert_commands(self):
        self.register_command(CommandLineUtils.m_cmd_key_file, "<path>", "Path to your key in PEM format.", False, str)
        self.register_command(CommandLineUtils.m_cmd_cert_file, "<path>", "Path to your client certificate in PEM format.", False, str)


    ########################################################################
    # cmdData utils/functions
    ########################################################################

    class CmdData:
        # General use
        input_endpoint : str
        input_cert : str
        input_key : str
        input_ca : str
        input_clientId : str
        input_port : int
        input_is_ci : bool
        input_use_websockets : bool
        # Proxy
        input_proxy_host : str
        input_proxy_port : int
        # PubSub
        input_topic : str

        def __init__(self) -> None:
            pass

        def parse_input_topic(self, cmdUtils, config):
            self.input_topic = cmdUtils.get_command(CommandLineUtils.m_cmd_topic, config["AWSIOT"]["TOPIC"])
            if (cmdUtils.get_command(CommandLineUtils.m_cmd_is_ci) != None):
                self.input_topic += "/" + str(uuid4())


    def parse_sample_input_pubsub(config: dict):
        cmdUtils = CommandLineUtils("PubSub - Send and receive messages through an MQTT connection.")
        cmdUtils.add_common_mqtt_commands()
        cmdUtils.add_common_topic_message_commands()
        cmdUtils.add_common_proxy_commands()
        cmdUtils.add_common_logging_commands()
        cmdUtils.add_common_key_cert_commands()
        cmdUtils.register_command(CommandLineUtils.m_cmd_port, "<int>", "Connection port. AWS IoT supports 443 and 8883 (optional, default=8883).", type=int)
        cmdUtils.register_command(CommandLineUtils.m_cmd_client_id, "<str>", "Client ID to use for MQTT connection (optional, default='test-*').", default="test-" + str(uuid4()))
        cmdUtils.register_command(CommandLineUtils.m_cmd_count, "<int>", "The number of messages to send (optional, default='0').", default=0, type=int)
        cmdUtils.get_args()

        cmdData = CommandLineUtils.CmdData()
        cmdData.input_endpoint = cmdUtils.get_command(CommandLineUtils.m_cmd_endpoint, config["AWSIOT"]["ENDPOINT"])
        cmdData.input_port = int(cmdUtils.get_command(CommandLineUtils.m_cmd_port, 8883))
        cmdData.input_cert = cmdUtils.get_command(CommandLineUtils.m_cmd_cert_file, config["AWSIOT"]["CERT"])
        cmdData.input_key = cmdUtils.get_command(CommandLineUtils.m_cmd_key_file, config["AWSIOT"]["PRIKEY"])
        cmdData.input_ca = cmdUtils.get_command(CommandLineUtils.m_cmd_ca_file, config["AWSIOT"]["ROOTCA"])
        cmdData.input_clientId = cmdUtils.get_command(CommandLineUtils.m_cmd_client_id, "test-" + str(uuid4()))
        cmdData.input_proxy_host = cmdUtils.get_command(CommandLineUtils.m_cmd_proxy_host)
        cmdData.input_proxy_port = int(cmdUtils.get_command(CommandLineUtils.m_cmd_proxy_port))
        cmdData.parse_input_topic(cmdUtils, config)
        cmdData.input_is_ci = cmdUtils.get_command(CommandLineUtils.m_cmd_is_ci, None) != None
        return cmdData
    

    # Constants for commonly used/needed commands
    m_cmd_endpoint = "endpoint"
    m_cmd_ca_file = "ca_file"
    m_cmd_cert_file = "cert"
    m_cmd_key_file = "key"
    m_cmd_proxy_host = "proxy_host"
    m_cmd_proxy_port = "proxy_port"
    m_cmd_topic = "topic"
    m_cmd_verbosity = "verbosity"
    m_cmd_port = "port"
    m_cmd_client_id = "client_id"
    m_cmd_is_ci = "is_ci"
