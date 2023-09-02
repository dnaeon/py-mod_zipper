# Copyright (c) 2013-2023 Marin Atanasov Nikolov <dnaeon@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer
#    in this position and unchanged.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR(S) ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR(S) BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
mod_zipper is an Apache module which is being used for browsing of
Zip archives.

It allows you to download individual files from a Zip archive located
on a remote system without the need to download first the archive
locally and extract it.

The mod_zipper module requires your Apache server to have mod_python
loaded already.

"""

__version__ = '0.1.0'

import os
import time
import zipfile
import tempfile
import shutil

from mod_python import util, apache

_layout = """<!DOCTYPE html>
<html>
  <head>
    <title>Zipper :: Zip Web Browser App</title>
    <link rel="stylesheet" href="css/main.css">
  </head>
  <body>
    <header>
      <div class="container">
        <h1 class="logo">Zipper :: Zip Web Browser App</h1>
      </div>
    </header>

    <div class="container">
    <!-- Content goes here --!>
    {content}
    <!-- Content ends here --!>
    </div>
  </body>
</html>
"""

def display_zip_contents(req):
    """
    Opens a Zip archive file and displays it's contents.
    """
    zip_file = None
    try:
        zip_file = zipfile.ZipFile(req.filename, 'r', allowZip64=True)
    except IOError as e:
        raise apache.SERVER_RETURN(apache.HTTP_INTERNAL_SERVER_ERROR)

    req.content_type = 'text/html'
    file_name = os.path.basename(req.filename)

    data = """
        <a href="?fetch=1">Download archive %s</a>
        <h3>Contents of %s</h3>
        <table>
          <tr>
            <th>Filename</th>
            <th>Length</th>
            <th>Size</th>
            <th>Ratio</th>
            <th>Date</th>
            <th>CRC</th>
            <th>Comment<th>
          </tr>""" % (file_name, file_name)

    for item in zip_file.namelist():
        info = zip_file.getinfo(item)
        if info.file_size and info.compress_size:
            ratio = str(round(float(info.compress_size) / float(info.file_size) * 100, 2)) + '%'
        else:
            ratio = '0%'

        data += '''
            <tr>
                <td><a href="{uri}?file={file_name}">{file_name}</a></td>
                <td>{file_size}</td>
                <td>{compress_size}</td>
                <td>{ratio}</td>
                <td>{timestamp}</td>
                <td>{crc}</td>
                <td>{comment}</td>
            </tr>'''.format(
                uri=req.uri,
                file_name=info.filename,
                file_size=info.file_size,
                compress_size=info.compress_size,
                ratio=ratio,
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S', (info.date_time + (0, 0, 0))),
                crc=hex(info.CRC),
                comment=info.comment.decode('utf-8'),
            )

    data += '</table>'
    zip_file.close()
    req.write(_layout.format(content=data))

    return apache.OK


def download_file_from_zip(req, name):
    """
    Extracts a file from a Zip archive and sends it to the client
    """
    zip_file = None
    try:
        zip_file = zipfile.ZipFile(req.filename, 'r', allowZip64=True)
    except IOError as e:
        raise apache.SERVER_RETURN(apache.HTTP_INTERNAL_SERVER_ERROR)

    # Set headers
    req.content_type = 'text/file'
    req.headers_out['Content-Disposition'] = 'attachment; filename={}'.format(os.path.basename(name.value))

    # Temp directory to extract the file
    tmpdir = tempfile.mkdtemp(prefix='mod_zipper-')
    path = zip_file.extract(name.value, path=tmpdir)
    zip_file.close()

    # Send the file and clean up
    send_file(req, path)
    shutil.rmtree(tmpdir, ignore_errors=True)

    return apache.OK


def download_full_archive(req):
    """
    Sends the full Zip archive to the client
    """
    if not os.path.exists(req.filename):
        return apache.DECLINED

    req.content_type = 'text/file'
    req.headers_out['Content-Disposition'] = 'attachment; filename={}'.format(os.path.basename(req.filename))
    send_file(req, req.filename)
    

def send_file(req, path):
    """
    Sends a file to the client
    """
    return req.sendfile(path)


def handler(req):
    """
    The Apache handler for mod_zipper
    """
    form = util.FieldStorage(req, keep_blank_values=1)
    fetch_file = form.getfirst('file')
    fetch_archive = form.getfirst('fetch')

    if fetch_file:
        download_file_from_zip(req, fetch_file)
    elif fetch_archive:
        download_full_archive(req)
    else:
        display_zip_contents(req)

    return apache.OK
