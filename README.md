# `followmail`

_followmail_ is a command line utility that parse a postfix log file (also gzipped) and follow pathway of specific mail,
in **to** or **from** fields.

## Installation

To install _followmail_, follow this:

```console
# With pypi
pip install followmail

# With git
git clone https://github.com/MatteoGuadrini/followmail.git && cd followmail
pip install .
```

## Command arguments

`followmail` have many command line arguments. They are explained in this table:

| short | long           | description                       | args          |
|-------|----------------|-----------------------------------|---------------|
| -v    | --verbose      | Print with verbosity              |               |
| -t    | --to           | Email address into **to** field   | Mail address  |
| -f    | --from         | Email address into **from** field | Mail address  |
| -l    | --maillog      | Input maillog file                | File path     |
| -q    | --queue        | Name of postfix queue             | Name of queue |
| -m    | --max-lines    | Max lines to print                | Number        |
| -D    | --sortby-date  | Sort lines by date                |               |
| -Q    | --sortby-queue | Sort lines by queue               |               |
| -D    | --sortby-server| Sort lines by server              |               |
| -c    | --csv          | Print in csv format               |               |
| -j    | --json         | Print in json format              |               |

## Examples

1. Search into **to** field the email _other@example.com_:

    ```bash
    followmail -t other@example.com
    ```

2. Search into **from** field the email _other@example.com_:

    ```bash
    followmail -f other@example.com
    ```

3. Search both **from** and **to** fields:

    ```bash
    followmail -f other@example.com -t other2@example.com
    ```
   
4. Filter per queue

   ```bash
    followmail -f other@example.com -t other2@example.com -q "postfix/in"
    ```
   
5. Select archived log

   ```bash
    followmail -f other@example.com -t other2@example.com -l "/var/log/maillog-20240709.tar.gz"
    ```
   
6. Select max 20 max lines

   ```bash
    followmail -f other@example.com -t other2@example.com -m 20
    ```

7. Sort results by date, queue or server

   ```bash
    followmail -f other@example.com -t other2@example.com -D
    followmail -f other@example.com -t other2@example.com -Q
    followmail -f other@example.com -t other2@example.com -S
    ```

8. Print result in CSV format

   ```bash
    followmail -f other@example.com -t other2@example.com -c
    ```

9. Print result in JSON format

   ```bash
    followmail -f other@example.com -t other2@example.com -j
    ```

10. Debugging

    ```bash
     followmail -f other@example.com -t other2@example.com -v
     ```


## Open source

_followmail_ is an open source project. Any contribute, It's welcome.

**A great thanks**.

For donations, press this

For me

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/guos)

For [Telethon](http://www.telethon.it/)

The Telethon Foundation is a non-profit organization recognized by the Ministry of University and Scientific and
Technological Research.
They were born in 1990 to respond to the appeal of patients suffering from rare diseases.
Come today, we are organized to dare to listen to them and answers, every day of the year.

[Adopt the future](https://www.ioadottoilfuturo.it/)

## Treeware

This package is [Treeware](https://treeware.earth). If you use it in production,
then we ask that you [**buy the world a tree**](https://plant.treeware.earth/matteoguadrini/mkpl) to thank us for our
work.
By contributing to the Treeware forest you’ll be creating employment for local families and restoring wildlife habitats.

[![Treeware](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=Treeware&query=%24.total&url=https%3A%2F%2Fpublic.offset.earth%2Fusers%2Ftreeware%2Ftrees)](https://treeware.earth)

## Acknowledgments

Thanks to Mark Lutz for writing the _Learning Python_ and _Programming Python_ books that make up my python foundation.

Thanks to Kenneth Reitz and Tanya Schlusser for writing the _The Hitchhiker’s Guide to Python_ books.

Thanks to Dane Hillard for writing the _Practices of the Python Pro_ books.

Special thanks go to my wife, who understood the hours of absence for this development.
Thanks to my children, for the daily inspiration they give me and to make me realize, that life must be simple.

Thanks, Python!