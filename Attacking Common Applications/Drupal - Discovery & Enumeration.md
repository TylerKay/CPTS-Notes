[Drupal](https://www.drupal.org/), launched in 2001 is the third and final CMS we'll cover on our tour through the world of common applications. Drupal is another open-source CMS that is popular among companies and developers. Drupal is written in PHP and supports using MySQL or PostgreSQL for the backend. Additionally, SQLite can be used if there's no DBMS installed.

## Discovery/Footprinting

During an external penetration test, we encounter what appears to be a CMS, but we know from a cursory review that the site is not running WordPress or Joomla. We know that CMS' are often "juicy" targets, so let's dig into this one and see what we can uncover.

A Drupal website can be identified in several ways, including by the header or footer message `Powered by Drupal`, the standard Drupal logo, the presence of a `CHANGELOG.txt` file or `README.txt file`, via the page source, or clues in the robots.txt file such as references to `/node`.
        shellsession
`tylapcheong@htb[/htb]$ curl -s http://drupal.inlanefreight.local | grep Drupal`

Another way to identify Drupal CMS is through [nodes](https://www.drupal.org/docs/8/core/modules/node/about-nodes). Drupal indexes its content using nodes. A node can hold anything such as a blog post, poll, article, etc. The page URIs are usually of the form `/node/<nodeid>`.

http://drupal.inlanefreight.local/node/1
For example, the blog post above is found to be at `/node/1`. This representation is helpful in identifying a Drupal website when a custom theme is in use.

Note: Not every Drupal installation will look the same or display the login page or even allow users to access the login page from the internet.

Drupal supports three types of users by default:

1. `Administrator`: This user has complete control over the Drupal website.
2. `Authenticated User`: These users can log in to the website and perform operations such as adding and editing articles based on their permissions.
3. `Anonymous`: All website visitors are designated as anonymous. By default, these users are only allowed to read posts.

## Enumeration

Once we have discovered a Drupal instance, we can do a combination of manual and tool-based (automated) enumeration to uncover the version, installed plugins, and more.

 Newer installs of Drupal by default block access to the `CHANGELOG.txt` and `README.txt` files, so we may need to do further enumeration. Let's look at an example of enumerating the version number using the `CHANGELOG.txt` file. To do so, we can use `cURL` along with `grep`, `sed`, `head`, etc.
 
```
tylapcheong@htb[/htb]$ curl -s http://drupal-acc.inlanefreight.local/CHANGELOG.txt | grep -m2 ""

Drupal 7.57, 2018-02-21
```

Here we have identified an older version of Drupal in use. Trying this against the latest Drupal version at the time of writing, we get a 404 response.

        shellsession
`tylapcheong@htb[/htb]$ curl -s http://drupal.inlanefreight.local/CHANGELOG.txt`

There are several other things we could check in this instance to identify the version. Let's try a scan with `droopescan` as shown in the Joomla enumeration section. `Droopescan` has much more functionality for Drupal than it does for Joomla.

Let's run a scan against the `http://drupal.inlanefreight.local` host.

        shellsession
`tylapcheong@htb[/htb]$ droopescan scan drupal -u http://drupal.inlanefreight.local`

This instance appears to be running version `8.9.1` of Drupal. At the time of writing, this was not the latest as it was released in June 2020. A quick search for Drupal-related [vulnerabilities](https://www.cvedetails.com/vulnerability-list/vendor_id-1367/product_id-2387/Drupal-Drupal.html) does not show anything apparent for this core version of Drupal. In this instance, we would next want to look at installed plugins or abusing built-in functionality.