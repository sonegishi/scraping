# Scrape DePauw Courses

Scraping DePauw's schedule of courses (https://my.depauw.edu/e/reg/soc-view/).

## Getting Started

### Chromedriver

Install a chromedriver if you don't have one.

#### Download Chromedriver

Download an appropriate chromedriver zip from [here](https://sites.google.com/a/chromium.org/chromedriver/home).

Assuming you are using macOS, download the one named `chromedriver_mac64.zip`.

#### Unzip the zip file downloaded

```shell
cd ~/Downloads
unzip chromedriver_mac64.zip
```

#### Give an appropriate permission
e
```shell
chmod +x chromedriver
```

### Installation

```shell
pip install poetry

poetry install

poetry shell
```

## Contributors

- So Negishi ([@sonegishi](https://github.com/sonegishi/))
