Many users create their passwords based on `simplicity rather than security`. To mitigate this human tendency (which often undermines security measures), password policies can be implemented on systems to enforce specific password requirements.

Commonly, users use the following additions for their password to fit the most common password policies:

| **Description**                       | **Password Syntax** |
| ------------------------------------- | ------------------- |
| First letter is uppercase             | `Password`          |
| Adding numbers                        | `Password123`       |
| Adding year                           | `Password2022`      |
| Adding month                          | `Password02`        |
| Last character is an exclamation mark | `Password2022!`     |
| Adding special characters             | `P@ssw0rd2022!`     |
 According to statistics provided by [WP Engine](https://wpengine.com/resources/passwords-unmasked-infographic/), most passwords are no longer than `ten` characters.
Let's look at a simple example using a password list with only one entry.

`tylapcheong@htb[/htb]$ cat password.list password`

We can use Hashcat to combine lists of potential names and labels with specific mutation rules to create custom wordlists. Hashcat uses a specific syntax to define characters, words, and their transformations. The complete syntax is documented in the official [Hashcat rule-based attack documentation](https://hashcat.net/wiki/doku.php?id=rule_based_attack), but the examples below are sufficient to understand how Hashcat mutates input words.

|**Function**|**Description**|
|---|---|
|`:`|Do nothing|
|`l`|Lowercase all letters|
|`u`|Uppercase all letters|
|`c`|Capitalize the first letter and lowercase others|
|`sXY`|Replace all instances of X with Y|
|`$!`|Add the exclamation character at the end|
We can use the following command to apply the rules in `custom.rule` to each word in `password.list` and store the mutated results in `mut_password.list`.

`tylapcheong@htb[/htb]$ hashcat --force password.list -r custom.rule --stdout | sort -u > mut_password.list`

Hashcat and JtR both come with pre-built rule lists that can be used for password generation and cracking. One of the most effective and widely used rulesets is `best64.rule`, which applies common transformations that frequently result in successful password guesses. It is important to note that password cracking and the creation of custom wordlists are, in most cases, a guessing game.

## Generating wordlists using CeWL

We can use a tool called [CeWL](https://github.com/digininja/CeWL) to scan potential words from a company's website and save them in a separate list. We can then combine this list with the desired rules to create a customized password list—one that has a higher probability of containing the correct password for an employee. We specify some parameters, like the depth to spider (`-d`), the minimum length of the word (`-m`), the storage of the found words in lowercase (`--lowercase`), as well as the file where we want to store the results (`-w`).

`tylapcheong@htb[/htb]$ cewl https://www.inlanefreight.com -d 4 -m 6 --lowercase -w inlane.wordlist tylapcheong@htb[/htb]$ wc -l inlane.wordlist 326`
