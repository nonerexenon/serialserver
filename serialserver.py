#!/usr/bin/env python
#-*- coding: utf-8 -*-
import Serial

from flask import Flask

app = Flask(__name__)

gen = Serial.Serial()

@app.route('/')
def route_index():
	return "Success"

@app.route("/get-serial")
def route_get_serial():
	serial_today = gen.generate()
	return ("Al serial bu: %s" % serial_today)


@app.route("/serial")
def route_serial():
	serial_today = gen.generate()
	return serial_today

if __name__ == '__main__':
	app.run(port=10000)


