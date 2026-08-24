[GitLab](https://about.gitlab.com/) is a web-based Git-repository hosting tool that provides wiki capabilities, issue tracking, and continuous integration and deployment pipeline functionality. GitLab is similar to GitHub and BitBucket, which are also web-based Git repository tools. A comparison between the three can be seen [here](https://stackshare.io/stackups/bitbucket-vs-github-vs-gitlab).

During internal and external penetration tests, it is common to come across interesting data in a company's GitHub repo or a self-hosted GitLab or BitBucket instance.

We may also find scripts or configuration files that were accidentally committed containing cleartext secrets such as passwords that we may use to our advantage. We may also come across SSH private keys. We can attempt to use the search function to search for users, passwords, etc. Applications such as GitLab allow for public repositories (that require no authentication), internal repositories (available to authenticated users), and private repositories (restricted to specific users). We'll see later on, a GitLab instance can be set up to allow anyone to register and then log in.

## Footprinting & Discovery

We can quickly determine that GitLab is in use in an environment by just browsing to the GitLab URL, and we will be directed to the login page, which displays the GitLab logo. 

The only way to footprint the GitLab version number in use is by browsing to the `/help` page when logged in. If the GitLab instance allows us to register an account, we can log in and browse to this page to confirm the version. If we cannot register an account, we may have to try a low-risk exploit such as [this](https://www.exploit-db.com/exploits/49821). There have been a few serious exploits against GitLab [12.9.0](https://www.exploit-db.com/exploits/48431) and GitLab [11.4.7](https://www.exploit-db.com/exploits/49257) in the past few years as well as GitLab Community Edition [13.10.3](https://www.exploit-db.com/exploits/49821), [13.9.3](https://www.exploit-db.com/exploits/49944), and [13.10.2](https://www.exploit-db.com/exploits/49951).

## Enumeration

There's not much we can do against GitLab without knowing the version number or being logged in. The first thing we should try is browsing to `/explore` and see if there are any public projects that may contain something interesting. Browsing to this page, we see a project called `Inlanefreight dev`.

```
http://gitlab.inlanefreight.local:8081/explore
```

Browsing to the project, it looks like an example project and may not contain anything useful, though it is always worth digging around.

From here, we can explore each of the pages linked in the top left `groups`, `snippets`, and `help`. We can also use the search functionality and see if we can uncover any other projects. Suppose the organization did not set up GitLab only to allow company emails to register or require an admin to approve a new account. In that case, we may be able to access additional data.

We can also use the registration form to enumerate valid users (more on this in the next section). If we can make a list of valid users, we could attempt to guess weak passwords or possibly re-use credentials that we find from a password dump using a tool such as `Dehashed` as seen in the osTicket section. Here we can see the user `root` is taken.

If we try to register with an email that has already been taken, we will get the error `1 error prohibited this user from being saved: Email has already been taken`. As of the time of writing, this username enumeration technique works with the latest version of GitLab.  Even if the `Sign-up enabled` checkbox is cleared within the settings page under `Sign-up restrictions`, we can still browse to the `/users/sign_up` page and enumerate users but will not be able to register a user.

Some mitigations can be put in place for this, such as enforcing 2FA on all user accounts, using `Fail2Ban` to block failed login attempts which are indicative of brute-forcing attacks, and even restricting which IP addresses can access a GitLab instance if it must be accessible outside of the internal corporate network. 

Let's go ahead and register with the credentials `hacker:Welcome` and log in and poke around. As soon as we complete registration, we are logged in and brought to the projects dashboard page. If we go to the `/explore` page now, we notice that there is now an internal project `Inlanefreight website` available to us. In a real-world scenario, we may be able to find a considerable amount of sensitive data if we can register and gain access to any of their repositories.

In a real-world scenario, we may be able to find a considerable amount of sensitive data if we can register and gain access to any of their repositories. As this [blog post](https://tillsongalloway.com/finding-sensitive-information-on-github/index.html) explains, there is a considerable amount of data that we may be able to uncover on GitLab, GitHub, etc.