# UConnect Bench Test app

This project lets you fire up a test bench for PowerNet-based UConnect systems.

## Hardware

- USB CAN interface - I used [this one (no affiliation)](https://www.amazon.com/dp/B0G6KHBGCJ)

## Usage

Make sure you have Python3 installed. Clone this repo, and create a virtual environment.

The first time only, run:
```shell
 python -m venv .venv
 source ./venv/Scripts/activate
 pip install -r requirements.xt
```

Subsiquent runs, just run:
```shell
source ./venv/Scripts/activate
```

Modify the `uconnect-bench-test.py` file to specify your COM port and simulated VIN. Then, just run:
```shell
python ./uconnect-bench-test.py
```
