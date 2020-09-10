import os
import platform
import subprocess
import webbrowser
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

try:
    from urllib.request import Request, urlopen
    from urllib.error import URLError
except ImportError:
    from urllib2 import Request, urlopen  # type: ignore
    from urllib2 import URLError  # type: ignore

DOCKER_URL = 'https://docs.docker.com/install/'
PLAN_LINK = 'https://app.platerecognizer.com/accounts/plan/?utm_source=installer&utm_medium=app'
IMAGE = 'platerecognizer/alpr-stream'
NONE = {'display': 'none'}
BLOCK = {'display': 'block'}
FLEX = {'display': 'flex'}
BASE_CONFIG = """
# Instructions:
# https://docs.google.com/document/d/1vLwyx4gQvv3gF_kQUvB5sLHoY0IlxV5b3gYUqR2wN1U/edit

# List of TZ names on https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
timezone = UTC

[cameras]
  # Full list of regions: http://docs.platerecognizer.com/#countries
  # regions = fr, gb

  # Sample 1 out of X frames. A high number will result in less compute.
  # A low number is preferred for a stream with fast moving vehicles
  # sample = 2

  # Maximum delay in seconds before a prediction is returned
  # max_prediction_delay = 6

  # Maximum time in seconds that a result stays in memory
  # memory_decay = 300

  # Enable make, model and color prediction. Your account must have that option.
  # mmc = true

  image_format = $(camera)_screenshots/%y-%m-%d/%H-%M-%S.%f.jpg

  [[camera-1]]
    active = yes
    url = rtsp://192.168.0.108:8080/video/h264
    name = Camera One

    # Output methods. Uncomment line to enable.
    # - Save to CSV. The corresponding frame is stored as an image in the same directory.
    # - Send to Webhook. The recognition data and vehicle image are encoded in
    # multipart/form-data and sent to webhook_target.
    csv_file = camera-1.csv
    # webhook_target = http://webhook.site/
    # webhook_image = yes
"""


def get_os():
    os_system = platform.system()
    if os_system == 'Windows':
        return 'Windows'
    elif os_system == 'Linux':
        return 'Linux'
    elif os_system == 'Darwin':
        return 'Mac OS'
    return os_system


def verify_docker_install():
    try:
        subprocess.check_output("docker info".split())
        return True
    except (OSError, subprocess.CalledProcessError) as e:
        print(e)
        return False


def get_container_id(image):
    cmd = 'docker ps -q --filter ancestor={}'.format(image)
    output = subprocess.check_output(cmd.split())
    return output.decode()


def stop_container(image):
    container_id = get_container_id(image)
    if container_id:
        cmd = 'docker stop {}'.format(container_id)
        os.system(cmd)
    return container_id


def get_image(image):
    images = subprocess.check_output(
        ['docker', 'images', '--format', '"{{.Repository}}"',
         image]).decode().split('\n')
    return images[0].replace('"', '')


def pull_docker(image=IMAGE):
    if get_container_id(image):
        stop_container(image)
    pull_cmd = f'docker pull {image}:latest'
    os.system(pull_cmd)


def read_config(home):
    try:
        config = Path.joinpath(Path(home), 'config.ini')
        conf = ''
        f = open(config, 'r')
        for line in f:
            conf += line
        f.close()
        return conf
    except IOError:  # file not found
        return BASE_CONFIG


def write_config(home, config):
    try:
        path = Path.joinpath(Path(home), 'config.ini')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w+') as conf:
            for line in config:
                conf.write(line)
        return True
    except Exception:
        return False


def verify_token(token, license_key, get_license=True):
    try:
        req = Request(
            'https://app.platerecognizer.com/v1/stream/license/{}/'.format(
                license_key))
        req.add_header('Authorization', 'Token {}'.format(token))
        urlopen(req).read()
        return True, None
    except URLError as e:
        if '404' in str(e) and get_license:
            return False, 'License Key is incorrect!!'
        elif str(403) in str(e):
            return False, 'Api Token is incorrect!!'
        else:
            return True, None


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SKETCHY])

