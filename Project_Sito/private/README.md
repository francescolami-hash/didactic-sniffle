# Private CV Context

Put the text version of Francesco's CV in:

```text
private/francesco_cv.txt
```

This folder is ignored by Git except for this README, so the real CV text stays private.

Recommended format:

```text
Professional summary
...

Work experience
Company - Role - Dates
- Main responsibilities
- Relevant achievements

Education
...

Skills
...

Languages
...
```

After editing the CV file, restart Flask so the chatbot can reload the context.

For hosted deployments such as Render, prefer setting the CV as a private environment variable:

```text
CV_CONTEXT_TEXT=<paste the CV text here>
```

When `CV_CONTEXT_TEXT` is present, the app uses it before trying to read `private/francesco_cv.txt`.
