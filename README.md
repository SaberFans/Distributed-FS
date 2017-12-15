# Distributed FS

Distributed FS implementaion in:
* Transparent File Acess
* Locking for concurrent write access
* Cache
* Directory Service

## Getting Started

### Prerequisites
 * Docker Toolset
 * Python Dev 3.6+

### How to Run

```
docker-compose up
```

### REST API


**Write File**

----
  Write File into System

* **URL**

  /write

* **Method:**

  `POST`
  

* **Data Params**

  * **Content-Type:** `multipart/form-data`
  * **Param Name:** file
  * **Param Name:** path

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{
                    "filepath": "/path1/path2",
                    "response": "OK",
                    "response_code": 200
				}`
 
* **Error Response:**

  * **Code:** 400 <br />
  *  **Content:** `{
    "filename": "filename",
    "path": "/path1",
    "response": "FileExists",
    "response_code": 400
}`


**Read**

----
  Read File from System
  
  * **URL**

  	/read
    
* **Data Params**

  * **Content-Type:** `application/x-www-form-urlencoded`
  * **Param Name:** filename
  * **Param Type:** text
  * **Param Name:** filepath
  * **Param Type:** text


  * **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{
    "filecontent": "b'filecontent'",
    "filepath": "/path",
    "response": "InCache",
    "response_code": 200
	}`
 
* **Error Response:**

  * **Code:** 404 <br />
    **Content:** `{
    "filename": "filename",
    "path": "/path",
    "response": "DirNotExists",
    "response_code": 404
}`

