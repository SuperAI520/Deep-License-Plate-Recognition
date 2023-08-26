import argparse
import datetime

import requests
from bs4 import BeautifulSoup


def parse_arguments():
    parser = argparse.ArgumentParser(description='Measure ParkPow load time.')
    parser.add_argument(
        "--url",
        help='The base URL of the ParkPow website. Defaults to localhost.',
        default="http://127.0.0.1:8000",
    )
    parser.add_argument(
        "--email",
        help='The email address to be used for login',
        default="test1@gmail.com",
    )
    parser.add_argument(
        "--password",
        help="The corresponding password for the provided email.",
        default="bt5Nt13llta^",
    )
    return parser.parse_args()


def login(session, url, email, password):
    LOGIN_URL = f"{url}/accounts/login/"

    res1 = session.get(LOGIN_URL)
    csrf_token = res1.cookies["csrftoken"]
    res2 = session.post(LOGIN_URL, data={"login": email, "password": password, "csrfmiddlewaretoken": csrf_token})
    return "dashboard" in res2.url


def _get_load_time_or_none(res):
    if res.status_code == 200:
        return res.elapsed.microseconds / 1000
    else:
        return None


def scrape_first_plate(session,url):
    _url = f"{url}/dashboard/"
    res = session.get(_url)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, "html.parser")
        td = soup.find("td", class_="license_plate")
        if td:
            return td.a.string.strip()
    return False


def scrape_first_camera(session, url):
    _url = f"{url}/dashboard/"
    res = session.get(_url)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, "html.parser")
        return soup.find("select", {"name": "camera"}).option.attrs["value"]

def get_load_time(session, url, page="dashboard", days=1):
    url = f"{url}/{page}/"

    time_delta = datetime.timedelta(days=days)
    dt_from = datetime.datetime.now() - time_delta

    res = session.get(url, params={"from": dt_from})

    return _get_load_time_or_none(res)


def get_load_time_search_plate(session, url, plate, page="dashboard", days=1):
    url = f"{url}/{page}/"
    time_delta = datetime.timedelta(days=days)

    dt_from = datetime.datetime.now() - time_delta
    res = session.get(url, params={"from": dt_from, "plate": plate})

    return _get_load_time_or_none(res)


def get_load_time_filter_by_camera(session, url, camera_id, page="dashboard", days=1):
    url = f"{url}/{page}/"
    time_delta = datetime.timedelta(days=days)

    dt_from = datetime.datetime.now() - time_delta
    res = session.get(url, params={"from": dt_from, "camera": camera_id})

    return _get_load_time_or_none(res)


def loop_operation(operation):
    for day in [1, 7, 14, 30, 60]:
        load_time = operation(day)
        load_time_str = f"{load_time}ms" if load_time else "failed to load"
        print(f"{load_time_str}")


def get_result(session, url, page, plate, camera):
    for day in [1, 7, 14, 30, 60]:
        load_time = get_load_time(session, url, page, day)
        load_time_plate = get_load_time_search_plate(session, url, plate, page, day)
        load_time_camera = get_load_time_filter_by_camera(session, url, camera, page, day)

        load_time_str = f"{load_time}ms" if load_time else "failed to load"
        load_time_plate_str = f"{load_time_plate}ms" if load_time_plate else "failed to load"
        load_time_camera_str = f"{load_time_camera}ms" if load_time_camera else "failed to load"

        yield dict(
            day=day,
            no_filter=load_time_str,
            filter_plate=load_time_plate_str,
            filter_camera=load_time_camera_str,
        )


def print_table(title, results):
    if not results:
        return
    print("| -------------------------------------------------------------------- |")
    print(f"|{title.center(70)}|")
    print("| -------------------------------------------------------------------- |")
    print("|   Range   | Without filter  | License plate search | Filter 1 camera |")
    print("| --------- | --------------- | -------------------- | --------------- |")
    for result in results:
        print("| {day:2n} day(s) | {no_filter:^15s} | {filter_plate:^20s} | {filter_camera:^15s} |"
              .format(**result))
    print("| -------------------------------------------------------------------- |")


def main():
    session = requests.session()
    args = parse_arguments()

    # Login
    print("Logging in...")
    if not login(session, args.url, args.email, args.password):
        print("Login failed. Exiting...")
        return

    print()

    plate = scrape_first_plate(session, args.url)
    camera = scrape_first_camera(session, args.url)

    if not plate:
        print("Failed to get a plate to search")
        return

    if not camera:
        print("Failed to get a camera for filtering")
        return

    # Dashboard
    results = get_result(session, args.url, "dashboard", plate, camera)
    print_table("Dashboard", results)

    print()
    print()

    # Alert
    results = get_result(session, args.url, "alerts", plate, camera)
    print_table("Alert", results)


if __name__ == "__main__":
    main()
