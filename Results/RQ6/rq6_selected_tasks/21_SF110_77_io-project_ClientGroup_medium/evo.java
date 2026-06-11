@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      Iterator<Client> iterator0 = clientGroup0.iterator();
      assertNotNull(iterator0);
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      boolean boolean0 = clientGroup0.contains((Client) null);
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      AlwaysFailMessageHandler alwaysFailMessageHandler0 = new AlwaysFailMessageHandler();
      MessageMultiplexer messageMultiplexer0 = new MessageMultiplexer(alwaysFailMessageHandler0);
      ClientHandler clientHandler0 = mock(ClientHandler.class, new ViolatedAssumptionAnswer());
      ClientToMessageHandlerAdapter clientToMessageHandlerAdapter0 = new ClientToMessageHandlerAdapter(messageMultiplexer0, clientHandler0);
      clientGroup0.addClientHandler(clientToMessageHandlerAdapter0);
      boolean boolean0 = clientGroup0.remove((Client) null);
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      clientGroup0.add((Client) null);
      clientGroup0.createSubGroup();
      assertEquals(1, clientGroup0.size());
      
      boolean boolean0 = clientGroup0.remove((Client) null);
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      ClientGroup clientGroup1 = new ClientGroup(clientGroup0);
      boolean boolean0 = clientGroup1.add((Client) null);
      assertEquals(0, clientGroup1.size());
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      AlwaysFailMessageHandler alwaysFailMessageHandler0 = new AlwaysFailMessageHandler();
      MessageMultiplexer messageMultiplexer0 = new MessageMultiplexer(alwaysFailMessageHandler0);
      ClientHandler clientHandler0 = mock(ClientHandler.class, new ViolatedAssumptionAnswer());
      ClientToMessageHandlerAdapter clientToMessageHandlerAdapter0 = new ClientToMessageHandlerAdapter(messageMultiplexer0, clientHandler0);
      clientGroup0.addClientHandler(clientToMessageHandlerAdapter0);
      clientGroup0.add((Client) null);
      MockThrowable mockThrowable0 = new MockThrowable();
      boolean boolean0 = clientGroup0.notifyExceptionCaught((Client) null, mockThrowable0);
      assertEquals(1, clientGroup0.size());
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      clientGroup0.add((Client) null);
      ClientGroup clientGroup1 = clientGroup0.createSubGroup();
      MockThrowable mockThrowable0 = new MockThrowable();
      clientGroup1.add((Client) null);
      clientGroup0.createSubGroup();
      boolean boolean0 = clientGroup0.notifyExceptionCaught((Client) null, mockThrowable0);
      assertEquals(1, clientGroup0.size());
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      clientGroup0.add((Client) null);
      clientGroup0.createSubGroup();
      MockThrowable mockThrowable0 = new MockThrowable();
      boolean boolean0 = clientGroup0.notifyExceptionCaught((Client) null, mockThrowable0);
      assertEquals(1, clientGroup0.size());
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      AlwaysFailMessageHandler alwaysFailMessageHandler0 = new AlwaysFailMessageHandler();
      ClientHandler clientHandler0 = mock(ClientHandler.class, new ViolatedAssumptionAnswer());
      ClientToMessageHandlerAdapter clientToMessageHandlerAdapter0 = new ClientToMessageHandlerAdapter(alwaysFailMessageHandler0, clientHandler0);
      clientGroup0.addClientHandler(clientToMessageHandlerAdapter0);
      clientGroup0.add((Client) null);
      // Undeclared exception!
      try { 
        clientGroup0.notifyMessageReceived((Client) null, (Object) null);
        fail("Expecting exception: AssertionError");
      
      } catch(AssertionError e) {
         //
         // Method called with the following arguments: null (node), null (message).
         //
      }
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      clientGroup0.add((Client) null);
      ClientGroup clientGroup1 = clientGroup0.createSubGroup();
      clientGroup1.add((Client) null);
      clientGroup0.createSubGroup();
      Locale locale0 = Locale.SIMPLIFIED_CHINESE;
      boolean boolean0 = clientGroup0.notifyMessageReceived((Client) null, locale0);
      assertEquals(1, clientGroup0.size());
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      clientGroup0.add((Client) null);
      clientGroup0.createSubGroup();
      Locale locale0 = Locale.SIMPLIFIED_CHINESE;
      boolean boolean0 = clientGroup0.notifyMessageReceived((Client) null, locale0);
      assertEquals(1, clientGroup0.size());
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      MessageMultiplexer messageMultiplexer0 = new MessageMultiplexer((MessageHandler) null);
      ClientHandler clientHandler0 = mock(ClientHandler.class, new ViolatedAssumptionAnswer());
      ClientToMessageHandlerAdapter clientToMessageHandlerAdapter0 = new ClientToMessageHandlerAdapter(messageMultiplexer0, clientHandler0);
      clientGroup0.addClientHandler(clientToMessageHandlerAdapter0);
      clientGroup0.add((Client) null);
      // Undeclared exception!
      try { 
        clientGroup0.notifyMessageSent((Client) null, (Object) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("ioproject.common.network.MessageMultiplexer", e);
      }
  }

  @Test(timeout = 4000)
  public void test12()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      clientGroup0.add((Client) null);
      ClientGroup clientGroup1 = clientGroup0.createSubGroup();
      clientGroup1.add((Client) null);
      clientGroup0.createSubGroup();
      Object object0 = new Object();
      boolean boolean0 = clientGroup0.notifyMessageSent((Client) null, object0);
      assertEquals(1, clientGroup0.size());
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test13()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      clientGroup0.add((Client) null);
      clientGroup0.createSubGroup();
      Object object0 = new Object();
      boolean boolean0 = clientGroup0.notifyMessageSent((Client) null, object0);
      assertEquals(1, clientGroup0.size());
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test14()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      ClientGroup clientGroup1 = clientGroup0.parentGroup();
      assertNull(clientGroup1);
  }

  @Test(timeout = 4000)
  public void test15()  throws Throwable  {
      ClientGroup clientGroup0 = new ClientGroup((ClientGroup) null);
      int int0 = clientGroup0.size();
      assertEquals(0, int0);
  }