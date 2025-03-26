Data Pusher API
Overview
The Data Pusher API is a robust, Django-based application that facilitates the handling of data from one account to multiple destinations (via webhook URLs). It allows users to manage destinations, logs, and data handling asynchronously. The API implements features such as data validation, rate limiting, role-based access control, logging, caching, and more, ensuring the application is secure, performant, and flexible.

Features
1. Account Management
Create, Update, Delete Accounts: The account represents the primary entity in the application. Each account has a unique ID, name, secret token, and timestamps associated with it. Admins can create new accounts, update existing ones, and delete accounts if necessary.

App Secret Token: Each account is associated with a unique token (app secret). This token is used for validating requests and ensuring the security of data transfers.

User Tracking: The account keeps track of the user that created or updated the account, enabling better audit and security controls.

2. Destination Management
Destination Creation: Each account can have one or more destinations. A destination is essentially a webhook URL where data will be sent. Destinations are associated with an HTTP method (GET, POST, PUT), headers, and other relevant metadata.

HTTP Method and Headers: When sending data to a destination, the application allows choosing the HTTP method and headers. Headers might include API keys, authentication tokens, or custom identifiers (such as APP_ID or APP_SECRET).

Timestamp Management: Each destination includes a timestamp indicating when the destination was created or updated.

3. User Management
Role-Based Access: Users in the system have different roles, such as Admin or Normal User. Admin users have full CRUD (Create, Read, Update, Delete) access to all accounts and destinations. Normal users can only view and update destinations associated with their account.

User Registration: During the first registration, the system automatically assigns the first user as an Admin. Subsequent users will be given a Normal User role unless explicitly changed by an admin.

4. Account Member Management
Assign Roles to Members: Admins can invite other users to join their account and assign specific roles (Admin or Normal User). Members can only access data related to the account they are associated with.

Role-Based Permissions: Only Admins have the ability to manage other users' roles within the account. Normal users have limited access and cannot modify other users' roles.

5. Log Management
Event Logs: Every interaction with the system (e.g., sending data to a destination) generates a log entry. Logs capture critical information like the event ID, account ID, destination, timestamps, and the status of data sent.

Log Access: Admins have unrestricted access to view all logs, whereas Normal Users can only view logs related to their own account.

Status Tracking: The logs include the status of data sent (successful, failed, etc.), which allows users to track and troubleshoot data-handling issues.

6. Data Handler API
POST Requests: The /server/incoming_data endpoint accepts JSON data via POST requests. This data is sent to the associated destinations (webhook URLs) as part of the processing pipeline.

Header Requirements: Every request to the data handler API must include specific headers, such as CL-X-TOKEN (the app secret) and CL-X-EVENT-ID (a unique event ID), for validation and security.

Async Processing: Once data is validated, the system uses Django Channels or Celery to send data asynchronously, ensuring that the API remains responsive even under high load.

7. Asynchronous Processing
Celery or Django Channels: The application uses Celery for background task management or Django Channels for real-time processing. This allows the application to offload data processing tasks (e.g., sending data to destinations) to background workers, ensuring fast response times for user requests.

Queue Management: Asynchronous tasks are queued and processed in the background, preventing the main application from being blocked by time-consuming tasks.

8. Authentication & Authorization
User Authentication: Users authenticate via Django’s built-in authentication system or third-party services. The system uses Token Authentication to secure the API, ensuring that only authorized users can access protected endpoints.

Obtain Auth Token: Users can obtain a token by providing their email and password through the obtain-token endpoint. This token is then used to authorize requests.

Role-Based Access Control: Admin users have access to manage all accounts, destinations, and logs, while Normal Users can only access data for their specific account.

9. Caching & Performance Optimization
Caching: Frequently accessed data, such as account details or destination information, is cached to improve performance. This reduces the load on the database and speeds up response times for users.

Query Optimization: Advanced querying mechanisms ensure that only relevant data is fetched, and database queries are optimized to prevent N+1 query problems. This ensures the system performs well even with a large number of records.

10. API Rate Limiting & Throttling
Rate Limiting: The API implements rate limiting to prevent abuse and ensure fair usage. For example, requests to /server/incoming_data are limited to 5 per second per account to avoid overloading the system.

Throttling: The throttling mechanism controls the rate at which requests can be made, protecting the backend from excessive traffic and ensuring high availability.

11. Data Validation
Field Validation: Custom validators are implemented to ensure the integrity of incoming data. For example, the email address must follow a valid format, and URLs must be well-formed.

Error Handling: If any of the data is invalid, the system returns an "Invalid Data" response, which helps users quickly identify issues with their requests.

