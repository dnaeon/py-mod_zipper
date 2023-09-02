## py-mod_zipper

`py-mod_zipper` is an Apache module, which allow you to browse and
extract specific files from Zip archives.

## Requirements

- Python 3.x
- [mod_python](https://github.com/grisha/mod_python)
- Apache 2.x

## Installation

Install the package.

``` shell
pip install .
```

## Configuration

Create an Apache vhost and configure `py-mod_zipper`.

``` apacheconf
Alias "/css" "/path/to/py-mod_zipper/css"
<Directory "/path/to/py-mod_zipper/css">
	Require all granted
</Directory>

<Directory /home/username/public_html> 
	Options +Indexes
	AddHandler mod_python .zip
	PythonHandler mod_zipper
	PythonDebug Off 
</Directory>
```

Make sure to reload the Apache service.

## Docker

Build a Docker image.

``` shell
docker build -t mod_zipper:latest .
```

Then run the container with a directory containing zip archives.

``` shell
docker run --rm -p 8080:80 -v /path/to/zip/files:/usr/local/apache2/htdocs mod_zipper:latest
```

Open your browser at http://localhost:8080/

## License

`py-mod_zipper` is Open Source and licensed under the [BSD
License](http://opensource.org/licenses/BSD-2-Clause).
