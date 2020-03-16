# Motherly Overwatch Monitor

This system is designed for very simple monitoring of processes and systems which cannot be queried by an HTTP request.

- The subsystem that wants to report it's status is called a child 
- It will regularly call an endpoint which will note down the time it was called

---

- The API can then be used to query the status of a child either in JSON format or as an image pixel for a dashboard