12. Search & Filtering
Advanced Querying: The application supports filtering and querying logs, destinations, and account data based on multiple criteria (e.g., timestamps, status, destination ID).

Search Functionality: Users can search through logs and destinations to quickly find relevant data, making it easier to manage and troubleshoot large datasets.

13. Comprehensive Testing
Unit Tests: All features are thoroughly tested using Django’s built-in test framework. This ensures that the application works as expected and that edge cases and potential errors are handled gracefully.

Test Coverage: The test suite covers critical aspects of the system, such as authentication, data handling, logging, and rate limiting.

14. Documentation
Swagger UI: The API documentation is available via Swagger UI. You can access it at http://127.0.0.1:8000/swagger/.

Token Authentication:

Open Swagger UI at http://127.0.0.1:8000/swagger/.

Navigate to the obtain-token endpoint to obtain a token by providing your email and password.

Once you obtain the token, use it to authenticate subsequent requests by clicking the Authorize button in Swagger and entering the token.

Installation
1. Clone the Repository
Clone the repository from GitHub to your local machine:

bash
Copy
Edit
git clone https://github.com/M-s-vignesh/Data_Pusher.git
2. Install Dependencies
Navigate to the project directory and install the required Python dependencies:

bash
Copy
Edit
cd Data_Pusher
pip install -r requirements.txt
3. Apply Migrations
Apply the necessary database migrations to set up the database schema:

bash
Copy
Edit
python manage.py migrate
4. Create a Superuser
Create a superuser account to manage the system through Django's admin panel:

bash
Copy
Edit
python manage.py createsuperuser
5. Run the Server
Start the development server to begin using the API:

bash
Copy
Edit
python manage.py runserver

Open Swagger UI at http://127.0.0.1:8000/swagger/

Running Unit Tests
If you'd like to ensure the application is working as expected, you can run the unit tests. Unit tests help verify that the functionality of the application is correct and that new changes do not break existing features.

1. Run Unit Tests
To run the unit tests for the application, you can use the Django test command:

bash
Copy
Edit
python manage.py test
This command will automatically discover and execute all the test cases in the project. If any tests fail, the command will provide details about the failures so you can debug them.

2. Test Output
After running the tests, you should see output indicating the number of tests run and whether they passed or failed. A typical successful test run would look like:

bash
Copy
Edit
Creating test database for alias 'default'...
.....

----------------------------------------------------------------------
Ran 5 tests in 2.345s

OK
If there are any test failures, the output will indicate which tests failed and provide error messages to help you identify the issue.


API Endpoints
1. Account CRUD Operations
GET /accounts/: Retrieve all accounts for the authenticated user.

POST /accounts/: Create a new account.

PUT /accounts/{id}/: Update an existing account.

DELETE /accounts/{id}/: Delete an account.

2. Destination CRUD Operations
GET /destinations/: Retrieve all destinations for the logged-in account.

POST /destinations/: Add a new destination.

PUT /destinations/{id}/: Update a destination.

DELETE /destinations/{id}/: Delete a destination.

3. Account Member CRUD Operations
GET /account-members/: Retrieve all account members.

POST /account-members/: Add a new member to an account.

PUT /account-members/{id}/: Update account member details.

DELETE /account-members/{id}/: Remove a member from an account.

4. Log Retrieval
GET /logs/: Retrieve logs for the logged-in account.

GET /logs/{destination_id}/: Retrieve logs filtered by destination ID.

5. Incoming Data API
POST /server/incoming_data: Receive JSON data and send it asynchronously to destinations.

Workflow Tree
├── Create User Account
│   └── User provides personal information (email, password)
│   └── Validate input data
│   └── Store user data in the database
├── Login through Authentication
│   └── User enters credentials (email, password)
│   └── Validate credentials
│   └── Generate and return authentication token
│   └── Authenticate user session
├── Create Users
│   └── Admin or authorized user creates new users
│   └── Provide user details (email, password)
│   └── Store new user data in the database
├── Create Accounts
│   └── Admin create new accounts for different services
│   └── Provide account details (account name, website, etc.)
│   └── Store account data in the database
├── Create Account Members
│   └── Admin adds members to the created accounts
│   └── Provide member details (name, role, access rights, etc.)
│   └── Assign members to appropriate accounts
├── Send Data Through Server / Incoming Data
│   └── Users or systems send data to the server
│   └── Validate incoming data
│   └── Process and store data in the backend/database
    └── Adds logs to the appropriate destinations and account
│   └── Send response or confirmation back to the client

