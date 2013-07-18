## py-mod_zipper -- Apache module written in Python for browsing of Zip files

The goal of this project is to provide an [Apache](http://apache.org/) module
written in [Python](http://python.org), which allows browsing of Zip files through your web browser.

The *py-mod_zipper* module also allows the users to download individual files from a Zip archive, without
having to download and extract the whole Zip archive upfront. 

This makes it very useful for browsing Zip archives and getting only the files you are interested in.

And all that you can do from your web browser!

## Support the project

If you would like to support the project by making a donation, please check the links below. Thank you!

[![Flattr this!](http://api.flattr.com/button/flattr-badge-large.png)](http://flattr.com/thing/1424619/unix-heaven-org-Spread-the-knowledge)

[![Support the py-mod_zipper module](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=dnaeon%2epay%40gmail%2ecom&lc=US&item_name=py-mod_zipper%20Apache%20module&no_note=0&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donate_SM%2egif%3aNonHostedGuest)

## Requirements

*py-mod_zipper* requires that you have *mod_python* installed and loaded by your Apache server.

To install *mod_python* on a Debian GNU/Linux system:

	$ sudo apt-get install libapache2-mod-python
	
## Configuration of py-mod_zipper

Add an Apache vhost and set *py-mod_zipper* as the handler for Zip files.

	<Directory /home/username/public_html> 
		Options +Indexes
		AddHandler mod_python .zip
		PythonHandler /path/to/mod_zipper.py
		PythonDebug Off 
	</Directory>

Restart Apache to apply the configuration changes:

	$ sudo service apache2 restart
	
## Screenshots of py-mod_zipper

You can see example screenshots of *py-mod_zipper* along with more details about it at the link below:

* [http://unix-heaven.org/py-mod_zipper](http://unix-heaven.org/py-mod_zipper)
