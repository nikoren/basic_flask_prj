


Basic querying


- Anonymous request


```http
─$  http --json --auth : GET http://127.0.0.1:5000/api/v1/get_token 
HTTP/1.0 401 UNAUTHORIZED
Content-Length: 67
Content-Type: application/json
Date: Tue, 23 May 2017 12:59:05 GMT
Server: Werkzeug/0.11.15 Python/2.7.13
WWW-Authenticate: Basic realm="Authentication Required"

{
    "error": "unauthorized", 
    "message": "invalid credentials"
}


```

- Password authentication


```http

http --auth nikoren@gmail.com:niko11niko@ GET http://127.0.0.1:5000/api/v1/get_token
HTTP/1.0 200 OK
Content-Length: 163
Content-Type: application/json
Date: Tue, 23 May 2017 12:55:21 GMT
Server: Werkzeug/0.11.15 Python/2.7.13

{
    "expiration": 3600, 
    "token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ5NTU0NzcyMSwiaWF0IjoxNDk1NTQ0MTIxfQ.eyJpZCI6MX0.o-JgASecwzym2YMStz1tBkfgk9WPVsNlXeJh5l6kxHU"
}

```


- boilerpate

```bash
export TOKEN='eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ5NjAyMzkyOCwiaWF0IjoxNDk2MDIwMzI4fQ.eyJpZCI6MX0.uqekaWmKIG_nc5O-8pQokGivrxb12FEiVq5hlB_odRw:'
export API='http://localhost:5000/api/v1'


```



- Token authentication


```bash
╰─$ http --json --auth $TOKEN GET ${API}/user/1
HTTP/1.0 200 OK
Content-Length: 145
Content-Type: application/json
Date: Tue, 23 May 2017 13:10:10 GMT
Server: Werkzeug/0.11.15 Python/2.7.13

{
    "confirmed": true, 
    "email": "nikoren@gmail.com", 
    "id": 1, 
    "role": "http://127.0.0.1:5000/api/v1/role/1", 
    "username": "nikoren"
}
```


- create user


```bash
╰─$ http -a $TOKEN POST $API/users/ role="$API/role/2" username='testX1' email='testX2@gmail.com' confirmed='true'
HTTP/1.0 201 CREATED
Content-Length: 3
Content-Type: application/json
Date: Mon, 29 May 2017 01:45:06 GMT
Location: http://localhost:5000/api/v1/user/5
Server: Werkzeug/0.11.15 Python/2.7.13

{}

```

- update user ( all fields should be provided even though not updated)

```bash
╰─$ http --auth $TOKEN PUT http://localhost:5000/api/v1/users/5 email=txe@gmail.com role=http://localhost:5000/api/v1/role/1 username=testX1            
HTTP/1.0 200 OK
Content-Length: 195
Content-Type: application/json
Date: Mon, 29 May 2017 02:10:25 GMT
Server: Werkzeug/0.11.15 Python/2.7.13

{
    "confirmed": true, 
    "email": "txe@gmail.com", 
    "id": 5, 
    "role": "http://localhost:5000/api/v1/role/1", 
    "self_url": "http://localhost:5000/api/v1/users/5", 
    "username": "testX1"
}


```


- delete user


```bash

╰─$ http --auth $TOKEN DELETE http://localhost:5000/api/v1/users/5 
HTTP/1.0 204 NO CONTENT
Content-Length: 0
Content-Type: application/json
Date: Mon, 29 May 2017 02:15:53 GMT
Server: Werkzeug/0.11.15 Python/2.7.13

```
