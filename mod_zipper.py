#
# Copyright (c) 2013-2014 Marin Atanasov Nikolov <dnaeon@gmail.com>
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
#

"""
mod_zipper is an Apache module which is being used for browsing Zip files from your browser.

It allows you to download individual files from a Zip archive located on a remote system without the
need to download first the archive locally and extract it. 

The mod_zipper module requires your Apache server to have mod_python loaded already.

"""

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
    %s
    <!-- Content ends here --!>
    </div>
  </body>
</html>
"""

def get_zip_contents(req):
    """
    Opens a Zip archive file and displays it's contents.
    
    """
    try:
        myFile = zipfile.ZipFile(req.filename, 'r', allowZip64=True)
    except IOError as e:
        return 'Failed to open file %s: %s' % (req.filename, e)
    
    req.content_type = 'text/html'
    req.send_http_header()

    archive_file = os.path.basename(req.filename)
    
    data = """
	<a href="?download-archive=1">Download archive %s</a>
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
	  </tr>""" % (archive_file, archive_file)

    for eachMember in myFile.namelist():
        info = myFile.getinfo(eachMember)

        if info.file_size and info.compress_size:
            ratio = str(round(float(info.compress_size) / float(info.file_size) * 100, 2)) + '%'
        else:
            ratio = '0%'

        data += """
	    <tr>
		<td><a href="%s?download-file=%s">%s</a></td>
        	<td>%s</td>
        	<td>%s</td>
            	<td>%s</td>
 		<td>%s</td>
		<td>%s</td>
		<td>%s</td>
            </tr>""" % (req.uri, info.filename, info.filename,
                        info.file_size,
                        info.compress_size,
                        ratio,
                        time.strftime('%Y-%m-%d %H:%M:%S', (info.date_time + (0, 0, 0))),
                        hex(info.CRC),
                        info.comment)
            
    data += '</table>'
    myFile.close()
    req.write(_layout % data)
    
    return apache.OK

def download_file(req, name):
    """
    Extracts a file from a Zip archive and transmits it to the user.

    """
    try:
        myFile = zipfile.ZipFile(req.filename, 'r', allowZip64=True)
    except IOError as e:
        return 'Failed to open file %s: %s' % (req.filename, e)

    # Send headers
    req.content_type = 'text/file'
    req.headers_out['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(name)
    req.send_http_header()

    # Temp directory to extract the file
    tmpdir = tempfile.mkdtemp(dir='/tmp')
    
    # Extract file from the archive
    path = myFile.extract(name, path=tmpdir)
    myFile.close()

    # Send the file
    send_file(req, path)
    
    # Clean up a bit here
    shutil.rmtree(tmpdir)

    return apache.OK

def download_archive(req):
    """
    Sends the whole Zip archive to the client

    """
    if not os.path.exists(req.filename):
        return 'File %s does not exists' % req.filename
    
    # Send headers
    req.content_type = 'text/file'
    req.headers_out['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(req.filename)
    req.send_http_header()

    send_file(req, req.filename)
    
def send_file(req, path, chunksize=1024):
    """
    Sends a file to the client

    """
    offset   = 0
    length   = 0
    filesize = os.stat(path)[6]

    while filesize > 0:
        if chunksize > filesize:
            length += filesize
        else:
            length += chunksize

        sent = req.sendfile(path, offset, length)

        offset += sent
        filesize -= sent

def handler(req):
    """
    Apache handler for handling user requests.

    """
    form = util.FieldStorage(req, keep_blank_values=1)

    file_value    = form.getfirst('download-file')
    archive_value = form.getfirst('download-archive')
    
    if file_value:
        download_file(req, file_value)
    elif archive_value:
        download_archive(req)
    else:
        get_zip_contents(req)

    return apache.OK

