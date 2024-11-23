#!/usr/bin/python3

import argparse
import sys
import time

import zeroconf

from pacontrol import Device


class Listener(zeroconf.ServiceListener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.devices = {}

    def update_service(self, zc: zeroconf.Zeroconf, type_: str, name: str) -> None:
        pass

    def remove_service(self, zc: zeroconf.Zeroconf, type_: str, name: str) -> None:
        del self.devices[name]

    def add_service(self, zc: zeroconf.Zeroconf, type_: str, name: str) -> None:
        service_info = zc.get_service_info(type_, name)
        self.devices[name] = Device(service_info)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list")
    subparsers.add_parser("mute")
    subparsers.add_parser("unmute")
    subparsers.add_parser("sleep")
    subparsers.add_parser("wakeup")

    set_cmd = subparsers.add_parser("set")
    set_cmd.add_argument("--input", choices=["rca", "xlr"])
    set_cmd.add_argument("--voicing", choices=["pure", "unr", "ext"])
    set_cmd.add_argument("--bass", type=int, default=None)
    set_cmd.add_argument("--desk", type=int, default=None)
    set_cmd.add_argument("--presence", type=int, default=None)
    set_cmd.add_argument("--treble", type=int, default=None)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    with zeroconf.Zeroconf() as zc:
        listener = Listener()
        browser = zeroconf.ServiceBrowser(zc, "_oca._udp.local.", listener)

        # lower wait time is usually not enough for devices to show up
        time.sleep(1)

        # making a copy to avoid issues with dictionary changes while iterating
        devices = listener.devices.copy()

        if args.command == "list":
            fmt = "{name:30s} {description:s}"
            print(fmt.format(name="NAME", description="DESCRIPTION"), file=sys.stderr)
            for device in devices.values():
                device.send_keepalive()
                name = device.get_name()
                description = device.get_description()
                print(fmt.format(name=name, description=description))
        elif args.command == "mute":
            for device in devices.values():
                device.send_keepalive()
                device.set_mute(1)
        elif args.command == "unmute":
            for device in devices.values():
                device.send_keepalive()
                device.set_mute(0)
        elif args.command == "sleep":
            for device in devices.values():
                device.send_keepalive()
                device.set_sleep(1)
        elif args.command == "wakeup":
            for device in devices.values():
                device.send_keepalive()
                device.set_sleep(0)
        elif args.command == "set":
            for device in devices.values():
                device.send_keepalive()

                if args.input:
                    mapping = {
                        "rca": 0,
                        "xlr": 1,
                    }
                    device.set_input(mapping[args.input])

                if args.voicing:
                    mapping = {
                        "pure": 0,
                        "unr": 1,
                        "ext": 2,
                    }
                    device.set_voicing(mapping[args.voicing])

                if args.bass is not None:
                    device.set_bass(args.bass)

                if args.desk is not None:
                    device.set_desk(args.desk)

                if args.presence is not None:
                    device.set_presence(args.presence)

                if args.treble is not None:
                    device.set_treble(args.treble)


if __name__ == "__main__":
    main()
