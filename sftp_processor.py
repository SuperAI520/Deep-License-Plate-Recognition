#!/usr/bin/env python
import argparse
import paramiko
import tempfile
import logging
from pathlib import Path
from plate_recognition import recognition_api
import os
import sys
from stat import S_ISDIR, S_ISREG

LOG_LEVEL = os.environ.get('LOGGING', 'INFO').upper()

logging.basicConfig(
    stream=sys.stdout,
    level=LOG_LEVEL,
    style='{',
    format="{asctime} {levelname} {name} {threadName} : {message}",
)

lgr = logging.getLogger(__name__)


def get_connection(hostname, username, port, password=None, pkey_path=None):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if password:
        ssh.connect(hostname, port, username, password)
    else:
        key = paramiko.RSAKey.from_private_key_file(pkey_path)
        ssh.connect(hostname, port, username, pkey=key)

    sftp = ssh.open_sftp()
    return sftp


def main(args):
    """

    :param args: args from argparse
    :return:
    """
    sftp = get_connection(args.host, args.user, args.port, password=args.password, pkey_path=args.pkey)
    root = Path(args.folder)

    for entry in sftp.listdir_attr(str(root)):
        remote_path = root / entry.filename
        mode = entry.st_mode
        if S_ISDIR(mode):
            # Skip Dir
            pass
        elif S_ISREG(mode):
            with tempfile.NamedTemporaryFile(suffix='_' + entry.filename, mode='rb+') as image:
                sftp.getfo(str(remote_path), image)

                api_res = recognition_api(image,
                                          args.regions,
                                          args.api_token,
                                          args.sdk_url,
                                          camera_id=args.camera_id,
                                          mmc=args.mmc,
                                          exit_on_error=False)

                lgr.info(api_res)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Read license plates from the images on an SFTP server and output the result as JSON or CSV.',
        epilog="",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.epilog += "Examples:\n" \
                     "Password login, Process images in /tmp/images: " \
                     "./sftp_processor.py -U usr1  -P pass -H 192.168.100.21 -f /tmp/images -a 4805bee#########\n" \
                     "Private Key login, Process images in /tmp/images: " \
                     "./sftp_processor.py -U usr1  --pkey '/home/danleyb2/.ssh/id_rsa' -H 192.168.100.21 -f /tmp/images -a 4805bee#########\n" \
                     "Password login, Process images in /tmp/images using Snapshot SDK: " \
                     "./sftp_processor.py -U usr1  -P pass -H 192.168.100.21 -f /tmp/images -s http://localhost:8080"

    parser.add_argument('-a', '--api-token', help='Cloud API Token.', required=False)
    parser.add_argument(
        '-r',
        '--regions',
        help='Match the license plate pattern fo specific region',
        required=False,
        action="append")
    parser.add_argument(
        '-s',
        '--sdk-url',
        help="Url to self hosted sdk  For example, http://localhost:8080",
        required=False)
    parser.add_argument('--camera-id',
                        help="Name of the source camera.",
                        required=False)
    parser.add_argument('-H', '--host', help='SFTP host', required=True)
    parser.add_argument('-U', '--user', help='SFTP user', required=True)
    parser.add_argument('-p', '--port', help='SFTP port', required=False, default=22)
    parser.add_argument('-P', '--password', help='SFTP password', required=False)
    parser.add_argument('--pkey', help='SFTP Private Key Path', required=False)

    parser.add_argument('-f',
                        '--folder',
                        help='Specify folder with images on the SFTP server.',
                        default='/')

    parser.add_argument(
        '--mmc',
        action='store_true',
        help='Predict vehicle make and model (SDK only). It has to be enabled.')
    cli_args = parser.parse_args()

    if not cli_args.sdk_url and not cli_args.api_token:
        raise Exception('api-key is required')

    main(cli_args)
