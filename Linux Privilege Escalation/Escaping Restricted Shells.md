A restricted shell is a type of shell that limits the user's ability to execute commands.
#### RBASH
[Restricted Bourne shell](https://www.gnu.org/software/bash/manual/html_node/The-Restricted-Shell.html) (`rbash`) is a restricted version of the Bourne shell, a standard command-line interpreter in Linux which limits the user's ability to use certain features of the Bourne shell, such as changing directories, setting or modifying environment variables, and executing commands in other directories.
#### RKSH
[Restricted Korn shell](https://www.ibm.com/docs/en/aix/7.2?topic=r-rksh-command) (`rksh`) is a restricted version of the Korn shell, another standard command-line interpreter. The `rksh` shell limits the user's ability to use certain features of the Korn shell, such as executing commands in other directories, creating or modifying shell functions, and modifying the shell environment.

#### RZSH
[Restricted Z shell](https://manpages.debian.org/experimental/zsh/rzsh.1.en.html) (`rzsh`) is a restricted version of the Z shell and is the most powerful and flexible command-line interpreter. The `rzsh` shell limits the user's ability to use certain features of the Z shell, such as running shell scripts, defining aliases, and modifying the shell environment.

Several methods can be used to escape from a restricted shell. Some of these methods involve exploiting vulnerabilities in the shell itself, while others involve using creative techniques to bypass the restrictions imposed by the shell. Here are a few examples of methods that can be used to escape from a restricted shell.

## Escaping

In some cases, it may be possible to escape from a restricted shell by injecting commands into the command line or other inputs the shell accepts

#### Command injection

Imagine that we are in a restricted shell that allows us to execute commands by passing them as arguments to the `ls` command.

For example, we could use the following command to inject a `pwd` command into the argument of the `ls` command:

        shellsession
`` tylapcheong@htb[/htb]$ ls -l `pwd` ``

This command would cause the `ls` command to be executed with the argument `-l`, followed by the output of the `pwd` command. Since the `pwd` command is not restricted by the shell, this would allow us to execute the `pwd` command and see the current working directory, even though the shell does not allow us to execute the `pwd` command directly.

#### Command Substitution

Another method for escaping from a restricted shell is to use command substitution. This involves using the shell's command substitution syntax to execute a command. For example, imagine the shell allows users to execute commands by enclosing them in backticks (`). In that case, it may be possible to escape from the shell by executing a command in a backtick substitution that is not restricted by the shell.

#### Command Chaining

In some cases, it may be possible to escape from a restricted shell by using command chaining. We would need to use multiple commands in a single command line, separated by a shell metacharacter, such as a semicolon (`;`) or a vertical bar (`|`), to execute a command.

#### Environment Variables

For escaping from a restricted shell to use environment variables involves modifying or creating environment variables that the shell uses to execute commands that are not restricted by the shell.

#### Shell Functions

In some cases, it may be possible to escape from a restricted shell by using shell functions. For this we can define and call shell functions that execute commands not restricted by the shell.



### Notes
- Search for {Restricted shell} bypasses. 
- ssh htb-user@10.129.205.109 -t "bash --noprofile"
- https://www.sans.org/blog/escaping-restricted-linux-shells