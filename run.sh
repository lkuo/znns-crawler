#!/bin/bash

scrapy crawl --logfile "./logs/$(date '+%Y-%m-%d_%H-%M-%S').logs" models && shutdown -P +3
