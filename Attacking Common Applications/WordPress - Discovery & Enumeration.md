WordPress is written in PHP and usually runs on Apache with MySQL as the backend.

## Discovery/Footprinting

A quick way to identify a WordPress site is by browsing to the `/robots.txt` file. A typical robots.txt on a WordPress installation may look like:

```
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php
Disallow: /wp-content/uploads/wpforms/

Sitemap: https://inlanefreight.local/wp-sitemap.xml
```

WordPress stores its plugins in the `wp-content/plugins` directory. This folder is helpful to enumerate vulnerable plugins. Themes are stored in the `wp-content/themes` directory. These files should be carefully enumerated as they may lead to RCE.

There are five types of users on a standard WordPress installation.

1. Administrator: This user has access to administrative features within the website. This includes adding and deleting users and posts, as well as editing source code.
2. Editor: An editor can publish and manage posts, including the posts of other users.
3. Author: They can publish and manage their own posts.
4. Contributor: These users can write and manage their own posts but cannot publish them.
5. Subscriber: These are standard users who can browse posts and edit their profiles.
## Enumeration

Another quick way to identify a WordPress site is by looking at the page source. Viewing the page with `cURL` and grepping for `WordPress` can help us confirm that WordPress is in use and footprint the version number, which we should note down for later. We can enumerate WordPress using a variety of manual and automated tactics.

```
tylapcheong@htb[/htb]$ curl -s http://blog.inlanefreight.local | grep WordPress

<meta name="generator" content="WordPress 5.8" /
```


Browsing the site and perusing the page source will give us hints to the theme in use, plugins installed, and even usernames if author names are published with posts. We should spend some time manually browsing the site and looking through the page source for each page, grepping for the `wp-content` directory, `themes` and `plugin`, and begin building a list of interesting data points.

Looking at the page source, we can see that the [Business Gravity](https://wordpress.org/themes/business-gravity/) theme is in use. We can go further and attempt to fingerprint the theme version number and look for any known vulnerabilities that affect it.

```
tylapcheong@htb[/htb]$ curl -s http://blog.inlanefreight.local/ | grep themes 

<link rel='stylesheet' id='bootstrap-css'  href='http://blog.inlanefreight.local/wp-content/themes/business-gravity/assets/vendors/bootstrap/css/bootstrap.min.css' type='text/css' media='all' />

```

Next, let's take a look at which plugins we can uncover.
`tylapcheong@htb[/htb]$ curl -s http://blog.inlanefreight.local/ | grep plugins`

From the output, we know that the [Contact Form 7](https://wordpress.org/plugins/contact-form-7/) and [mail-masta](https://wordpress.org/plugins/mail-masta/) plugins are installed. The next step would be enumerating the versions.

Browsing to `http://blog.inlanefreight.local/wp-content/plugins/mail-masta/` shows us that directory listing is enabled and that a `readme.txt` file is present. These files are very often helpful in fingerprinting version numbers.

```
tylapcheong@htb[/htb]$ curl -s http://blog.inlanefreight.local/?p=1 | grep plugins
```

A quick search for this plugin version shows [this](https://www.exploit-db.com/exploits/49967) unauthenticated remote code execution vulnerability from June of 2021. We'll note this down and move on. It is important at this stage to not jump ahead of ourselves and start exploiting the first possible flaw we see, as there are many other potential vulnerabilities and misconfigurations possible in WordPress that we don't want to miss.

## Enumerating Users

We can do some manual enumeration of users as well. As mentioned earlier, the default WordPress login page can be found at `/wp-login.php`.

Entering 'admin' in the username input.
`Error: The password you entered for the username admin is incorrect`

However, an invalid username returns that the user was not found.
`Error: The username someone is not registered on this site. If you are unsure of your username, try your email address instead`

This makes WordPress vulnerable to username enumeration, which can be used to obtain a list of potential usernames.

Let's recap. At this stage, we have gathered the following data points:

- The site appears to be running WordPress core version 5.8
- The installed theme is Business Gravity
- The following plugins are in use: Contact Form 7, mail-masta, wpDiscuz
- The wpDiscuz version appears to be 7.0.4, which suffers from an unauthenticated remote code execution vulnerability
- The mail-masta version seems to be 1.0.0, which suffers from a Local File Inclusion vulnerability
- The WordPress site is vulnerable to user enumeration, and the user `admin` is confirmed to be a valid user



Let's take things a step further and validate/add to some of our data points with some automated enumeration scans of the WordPress site. Once we complete this, we should have enough information in hand to begin planning and mounting our attacks.

---

## WPScan

[WPScan](https://github.com/wpscanteam/wpscan) is an automated WordPress scanner and enumeration tool. It determines if the various themes and plugins used by a blog are outdated or vulnerable. It’s installed by default on Parrot OS but can also be installed manually with `gem`.

`tylapcheong@htb[/htb]$ sudo gem install wpscan`

WPScan is also able to pull in vulnerability information from external sources. We can obtain an API token from [WPVulnDB](https://wpvulndb.com/), which is used by WPScan to scan for PoC and reports.

The `--enumerate` flag is used to enumerate various components of the WordPress application, such as plugins, themes, and users. By default, WPScan enumerates vulnerable plugins, themes, users, media, and backups.

Let’s invoke a normal enumeration scan against a WordPress website with the `--enumerate` flag and pass it an API token from WPVulnDB with the `--api-token` flag.

`tylapcheong@htb[/htb]$ sudo wpscan --url http://blog.inlanefreight.local --enumerate --api-token dEOFB<SNIP>`

WPScan uses various passive and active methods to determine versions and vulnerabilities, as shown in the report above. The default number of threads used is `5`. However, this value can be changed using the `-t` flag.

This scan helped us confirm some of the things we uncovered from manual enumeration (WordPress core version 5.8 and directory listing enabled), showed us that the theme that we identified was not exactly correct (Transport Gravity is in use which is a child theme of Business Gravity), uncovered another username (john), and showed that automated enumeration on its own is often not enough (missed the wpDiscuz and Contact Form 7 plugins). WPScan provides information about known vulnerabilities. The report output also contains URLs to PoCs, which would allow us to exploit these vulnerabilities.