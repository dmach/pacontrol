# About

PAControl is an alternative to Adam Audio's A Control.
It is a command-line tool and a python library.


# Usage

## List devices
`./pacontrol-cli.py list`

## Mute all available devices
`./pacontrol-cli.py mute`

## Unmute all available devices
`./pacontrol-cli.py unmute`

## Sleep all available devices
`./pacontrol-cli.py sleep`

## Wake all available devices up
`./pacontrol-cli.py wakeup`

## Set all available devices according to given parameters:
```
./pacontrol-cli.py set \
  --input=rca|xlr \
  --voicing=pure|unr|ext \
  --bass=-2|-1|0|1 \
  --desk=-2|-1|0 \
  --presence=-1|0|1 \
  --treble=-1|0|1
```
