# Example: Web API Architecture (ASCII)

This is an example ASCII architecture diagram for validating the tachi interface contract and output template. It depicts a web API with authentication, showing components across trust boundary zones.

**DFD Element Classification:**
- External User: External Entity
- API Gateway: Process
- Auth Service: Process
- User Database: Data Store

```
format: ascii
```

## Architecture Diagram

```
+------------------+
|  External User   |
|  (browser/app)   |
+--------+---------+
         |
         | HTTPS requests
         | (credentials, API calls)
         |
- - - - -|- - - - - - - - - - - - - - - - - - - - - Trust Boundary
         |                                           (External / Internal)
         |
+--------v---------+
|                   |
|   API Gateway     |
|   (NGINX/Kong)    |
|                   |
+--+-------------+--+
   |             |
   |             |  Validate token
   |             |  (JWT bearer token)
   |             |
   |        +----v--------------+
   |        |                   |
   |        |  Auth Service     |
   |        |  (Node.js)        |
   |        |                   |
   |        +----+--------------+
   |             |
   |             | Verify credentials
   |             | (username, password hash)
   |             |
   |        +----v--------------+
   |        |                   |
   |        |  User Database    |
   |        |  (PostgreSQL)     |
   |        |                   |
   |        +-------------------+
   |
   | Query/mutate data
   | (SQL over TLS)
   |
   v
```

## Data Flows

```
External User ---[HTTPS: login credentials]--> API Gateway
External User ---[HTTPS: API requests + JWT]--> API Gateway
API Gateway   ---[HTTP: JWT token]-----------> Auth Service
Auth Service  ---[SQL: credential lookup]----> User Database
Auth Service  ---[HTTP: auth result]---------> API Gateway
API Gateway   ---[SQL: data queries]---------> User Database
API Gateway   ---[HTTPS: API responses]------> External User
```

## Trust Boundary

```
- - - - - - - - - - - - - - - - - - - - - -
  EXTERNAL ZONE          INTERNAL ZONE
- - - - - - - - - - - - - - - - - - - - - -
  External User     |    API Gateway
                    |    Auth Service
                    |    User Database
- - - - - - - - - - - - - - - - - - - - - -
```

All internal components (API Gateway, Auth Service, User Database) reside within the internal trust zone. The External User communicates across the trust boundary exclusively via HTTPS through the API Gateway.
