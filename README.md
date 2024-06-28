# pycarwings3

[![CI](https://github.com/ev-freaks/pycarwings3/actions/workflows/main.yml/badge.svg)](https://github.com/ev-freaks/pycarwings3/actions/workflows/main.yml)

## Introduction

`pycarwings3` is a fork of [pycarwings2](https://github.com/filcole/pycarwings2), updated to support asynchronous operations with the Carwings API via aiohttp, focusing on Python 3 compatibility.

The original `pycarwings2` project is no longer active.

## Rationale Behind the New Name

The library underwent significant changes, especially adopting asynchronous programming, which led to a break in backward compatibility with `pycarwings2`.

The new name reflects these changes and aims for easier PyPI distribution.

## Abstract

Library for connecting and interacting with Nissan's CARWINGS service for Nissan LEAF cars.
Uses the (newly secure!) REST/JSON API rather than the previous XML-based API.

## Asynchronous methods

Note that several of the most interesting methods in the CARWINGS service are
asynchronous--you ask the service to do something, and it just says "ok". You then
have to poll a corresponding method to find out if the operation was successful.

Recently the polling has continued to return zero, yet when querying the data
held on the Nissan servers the last update date changes, indicating a response
has been received from the car, see examples/get-leaf-info.py for how this can
be handled.

## Installation

    pip3 install pycarwings3

## Example usage

* Copy file ./examples/config.ini to ./examples/my_config.ini
* Edit my_config.ini and enter your username, password and region
* Run python3 ./examples/get-leaf-info.py

## License

Copyright 2016 Jason Horne
Copyright 2018 Phil Cole
Copyright 2024 Remus Lazar

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
