# Channel Management Test Cases

## 1. Create Channel

**Test Case 1.1: Successful Channel Creation**
*   **Steps:**
    1.  Ensure the user is authenticated and is a member of "Workspace_A".
    2.  Client emits `createChannel` SocketIO event with `name`: "Announcements" and `wid`: (ID of "Workspace_A").
*   **Expected Result:**
    *   Server receives the event.
    *   A new `Channel` record is created in the database:
        *   `name` is "Announcements".
        *   `admin_username` is `current_user.name`.
        *   `wid` is the ID of "Workspace_A".
    *   A `createChannelJS` SocketIO event is broadcast to all users in the room for "Workspace_A" (`room.name`). The event data includes the new channel's `id`, `name`, `admin_username`, and `wid`.
    *   The new channel "Announcements" appears in the channel list UI for all members of "Workspace_A".

**Test Case 1.2: Create Channel with a Duplicate Name in the Same Workspace**
*   **Steps:**
    1.  User is authenticated and in "Workspace_A". "Workspace_A" already contains a channel named "General".
    2.  Client emits `createChannel` SocketIO event with `name`: "General" and `wid`: (ID of "Workspace_A").
*   **Expected Result:**
    *   A new channel record "General" is created in the database for "Workspace_A" (current system allows this, as uniqueness is typically by ID).
    *   The `createChannelJS` event is broadcast, and another "General" channel appears in the UI.
    *   (Note: Depending on desired behavior, a unique constraint on (name, wid) might be preferable in the database model to prevent this, but current code allows it.)

**Test Case 1.3: Attempt to Create Channel in a Non-existent Workspace**
*   **Steps:**
    1.  User is authenticated.
    2.  Client emits `createChannel` SocketIO event with `name`: "TestChannel" and `wid`: (ID of a non-existent workspace).
*   **Expected Result:**
    *   Server's `handle_createChannel` finds no `room` (Workspace object).
    *   An `error` SocketIO event is emitted back to the user (via `request.sid`) with a message like "Workspace not found for channel creation."
    *   No channel is created.

**Test Case 1.4: Attempt to Create Channel in a Workspace User is Not Part Of (Security Check - Conceptual)**
*   **Steps:**
    1.  User_A is authenticated but is NOT a member of "Workspace_Secret" (ID_Secret).
    2.  User_A crafts and emits a `createChannel` SocketIO event with `name`: "Infiltration" and `wid`: ID_Secret.
*   **Expected Result (Ideal & Hardened System):**
    *   The server should validate if `current_user` has rights to create a channel in `wid`. This check is NOT currently implemented in `handle_createChannel` but was noted as a hardening opportunity.
    *   If the check fails, an error message (e.g., "Not authorized to create channel in this workspace.") should be emitted to User_A. No channel created.
*   **Expected Result (Current System):**
    *   If the workspace ID_Secret exists, the channel "Infiltration" would be created under Workspace_Secret, with User_A as `admin_username`. This is because the current `handle_createChannel` only checks if the workspace itself exists, not if the `current_user` is a member of it.

**Test Case 1.5: Create Channel When Not Authenticated**
*   **Steps:**
    1.  User is not authenticated.
    2.  Client attempts to emit `createChannel` SocketIO event.
*   **Expected Result:**
    *   Action fails due to lack of authentication (e.g., `current_user` is AnonymousUserMixin).
    *   No channel created. Server might reject the event or the call to `current_user.name` would fail.

## 2. List/Access Channels

**Test Case 2.1: Correct Listing of Channels for a Workspace**
*   **Steps:**
    1.  User is authenticated and a member of "Workspace_A", which has channels "General" and "Random".
    2.  User selects "Workspace_A" in the UI.
*   **Expected Result:**
    *   Client emits `getChannels` SocketIO event with `wid`: (ID of "Workspace_A").
    *   Server's `sendChannels` handler queries and finds "General" and "Random".
    *   A `getChannelsJS` SocketIO event is received by the client, containing a list of channel objects (each with `id`, `name`, `admin_username`, `wid`) for "Workspace_A".
    *   The UI updates to display "General" and "Random" in the channel list.

**Test Case 2.2: Listing Channels for a Workspace with No Channels**
*   **Steps:**
    1.  User is authenticated and a member of "Workspace_B", which has no channels.
    2.  User selects "Workspace_B" in the UI.
*   **Expected Result:**
    *   Client emits `getChannels` for "Workspace_B".
    *   Server's `sendChannels` handler finds no channels for "Workspace_B".
    *   `getChannelsJS` event is received with an empty list for `channels` and `channelCount: 0`.
    *   The UI displays an empty channel list or an appropriate message (e.g., "No channels yet").

**Test Case 2.3: Initial Channel Load on Chat Page (`website/views.py - chat`)**
*   **Steps:**
    1.  User logs in. Their default (first) workspace in `user.workspace_list` is "Workspace_Default", which has channels "Welcome" and "Info".
*   **Expected Result:**
    *   The `chat` view in `website/views.py` correctly identifies "Workspace_Default".
    *   It fetches its channels ("Welcome", "Info").
    *   The initial page render includes these channels for "Workspace_Default".

## 3. Channel Data Integrity

**Test Case 3.1: Verify Channel Attributes**
*   **Steps:**
    1.  Create a channel "Tech Talk" in "Workspace_Dev" by User_Pat.
    2.  Retrieve this channel's data (either via `getChannels` or by inspecting the database).
*   **Expected Result:**
    *   The channel record has:
        *   `name`: "Tech Talk"
        *   `admin_username`: "User_Pat"
        *   `wid`: (ID of "Workspace_Dev")
        *   A unique `id` (primary key).
    *   These attributes are correctly reflected in data sent to the client.
