# Workspace Management Test Cases

## 1. Create Workspace

**Test Case 1.1: Successful Workspace Creation**
*   **Steps:**
    1.  Ensure the user is authenticated.
    2.  Client emits `createWorkspace` SocketIO event with a new workspace name (e.g., "My New Workspace").
*   **Expected Result:**
    *   Server receives the event.
    *   A new `Workspace` record is created in the database with the provided name, `current_user.name` as `admin_username`, and a generated `joining_code`.
    *   The `id` of this new workspace is appended to the `user.workspace_list` in the `User` record (ensuring space separation and a trailing space, e.g., "id1 id2 ").
    *   A `createWorkspaceJS` SocketIO event is emitted back to all clients (or relevant room) containing the new workspace's details: `name`, `admin_username` (which is `current_user.name`), `id`, and `joining_code`.
    *   The user's UI updates to show the new workspace in their list.

**Test Case 1.2: Attempt to Create Workspace When Not Authenticated**
*   **Steps:**
    1.  User is not authenticated (e.g., no valid session/cookie).
    2.  Client attempts to emit `createWorkspace` SocketIO event.
*   **Expected Result:**
    *   The action should fail. Ideally, the SocketIO connection or event handler on the server-side should reject the request due to lack of authentication (e.g., `current_user` would be AnonymousUserMixin).
    *   No new workspace is created. No event emitted back, or an error event specific to authentication failure.

## 2. Join Workspace

**Test Case 2.1: Successful Join to an Existing Workspace**
*   **Steps:**
    1.  Ensure the user is authenticated.
    2.  Another user has already created a workspace with a known name (e.g., "Target Workspace") and `joining_code`.
    3.  Client emits `joinWorkspace` SocketIO event with `name`: "Target Workspace" and `code`: (the valid joining code).
*   **Expected Result:**
    *   Server receives the event.
    *   The server validates that a workspace exists with the given name and joining code.
    *   The `id` of "Target Workspace" is appended to the `user.workspace_list` for the joining user (ensuring space separation and trailing space, and no duplicates).
    *   A `workspaceJoined` SocketIO event is emitted back to the joining user (via `request.sid`) with the workspace `id`, `username` (`current_user.name`), and `name`.
    *   The user's UI updates to show "Target Workspace" in their list.

**Test Case 2.2: Attempt to Join with Invalid Joining Code**
*   **Steps:**
    1.  Ensure the user is authenticated.
    2.  A workspace "Target Workspace" exists.
    3.  Client emits `joinWorkspace` SocketIO event with `name`: "Target Workspace" and `code`: "INVALIDCODE".
*   **Expected Result:**
    *   Server receives the event.
    *   Server queries for the workspace and finds no match for the name and code combination.
    *   An `error` SocketIO event is emitted back to the joining user (via `request.sid`) with a message like "Invalid workspace name or joining code."
    *   `user.workspace_list` is not modified.

**Test Case 2.3: Attempt to Join with Non-existent Workspace Name**
*   **Steps:**
    1.  Ensure the user is authenticated.
    2.  Client emits `joinWorkspace` SocketIO event with `name`: "NonExistentWorkspace" and `code`: "ANYCODE".
*   **Expected Result:**
    *   Server receives the event.
    *   Server queries for the workspace and finds no match.
    *   An `error` SocketIO event is emitted back to the joining user (via `request.sid`) with a message like "Invalid workspace name or joining code."
    *   `user.workspace_list` is not modified.

**Test Case 2.4: Attempt to Join a Workspace User is Already Part Of**
*   **Steps:**
    1.  Ensure the user is authenticated and has already joined "Target Workspace".
    2.  Client emits `joinWorkspace` SocketIO event with `name`: "Target Workspace" and its valid `joining_code`.
*   **Expected Result:**
    *   Server receives the event.
    *   Server validates workspace existence.
    *   Server checks the `user.workspace_list` and finds the workspace ID already present.
    *   An `error` SocketIO event is emitted back to the joining user (via `request.sid`) with a message like "You have already joined the workspace!".
    *   `user.workspace_list` is not modified further.

## 3. List/Access Workspaces

**Test Case 3.1: Correct Listing of Joined Workspaces on Login/Page Load**
*   **Steps:**
    1.  User (who has previously created/joined multiple workspaces, e.g., "WS1", "WS2") logs in.
    2.  User navigates to the main chat page (`/chat`).
*   **Expected Result:**
    *   The `chat` view in `website/views.py` correctly parses `user.workspace_list` (e.g., "id1 id2 ").
    *   It fetches the corresponding `Workspace` objects from the database.
    *   The UI correctly lists all joined workspaces (e.g., "WS1", "WS2").

**Test Case 3.2: Correct Parsing of `workspace_list` with Potential Formatting Issues**
*   **Steps:**
    1.  Manually (or through a previous bug) set a user's `workspace_list` to something like " id1  id2 " (extra spaces) or "id3 " (trailing space is expected standard).
    2.  User logs in and navigates to `/chat`.
*   **Expected Result:**
    *   The `chat` view robustly parses the `workspace_list` (e.g., `wlist = [int(i) for i in user.workspace_list.split() if i]`).
    *   All valid workspace IDs are extracted, and corresponding workspaces are listed. No errors due to empty strings from `split()`.

**Test Case 3.3: Interaction with Workspaces (Channel & Name Display)**
*   **Steps:**
    1.  User is logged in and on the `/chat` page with multiple workspaces listed.
    2.  User clicks/selects a specific workspace from their list.
*   **Expected Result:**
    *   Client emits `getChannels` SocketIO event with the selected workspace's ID (`wid`). Server responds with `getChannelsJS` containing the list of channels for that workspace. UI updates to show these channels.
    *   Client emits `getWorkspaceName` SocketIO event with `wid`. Server responds with `changeWorkspaceName` containing the workspace `name` and `joining_id`. UI updates this information.

## 4. `workspace_list` Integrity

**Test Case 4.1: `workspace_list` Update - Create then Join**
*   **Steps:**
    1.  Authenticated user creates a new workspace "WS_Alpha". `user.workspace_list` becomes "ID_Alpha ".
    2.  Same user then joins an existing workspace "WS_Beta" (ID_Beta).
*   **Expected Result:**
    *   `user.workspace_list` in the database is updated to "ID_Alpha ID_Beta ".
    *   The UI reflects both workspaces.

**Test Case 4.2: `workspace_list` Update - Initially Empty**
*   **Steps:**
    1.  A new user signs up. Their `user.workspace_list` is initially empty or `None`.
    2.  User creates a new workspace "WS_First".
*   **Expected Result:**
    *   `user.workspace_list` in the database is updated to "ID_First ".

**Test Case 4.3: `workspace_list` Update - Joining First Workspace**
*   **Steps:**
    1.  A new user signs up. Their `user.workspace_list` is initially empty or `None`.
    2.  User joins an existing workspace "WS_Join".
*   **Expected Result:**
    *   `user.workspace_list` in the database is updated to "ID_Join ".

## 5. Joining Code
**Test Case 5.1: Joining Code Generation**
*   **Steps:**
    1. Authenticated user creates a new workspace.
*   **Expected Result:**
    *   A joining code is generated.
    *   The joining code consists of 4 letters and 2 digits.
    *   The joining code is associated with the workspace.

(Note on Joining Code Randomness: The current `random_string(4,2)` function provides limited permutations. This is noted as a potential future improvement area if more robust uniqueness/security for joining codes is required, but not a bug for current scope unless collisions become frequent.)
