# Authentication Flow Test Cases

## 1. Registration

**Test Case 1.1: Successful Registration**
*   **Steps:**
    1.  Navigate to the signup page.
    2.  Fill in a unique email address.
    3.  Fill in a unique username.
    4.  Enter a password.
    5.  Confirm the password (if applicable).
    6.  Upload an image for the profile picture.
    7.  Submit the registration form.
*   **Expected Result:**
    *   User is redirected to the login page (or a success page indicating they should now log in).
    *   A new user record is created in the database with the provided email, username, and a hashed version of the password.
    *   The profile image URL is correctly stored.

**Test Case 1.2: Registration with Existing Email**
*   **Steps:**
    1.  Navigate to the signup page.
    2.  Fill in an email address that already exists in the database.
    3.  Fill in a unique username.
    4.  Enter a password.
    5.  Upload an image.
    6.  Submit the form.
*   **Expected Result:**
    *   An error message "Email already taken. Please try again." (or similar) is displayed on the `login-register.html` page.
    *   No new user record is created.

**Test Case 1.3: Registration with Existing Username**
*   **Steps:**
    1.  Navigate to the signup page.
    2.  Fill in a unique email address.
    3.  Fill in a username that already exists in the database.
    4.  Enter a password.
    5.  Upload an image.
    6.  Submit the form.
*   **Expected Result:**
    *   An error message "Name already taken. Please try again." (or similar) is displayed on the `login-register.html` page.
    *   No new user record is created.

**Test Case 1.4: Registration with Missing Required Fields**
*   **Steps:**
    1.  Navigate to the signup page.
    2.  Fill in some fields but leave a required field empty (e.g., password or email or name).
    3.  Submit the form.
*   **Expected Result:**
    *   An error message "Invalid Credentials. Please try again." (or similar, based on implementation) is displayed on the `login-register.html` page.
    *   No new user record is created.

## 2. Login

**Test Case 2.1: Successful Login**
*   **Steps:**
    1.  Navigate to the login page.
    2.  Enter the username of an existing user.
    3.  Enter the correct password for that user.
    4.  Optionally, check the "Remember me" box.
    5.  Submit the login form.
*   **Expected Result:**
    *   User is redirected to the chat page (e.g., `/chat`).
    *   The user is logged in (`current_user` is populated and `current_user.is_authenticated` is true).
    *   If "Remember me" was checked, the session cookie should be persistent.

**Test Case 2.2: Login with Incorrect Password**
*   **Steps:**
    1.  Navigate to the login page.
    2.  Enter the username of an existing user.
    3.  Enter an incorrect password.
    4.  Submit the login form.
*   **Expected Result:**
    *   An error message "Please check your login details and try again." (or similar) is displayed on the `login-register.html` page.
    *   User is not logged in.

**Test Case 2.3: Login with Non-existent Username**
*   **Steps:**
    1.  Navigate to the login page.
    2.  Enter a username that does not exist in the database.
    3.  Enter any password.
    4.  Submit the login form.
*   **Expected Result:**
    *   An error message "Please check your login details and try again." (or similar) is displayed on the `login-register.html` page.
    *   User is not logged in.

**Test Case 2.4: Login with Missing Fields**
*   **Steps:**
    1.  Navigate to the login page.
    2.  Leave username or password field empty.
    3.  Submit the login form.
*   **Expected Result:**
    *   An error message "Missing Data" (or similar) is displayed on the `login-register.html` page.
    *   User is not logged in.

## 3. Logout

**Test Case 3.1: Successful Logout**
*   **Steps:**
    1.  Log in as an existing user.
    2.  Navigate to the `/logout` URL (or click a logout button).
*   **Expected Result:**
    *   User is logged out (`current_user.is_authenticated` is false).
    *   User is redirected to the `login-register.html` page (or another appropriate public page).
    *   Session data related to the user's identity and custom application data (e.g., `imageid`, workspace `name` in session) is cleared.
    *   Attempting to access a protected page (e.g., `/chat`) should redirect the user to the login page.

## 4. Session Persistence ("Remember Me")

**Test Case 4.1: Login with "Remember Me" Checked**
*   **Steps:**
    1.  Navigate to the login page.
    2.  Enter valid credentials for an existing user.
    3.  Check the "Remember me" checkbox.
    4.  Submit the login form.
    5.  Verify successful login and redirection to a protected page.
    6.  Close the browser completely.
    7.  Reopen the browser and navigate back to the application's protected page (e.g., `/chat`).
*   **Expected Result:**
    *   User is still logged in and can access the protected page without needing to re-enter credentials.

**Test Case 4.2: Login without "Remember Me" Checked**
*   **Steps:**
    1.  Navigate to the login page.
    2.  Enter valid credentials for an existing user.
    3.  Ensure the "Remember me" checkbox is unchecked.
    4.  Submit the login form.
    5.  Verify successful login and redirection to a protected page.
    6.  Close the browser completely.
    7.  Reopen the browser and navigate back to the application's protected page (e.g., `/chat`).
*   **Expected Result:**
    *   User is logged out and is redirected to the login page. Access to the protected page is denied until login.
