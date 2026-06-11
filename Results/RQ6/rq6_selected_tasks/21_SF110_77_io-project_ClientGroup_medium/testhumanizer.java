@Test(timeout = 4000)
    public void testRemoveNullClientWithoutHandler() throws Throwable {
        // Given: A ClientGroup with a ClientToMessageHandlerAdapter
        ClientGroup clientGroup = new ClientGroup(null);
        AlwaysFailMessageHandler alwaysFailMessageHandler = new AlwaysFailMessageHandler();
        ClientHandler clientHandler = mock(ClientHandler.class, new ViolatedAssumptionAnswer());
        ClientToMessageHandlerAdapter handlerAdapter = new ClientToMessageHandlerAdapter(alwaysFailMessageHandler, clientHandler);
        clientGroup.addClientHandler(handlerAdapter);

        // When: Removing a null client
        boolean result = clientGroup.remove(null);

        // Then: The removal should return false
        assertFalse("Expected removal of null client to return false", result);
    }

    @Test(timeout = 4000)
    public void testAddAndRemoveNullClient() throws Throwable {
        // Given: A ClientGroup with a null client added
        ClientGroup clientGroup = new ClientGroup(null);
        clientGroup.add(null);
        clientGroup.createSubGroup();

        // When: Removing the null client
        boolean result = clientGroup.remove(null);

        // Then: The removal should return true and size should be 1
        assertTrue("Expected removal of null client to return true", result);
        assertEquals("Expected size to be 1 after adding and removing null client", 1, clientGroup.size());
    }

    @Test(timeout = 4000)
    public void testAddNullClientWithHandler() throws Throwable {
        // Given: A ClientGroup with a ClientToMessageHandlerAdapter
        ClientGroup clientGroup = new ClientGroup(null);
        ClientHandler clientHandler = mock(ClientHandler.class, new ViolatedAssumptionAnswer());
        ClientToMessageHandlerAdapter handlerAdapter = new ClientToMessageHandlerAdapter(null, clientHandler);
        clientGroup.addClientHandler(handlerAdapter);

        // When: Adding a null client
        boolean result = clientGroup.add(null);

        // Then: The addition should return true and size should be 1
        assertTrue("Expected addition of null client to return true", result);
        assertEquals("Expected size to be 1 after adding null client", 1, clientGroup.size());
    }

    @Test(timeout = 4000)
    public void testAddNullClientToSubGroup() throws Throwable {
        // Given: A ClientGroup with a parent group
        ClientGroup parentGroup = new ClientGroup(null);
        ClientGroup clientGroup = new ClientGroup(parentGroup);

        // When: Adding a null client to the subgroup
        boolean result = clientGroup.add(null);

        // Then: The addition should return false and size should be 0
        assertFalse("Expected addition of null client to return false", result);
        assertEquals("Expected size to be 0 after adding null client", 0, clientGroup.size());
    }

    @Test(timeout = 4000)
    public void testContainsNullClient() throws Throwable {
        // Given: A ClientGroup
        ClientGroup clientGroup = new ClientGroup(null);

        // When: Checking if it contains a null client
        boolean result = clientGroup.contains(null);

        // Then: The result should be false
        assertFalse("Expected contains(null) to return false", result);
    }

    @Test(timeout = 4000)
    public void testNotifyExceptionCaughtWithNullClient() throws Throwable {
        // Given: A ClientGroup with a ClientToMessageHandlerAdapter
        ClientGroup clientGroup = new ClientGroup(null);
        clientGroup.add(null);
        AlwaysFailMessageHandler alwaysFailMessageHandler = new AlwaysFailMessageHandler();
        MessageMultiplexer messageMultiplexer = new MessageMultiplexer(alwaysFailMessageHandler);
        ClientToMessageHandlerAdapter handlerAdapter = new ClientToMessageHandlerAdapter(messageMultiplexer, null);
        clientGroup.addClientHandler(handlerAdapter);
        MockThrowable mockThrowable = new MockThrowable("", null);

        // When: Notifying an exception caught with a null client
        // Then: Expect a NullPointerException
        try {
            clientGroup.notifyExceptionCaught(null, mockThrowable);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testNotifyExceptionCaughtWithNullThrowable() throws Throwable {
        // Given: A ClientGroup with a null client added
        ClientGroup clientGroup = new ClientGroup(null);
        clientGroup.add(null);
        ClientGroup subGroup = clientGroup.createSubGroup();
        subGroup.add(null);
        clientGroup.createSubGroup();

        // When: Notifying an exception caught with a null throwable
        boolean result = clientGroup.notifyExceptionCaught(null, null);

        // Then: The notification should return true and size should be 1
        assertTrue("Expected notifyExceptionCaught to return true", result);
        assertEquals("Expected size to be 1 after notifying exception", 1, clientGroup.size());
    }

    @Test(timeout = 4000)
    public void testNotifyMessageReceivedWithNullClient() throws Throwable {
        // Given: A ClientGroup with a ClientToMessageHandlerAdapter
        ClientGroup clientGroup = new ClientGroup(null);
        clientGroup.add(null);
        AlwaysFailMessageHandler alwaysFailMessageHandler = new AlwaysFailMessageHandler();
        MessageMultiplexer messageMultiplexer = new MessageMultiplexer(alwaysFailMessageHandler);
        ClientHandler clientHandler = mock(ClientHandler.class, new ViolatedAssumptionAnswer());
        ClientToMessageHandlerAdapter handlerAdapter = new ClientToMessageHandlerAdapter(messageMultiplexer, clientHandler);
        clientGroup.addClientHandler(handlerAdapter);

        // When: Notifying a message received with a null client
        // Then: Expect a NullPointerException
        try {
            clientGroup.notifyMessageReceived(null, null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testNotifyMessageReceivedWithWeakReference() throws Throwable {
        // Given: A ClientGroup with a null client added
        ClientGroup clientGroup = new ClientGroup(null);
        clientGroup.add(null);
        ClientGroup subGroup = clientGroup.createSubGroup();
        subGroup.add(null);
        clientGroup.createSubGroup();
        ReferenceQueue<ClientGroup> referenceQueue = new ReferenceQueue<>();
        WeakReference<ClientGroup> weakReference = new WeakReference<>(null, referenceQueue);
        WeakReference<Object> weakReferenceObject = new WeakReference<>(weakReference);

        // When: Notifying a message received with a weak reference
        boolean result = clientGroup.notifyMessageReceived(null, weakReferenceObject);

        // Then: The notification should return true and size should be 1
        assertTrue("Expected notifyMessageReceived to return true", result);
        assertEquals("Expected size to be 1 after notifying message received", 1, clientGroup.size());
    }

    @Test(timeout = 4000)
    public void testNotifyMessageSentWithNullClient() throws Throwable {
        // Given: A ClientGroup with a ClientToMessageHandlerAdapter
        ClientGroup clientGroup = new ClientGroup(null);
        clientGroup.add(null);
        AlwaysFailMessageHandler alwaysFailMessageHandler = new AlwaysFailMessageHandler();
        MessageMultiplexer messageMultiplexer = new MessageMultiplexer(alwaysFailMessageHandler);
        ClientToMessageHandlerAdapter handlerAdapter = new ClientToMessageHandlerAdapter(messageMultiplexer, null);
        clientGroup.addClientHandler(handlerAdapter);

        // When: Notifying a message sent with a null client
        // Then: Expect a NullPointerException
        try {
            clientGroup.notifyMessageSent(null, null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testNotifyMessageSentWithNullObject() throws Throwable {
        // Given: A ClientGroup with a null client added
        ClientGroup clientGroup = new ClientGroup(null);
        clientGroup.add(null);
        ClientGroup subGroup = clientGroup.createSubGroup();
        subGroup.add(null);
        clientGroup.createSubGroup();

        // When: Notifying a message sent with a null object
        boolean result = clientGroup.notifyMessageSent(null, null);

        // Then: The notification should return true and size should be 1
        assertTrue("Expected notifyMessageSent to return true", result);
        assertEquals("Expected size to be 1 after notifying message sent", 1, clientGroup.size());
    }

    @Test(timeout = 4000)
    public void testIteratorNotNull() throws Throwable {
        // Given: A ClientGroup
        ClientGroup clientGroup = new ClientGroup(null);

        // When: Getting the iterator
        Iterator<Client> iterator = clientGroup.iterator();

        // Then: The iterator should not be null
        assertNotNull("Expected iterator to be not null", iterator);
    }

    @Test(timeout = 4000)
    public void testParentGroupIsNull() throws Throwable {
        // Given: A ClientGroup
        ClientGroup clientGroup = new ClientGroup(null);

        // When: Getting the parent group
        ClientGroup parentGroup = clientGroup.parentGroup();

        // Then: The parent group should be null
        assertNull("Expected parent group to be null", parentGroup);
    }

    @Test(timeout = 4000)
    public void testInitialSizeIsZero() throws Throwable {
        // Given: A ClientGroup
        ClientGroup clientGroup = new ClientGroup(null);

        // When: Getting the size
        int size = clientGroup.size();

        // Then: The size should be zero
        assertEquals("Expected initial size to be zero", 0, size);
    }