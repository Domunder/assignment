# NY Times Article Search loader

Loads articles from the NY Times Article Search API in batches and returns each one as a flattened dictionary.

## Setup and run

```
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, set `NY_TIMES_KEY` to your API key, then run:

```
python test.py
```

## Notes

Required tasks:

- [x] Return news items from the NY Times Article Search API as Python dictionaries
- [x] Follow the template, with `getDataBatch` returning results in batches
- [x] Return each result as a flattened dictionary containing all elements of the document
- [x] Define the flatten function without a third-party library
- [x] Provide a `requirements.txt` file
- [x] Provide a README file
- [x] Finished bonus tasks


## Use of AI

I used the Claude extension in VS Code as a sparring partner in manual mode, with code auto-completion turned off. I asked it questions about the code and for hints when I got stuck. To be honest, my current work is mostly reviewing and understanding code that Claude has written, so I'm a bit out of practice at writing code myself.
