![[concepts_of_attacks.png]]

The concept is based on four categories that occur for each vulnerability. First, we have a `Source` that performs the specific request to a `Process` where the vulnerability gets triggered. Each process has a specific set of `Privileges` with which it is executed. Each process has a task with a specific goal or `Destination` to either compute new data or forward it.

## Source

We can generalize `Source` as a source of information used for the specific task of a process. There are many different ways to pass information to a process. The graphic shows some of the most common examples of how information is passed to the processes.

|**Information Source**|**Description**|
|---|---|
|`Code`|This means that the already executed program code results are used as a source of information. These can come from different functions of a program.|
|`Libraries`|A library is a collection of program resources, including configuration data, documentation, help data, message templates, prebuilt code and subroutines, classes, values, or type specifications.|
|`Config`|Configurations are usually static or prescribed values that determine how the process processes information.|
|`APIs`|The application programming interface (API) is mainly used as the interface of programs for retrieving or providing information.|
|`User Input`|If a program has a function that allows the user to enter specific values used to process the information accordingly, this is the manual entry of information by a person.|
The source is, therefore, the source that is exploited for vulnerabilities. It does not matter which protocol is used because HTTP header injections can be manipulated manually, as can buffer overflows. The source for this can therefore be categorized as `Code`

## Processes

The `Process` is about processing the information forwarded from the source. These are processed according to the intended task determined by the program code. For each task, the developer specifies how the information is processed.

|**Process Components**|**Description**|
|---|---|
|`PID`|The Process-ID (PID) identifies the process being started or is already running. Running processes have already assigned privileges, and new ones are started accordingly.|
|`Input`|This refers to the input of information that could be assigned by a user or as a result of a programmed function.|
|`Data processing`|The hard-coded functions of a program dictate how the information received is processed.|
|`Variables`|The variables are used as placeholders for information that different functions can further process during the task.|
|`Logging`|During logging, certain events are documented and, in most cases, stored in a register or a file. This means that certain information remains in the system.|
## Privileges

`Privileges` are present in any system that controls processes. These serve as a type of permission that determines what tasks and actions can be performed on the system. In simple terms, it can be compared to a bus ticket.

| **Privileges** | **Description**                                                                                                                                                                                           |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `System`       | These privileges are the highest privileges that can be obtained, which allow any system modification. In Windows, this type of privilege is called `SYSTEM`, and in Linux, it is called `root`.          |
| `User`         | User privileges are permissions that have been assigned to a specific user. For security reasons, separate users are often set up for particular services during the installation of Linux distributions. |
| `Groups`       | Groups are a categorization of at least one user who has certain permissions to perform specific actions.                                                                                                 |
| `Policies`     | Policies determine the execution of application-specific commands, which can also apply to individual or grouped users and their actions.                                                                 |
| `Rules`        | Rules are the permissions to perform actions handled from within the applications themselves.                                                                                                             |
## Destination

Every task has at least one purpose and goal that must be fulfilled. Logically, if any data set changes were missing or not stored or forwarded anywhere, the task would be generally unnecessary. The result of such a task is either stored somewhere or forwarded to another processing point. Therefore we speak here of the `Destination` where the changes will be made.

|**Destination**|**Description**|
|---|---|
|`Local`|The local area is the system's environment in which the process occurred. Therefore, the results and outcomes of a task are either processed further by a process that includes changes to data sets or storage of the data.|
|`Network`|The network area is mainly a matter of forwarding the results of a process to a remote interface. This can be an IP address and its services or even entire networks. The results of such processes can also influence the route under certain circumstances.|