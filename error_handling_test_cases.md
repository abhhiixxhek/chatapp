# Error Handling Test Cases

## 1. Access Control Errors

**Test Case 1.1: Accessing `@login_required` route `/chat` without login**
*   **Steps:**
    1.  Ensure no user is logged in (clear session/cookies if necessary).
    2.  Attempt to navigate directly to the `/chat` URL.
*   **Expected Result:**
    *   User is redirected to the login page (e.g., `/authorization` which renders `login-register.html`).
    *   The Flask debug log (if active) might show a 302 redirect.

**Test Case 1.2: Accessing `@login_required` route `/logout` without login**
*   **Steps:**
    1.  Ensure no user is logged in.
    2.  Attempt to navigate directly to the `/logout` URL.
*   **Expected Result:**
    *   User is redirected to the login page.

**Test Case 1.3: Accessing `@login_required` route `/imageUploadChat` (POST) without login**
*   **Steps:**
    1.  Ensure no user is logged in.
    2.  Craft and send a POST request (e.g., using cURL or a tool like Postman) to `/imageUploadChat` with necessary form data (even if dummy).
*   **Expected Result:**
    *   Server responds with a redirect to the login page (likely a 302 status code).
    *   No image processing or database changes occur.

## 2. Invalid/Missing Data in SocketIO Events

**Test Case 2.1: `handle_createWorkspace` with missing `name`**
*   **Steps:**
    1.  Authenticated user's client emits `createWorkspace` SocketIO event with `data = {}` or `data = {"other_field": "value"}` (missing `name`).
*   **Expected Result:**
    *   Server emits an `error` event back to the client (e.g., `{'msg': 'Workspace name is required.'}`) via `request.sid`.
    *   No new workspace is created in the database.

**Test Case 2.2: `handle_createChannel` with missing `name` or `wid`**
*   **Steps:**
    1.  Authenticated user's client emits `createChannel` with `data = {"name": "Test"}` (missing `wid`) or `data = {"wid": 1}` (missing `name`).
*   **Expected Result:**
    *   Server emits an `error` event back to the client (e.g., `{'msg': 'Channel name and workspace ID are required.'}`).
    *   No new channel is created.

**Test Case 2.3: `getChannels` with missing `wid`**
*   **Steps:**
    1.  Client emits `getChannels` with `data = {}`.
*   **Expected Result:**
    *   Server emits `getChannelsJS` with `{"channels":[], "channelCount":0, "name":""}`. No server error.

**Test Case 2.4: `getChannels` with non-existent `wid`**
*   **Steps:**
    1.  Client emits `getChannels` with `data = {"wid": 99999}` (assuming 99999 is not a real workspace ID).
*   **Expected Result:**
    *   Server emits `getChannelsJS` with `{"channels":[], "channelCount":0, "name":""}`. No server error.

**Test Case 2.5: `chatmsg` with missing `msg`, `wid`, or `channel_id`**
*   **Steps:**
    1.  Client emits `chatmsg` with incomplete data (e.g., missing `msg`).
*   **Expected Result:**
    *   Server emits an `error` event back (e.g., `{'msg': 'Message content, workspace ID, and channel ID are required.'}`).
    *   No chat message stored.

**Test Case 2.6: `chatmsg` to a non-existent workspace**
*   **Steps:**
    1.  Client emits `chatmsg` with a valid `channel_id` but a `wid` for a non-existent workspace.
*   **Expected Result:**
    *   Server emits an `error` event back (e.g., `{'msg': 'Workspace not found for chat message.'}`).
    *   No chat message stored.

**Test Case 2.7: `getMessages` with non-existent `wid` or `channel_id`**
*   **Steps:**
    1.  Client emits `getMessages` with a `wid` for a non-existent workspace or a `channel_id` not found within the given `wid`.
*   **Expected Result:**
    *   Server emits `receiveMessageJS` with `{"chats":[], "channel_id":..., "name":"Not Found"}`. No server error.

**Test Case 2.8: `joinRoom` with invalid/missing data**
*   **Steps:**
    1. Client emits `joinRoom` with `data={}`.
*   **Expected Result:**
    * Server logs an error ("joinRoom called with insufficient data."). No crash. If this event were critical for UI feedback, an error emit could be added.

**Test Case 2.9: `addWorkspace` with missing `name` or `code`**
*   **Steps:**
    1. Client emits `addWorkspace` with `data={"name": "Test"}` (missing `code`).
*   **Expected Result:**
    * Server emits an `error` event back (e.g., `{'msg': 'Workspace name and joining code are required.'}`).
    * User is not added to any workspace.

## 3. Resource Not Found (HTTP)

**Test Case 3.1: Navigate to a fake URL**
*   **Steps:**
    1.  User attempts to navigate to a URL like `/this/route/does/not/exist`.
*   **Expected Result:**
    *   The custom 404 error page (`404.html`) is displayed.
    *   HTTP status code is 404.

## 4. Server Errors (HTTP)

**Test Case 4.1: Simulate an Unhandled Exception (Conceptual)**
*   **Steps:**
    1.  (Development/Testing) Introduce a temporary code change in a route that will cause an unhandled Python exception (e.g., `raise Exception("Test server error")` in a view function).
    2.  Access that route via a browser or tool.
*   **Expected Result:**
    *   The custom 500 error page (`500.html`) is displayed to the user.
    *   HTTP status code is 500.
    *   The actual exception details are logged on the server but not exposed to the client.

**Test Case 4.2: `sendimage` with `session['imageid']` not set**
*   **Steps:**
    1. Client emits `sendimage` socket event when `session['imageid']` is not set (e.g. direct emit without prior image upload).
*   **Expected Result:**
    * Server logs "Error: 'imageid' not found in session."
    * No further processing, no crash.

**Test Case 4.3: `sendimage` with `imageid` for a chat entry that doesn't exist**
*   **Steps:**
    1. `session['imageid']` is set to an ID that does not correspond to any record in the `Chats` table.
    2. Client emits `sendimage`.
*   **Expected Result:**
    * Server logs "Error: Chat entry not found for imageid XYZ".
    * `session['imageid']` is cleared.
    * No message emitted, no crash.

**Test Case 4.4: `sendimage` for a chat entry whose workspace doesn't exist**
*   **Steps:**
    1. `session['imageid']` refers to a valid chat entry, but its `wid` refers to a non-existent workspace.
    2. Client emits `sendimage`.
*   **Expected Result:**
    * Server logs "Error: Workspace not found for chat entry ID ABC with WID XYZ".
    * No message emitted, no crash.

(Note: Some SocketIO handlers like `joinRoom`, `getChannels`, `getWorkspaceName` might not emit errors directly to client for "not found" scenarios if they are part of background UI updates, but they should log errors and return empty/default data to prevent client-side errors.)