app.layout = dbc.Container(children=[
    html.H1(children='Plate Recognizer Installer'),
    dbc.Form(children=[
        dbc.FormGroup([
            dbc.Label(get_os(), id='input-os', width=2),
            dbc.Label('Host OS', html_for='input-os', width=10),
        ],
                      row=True),
        dbc.FormGroup([
            dbc.Col(dbc.Button(
                'Refresh', color='secondary', id='refresh-docker'),
                    width=2),
            dcc.Loading(type="circle", children=html.Div(id="loading-refresh")),
            dbc.Label([
                "Docker is not installed, Follow ",
                html.A(DOCKER_URL, href=DOCKER_URL, target='_blank'),
                " to install docker for your machine."
            ],
                      html_for='refresh-docker',
                      width=10),
        ],
                      row=True,
                      style=NONE,
                      id='refresh'),
        dbc.FormGroup([
            dbc.Col([
                dbc.Button('Update', color='secondary', id='update-image'),
                html.Span(
                    ' Updated', id='span-update', className='align-middle'),
            ],
                    width=2),
            dcc.Loading(type="circle", children=html.Div(id="loading-update")),
            dbc.Label('Docker image found on your system, you may update it.',
                      html_for='update-image',
                      width=10),
        ],
                      row=True,
                      style=NONE,
                      id='update'),
    ]),
    dbc.Form(children=[
        dbc.FormGroup([
            dbc.Col(
                dbc.Input(type='text', id='input-token', placeholder='Token'),
                width=2,
            ),
            dbc.Label([
                'Please enter your Plate Recognizer API Token. Go ',
                html.A('here', href=PLAN_LINK, target='_blank'), ' to get it.'
            ],
                      html_for='input-token',
                      width=10),
        ],
                      row=True),
        dbc.FormGroup([
            dbc.Col(
                dbc.Input(
                    type='text', id='input-key', placeholder='License Key'),
                width=2,
            ),
            dbc.Label([
                'Please enter the Stream License Key. Go ',
                html.A('here', href=PLAN_LINK, target='_blank'), ' to get it.'
            ],
                      html_for='input-key',
                      width=10),
        ],
                      row=True),
        dbc.FormGroup([
            dbc.Col(
                dbc.Input(value=str(Path.joinpath(Path.home(), 'stream')),
                          type='text',
                          id='input-home',
                          placeholder='Path to directory'),
                width=2,
            ),
            dbc.Label('Path to directory of your Stream installation',
                      html_for='input-home',
                      width=10),
        ],
                      className='mb-2',
                      row=True),
        dbc.FormGroup([
            dbc.Label([
                dbc.Checkbox(id="check-boot", className="form-check-input"),
                'Do you want Stream to automatically boot on system startup?'
            ],
                      html_for="check-boot",
                      className='pl-0',
                      width=12),
        ],
                      check=True,
                      className='mb-1'),
    ],
             style=NONE,
             id='form'),
    html.Div(children=[
        html.P('Stream config:'),
        dbc.Textarea(bs_size='sm',
                     id='area-config',
                     style={
                         'width': '70%',
                         'height': '300px'
                     }),
        html.P(children='', style={'color': 'red'}, id='p-status'),
        html.Code(id='command'),
        dcc.Loading(type="circle", children=html.Div(id="loading-submit")),
        dbc.Button(
            'Submit', color='primary', id='button-submit', className='mt-2'),
    ],
             id='footer',
             style=NONE)
])


@app.callback([
    Output('refresh', 'style'),
    Output('update', 'style'),
    Output('form', 'style'),
    Output('footer', 'style'),
    Output('loading-refresh', 'children')
], [Input('refresh-docker', 'n_clicks')])
def update_docker(n_clicks):
    if verify_docker_install():
        if get_image(IMAGE):
            return NONE, FLEX, BLOCK, BLOCK, None
        else:
            return NONE, NONE, BLOCK, BLOCK, None
    else:
        return FLEX, NONE, NONE, NONE, None


@app.callback([
    Output('update-image', 'disabled'),
    Output('span-update', 'style'),
    Output('loading-update', 'children')
], [Input('update-image', 'n_clicks')])
def update_image(n_clicks):
    if n_clicks:
        pull_docker()
        return True, {'display': 'inline', 'color': 'green'}, None
    return False, NONE, None


@app.callback(Output('area-config', 'value'), [Input('input-home', 'value')])
def change_path(home):
    return read_config(home)


@app.callback([
    Output('p-status', 'children'),
    Output('command', 'children'),
    Output('loading-submit', 'children')
], [
    Input('button-submit', 'n_clicks'),
    State('input-token', 'value'),
    State('input-key', 'value'),
    State('input-home', 'value'),
    State('check-boot', 'checked'),
    State('area-config', 'value')
])
def submit(n_clicks, token, key, home, boot, config):
    if n_clicks:
        is_valid, error = verify_token(token, key)
        if is_valid:
            if not write_config(home, config):
                return "Cannot use selected directory. Please choose another one.", '', None
            command = 'docker run --rm -t ' \
                      '--name stream ' \
                      f'-v {home}:/user-data ' \
                      '--user `id -u`:`id -g` ' \
                      f'-e LICENSE_KEY={key} ' \
                      f'-e TOKEN={token} ' \
                      f'{IMAGE}'
            if get_os() != 'Windows':
                command = command.replace('-v', '--user `id -u`:`id -g` -v')
            if os.path.exists('/etc/nv_tegra_release'):
                command = command.replace(
                    '-t', '--runtime nvidia --privileged --group-add video -t')
                command += ':jetson'
            if boot:
                command = command.replace('--rm', '--restart unless-stopped')
            if not get_image(IMAGE):
                pull_docker()
            message = 'You can now start Stream. Open a terminal and type the command below. You can save this command for future use.'
            return message, command, None
        else:
            return error, '', None
    else:
        return '', '', None


if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/')
    app.run_server(debug=False)
