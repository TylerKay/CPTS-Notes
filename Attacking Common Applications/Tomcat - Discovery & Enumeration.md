[Apache Tomcat](https://tomcat.apache.org/) is an open-source web server that hosts applications written in Java. Tomcat was initially designed to run Java Servlets and Java Server Pages (JSP) scripts.

Tomcat is often less apt to be exposed to the internet (though). We see it from time to time on external pentests and can make for an excellent foothold into the internal network. It is far more common to see Tomcat (and multiple instances, for that matter) during internal pentests.

## Discovery/Footprinting

During our external penetration test, we run EyeWitness and see one host listed under "High Value Targets." The tool believes the host is running Tomcat, but we must confirm to plan our attacks. If we are dealing with Tomcat on the external network, this could be an easy foothold into the internal network environment.

Tomcat servers can be identified by the Server header in the HTTP response. If the server is operating behind a reverse proxy, requesting an invalid page should reveal the server and version. Here we can see that Tomcat version `9.0.30` is in use.
http://app-dev.inlanefreight.local:8080/invalid

Custom error pages may be in use that do not leak this version information. In this case, another method of detecting a Tomcat server and version is through the `/docs` page.

        shellsession
`tylapcheong@htb[/htb]$ curl -s http://app-dev.inlanefreight.local:8080/docs/ | grep Tomcat`

This is the default documentation page, which may not be removed by administrators. Here is the general folder structure of a Tomcat installation.
```
        shellsession
├── bin
├── conf
│   ├── catalina.policy
│   ├── catalina.properties
│   ├── context.xml
│   ├── tomcat-users.xml
│   ├── tomcat-users.xsd
│   └── web.xml
├── lib
├── logs
├── temp
├── webapps
│   ├── manager
│   │   ├── images
│   │   ├── META-INF
│   │   └── WEB-INF
|   |       └── web.xml
│   └── ROOT
│       └── WEB-INF
└── work
    └── Catalina
        └── localhost
```

The `bin` folder stores scripts and binaries needed to start and run a Tomcat server. The `conf` folder stores various configuration files used by Tomcat. The `tomcat-users.xml` file stores user credentials and their assigned roles. The `lib` folder holds the various JAR files needed for the correct functioning of Tomcat. The `logs` and `temp` folders store temporary log files. The `webapps` folder is the default webroot of Tomcat and hosts all the applications. The `work` folder acts as a cache and is used to store data during runtime.

Each folder inside webapps is expected to have the following structure.

```
        shellsession
webapps/customapp
├── images
├── index.jsp
├── META-INF
│   └── context.xml
├── status.xsd
└── WEB-INF
    ├── jsp
    |   └── admin.jsp
    └── web.xml
    └── lib
    |    └── jdbc_drivers.jar
    └── classes
        └── AdminServlet.class
```

The most important file among these is `WEB-INF/web.xml`, which is known as the deployment descriptor. This file stores information about the routes used by the application and the classes handling these routes. All compiled classes used by the application should be stored in the `WEB-INF/classes` folder. These classes might contain important business logic as well as sensitive information.

The `lib` folder stores the libraries needed by that particular application. The `jsp` folder stores [Jakarta Server Pages (JSP)](https://en.wikipedia.org/wiki/Jakarta_Server_Pages), formerly known as `JavaServer Pages`, which can be compared to PHP files on an Apache server.
Here’s an example web.xml file.

```
<?xml version="1.0" encoding="ISO-8859-1"?>

<!DOCTYPE web-app PUBLIC "-//Sun Microsystems, Inc.//DTD Web Application 2.3//EN" "http://java.sun.com/dtd/web-app_2_3.dtd">

<web-app>
  <servlet>
    <servlet-name>AdminServlet</servlet-name>
    <servlet-class>com.inlanefreight.api.AdminServlet</servlet-class>
  </servlet>

  <servlet-mapping>
    <servlet-name>AdminServlet</servlet-name>
    <url-pattern>/admin</url-pattern>
  </servlet-mapping>
</web-app>
```
The `web.xml` configuration above defines a new servlet named `AdminServlet` that is mapped to the class `com.inlanefreight.api.AdminServlet`. Java uses the dot notation to create package names, meaning the path on disk for the class defined above would be:
- `classes/com/inlanefreight/api/AdminServlet.class`
Next, a new servlet mapping is created to map requests to `/admin` with `AdminServlet`. This configuration will send any request received for `/admin` to the `AdminServlet.class` class for processing. The `web.xml` descriptor holds a lot of sensitive information and is an important file to check when leveraging a Local File Inclusion (LFI) vulnerability.

The `tomcat-users.xml` file is used to allow or disallow access to the `/manager` and `host-manager` admin pages.

The file shows us what each of the roles `manager-gui`, `manager-script`, `manager-jmx`, and `manager-status` provide access to. In this example, we can see that a user `tomcat` with the password `tomcat` has the `manager-gui` role, and a second weak password `admin` is set for the user account `admin`

## Enumeration

After fingerprinting the Tomcat instance, unless it has a known vulnerability, we'll typically want to look for the `/manager` and the `/host-manager` pages. We can attempt to locate these with a tool such as `Gobuster` or just browse directly to them.

        shellsession
`tylapcheong@htb[/htb]$ gobuster dir -u http://web01.inlanefreight.local:8180/ -w /usr/share/dirbuster/wordlists/directory-list-2.3-small.txt`

We may be able to either log in to one of these using weak credentials such as `tomcat:tomcat`, `admin:admin`, etc. If these first few tries don't work, we can try a password brute force attack against the login page, covered in the next section. If we are successful in logging in, we can upload a [Web Application Resource or Web Application ARchive (WAR)](https://en.wikipedia.org/wiki/WAR_\(file_format\)#:~:text=In%20software%20engineering%2C%20a%20WAR,that%20together%20constitute%20a%20web) file containing a JSP web shell and obtain remote code execution on the Tomcat server.