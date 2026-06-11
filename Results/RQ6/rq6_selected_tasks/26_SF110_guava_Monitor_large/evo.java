@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      Monitor monitor0 = new Monitor();
      TimeUnit timeUnit0 = TimeUnit.MILLISECONDS;
      // Undeclared exception!
      try { 
        monitor0.waitForUninterruptibly((Monitor.Guard) null, 0L, timeUnit0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.util.concurrent.Monitor", e);
      }
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      Monitor monitor0 = new Monitor();
      // Undeclared exception!
      try { 
        monitor0.waitForUninterruptibly((Monitor.Guard) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.util.concurrent.Monitor", e);
      }
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      Monitor monitor0 = new Monitor(true);
      TimeUnit timeUnit0 = TimeUnit.SECONDS;
      // Undeclared exception!
      try { 
        monitor0.waitFor((Monitor.Guard) null, 202L, timeUnit0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.util.concurrent.Monitor", e);
      }
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      Monitor monitor0 = new Monitor(true);
      // Undeclared exception!
      try { 
        monitor0.waitFor((Monitor.Guard) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.util.concurrent.Monitor", e);
      }
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      Monitor monitor0 = new Monitor();
      // Undeclared exception!
      try { 
        monitor0.tryEnterIf((Monitor.Guard) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.util.concurrent.Monitor", e);
      }
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      Monitor monitor0 = new Monitor(false);
      // Undeclared exception!
      try { 
        monitor0.hasWaiters((Monitor.Guard) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.util.concurrent.Monitor", e);
      }
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      Monitor monitor0 = new Monitor(false);
      TimeUnit timeUnit0 = TimeUnit.HOURS;
      // Undeclared exception!
      try { 
        monitor0.enterWhenUninterruptibly((Monitor.Guard) null, (-1897L), timeUnit0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.util.concurrent.Monitor", e);
      }
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      Monitor monitor0 = new Monitor();
      // Undeclared exception!
      try { 
        monitor0.enterWhenUninterruptibly((Monitor.Guard) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.util.concurrent.Monitor", e);
      }
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      Monitor monitor0 = new Monitor();
      TimeUnit timeUnit0 = TimeUnit.NANOSECONDS;
      // Undeclared exception!
      try { 
        monitor0.enterWhen((Monitor.Guard) null, 0L, timeUnit0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.util.concurrent.Monitor", e);
      }
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      Monitor monitor0 = new Monitor();
      // Undeclared exception!
      try { 
        monitor0.enterWhen((Monitor.Guard) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.util.concurrent.Monitor", e);
      }
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      Monitor monitor0 = new Monitor();
      TimeUnit timeUnit0 = TimeUnit.HOURS;
      // Undeclared exception!
      try { 
        monitor0.enterIfInterruptibly((Monitor.Guard) null, 690L, timeUnit0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.util.concurrent.Monitor", e);
      }
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      Monitor monitor0 = new Monitor();
      // Undeclared exception!
      try { 
        monitor0.enterIfInterruptibly((Monitor.Guard) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.util.concurrent.Monitor", e);
      }
  }

  @Test(timeout = 4000)
  public void test12()  throws Throwable  {
      Monitor monitor0 = new Monitor(true);
      TimeUnit timeUnit0 = TimeUnit.MICROSECONDS;
      // Undeclared exception!
      try { 
        monitor0.enterIf((Monitor.Guard) null, (long) 2, timeUnit0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.util.concurrent.Monitor", e);
      }
  }

  @Test(timeout = 4000)
  public void test13()  throws Throwable  {
      Monitor monitor0 = new Monitor();
      // Undeclared exception!
      try { 
        monitor0.enterIf((Monitor.Guard) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.util.concurrent.Monitor", e);
      }
  }

  @Test(timeout = 4000)
  public void test14()  throws Throwable  {
      Monitor monitor0 = new Monitor();
      TimeUnit timeUnit0 = TimeUnit.NANOSECONDS;
      monitor0.enterInterruptibly(0L, timeUnit0);
      monitor0.leave();
      assertFalse(monitor0.isFair());
  }

  @Test(timeout = 4000)
  public void test15()  throws Throwable  {
      Monitor monitor0 = new Monitor(false);
      TimeUnit timeUnit0 = TimeUnit.HOURS;
      boolean boolean0 = monitor0.enter((long) 0, timeUnit0);
      assertTrue(boolean0);
      assertFalse(monitor0.isFair());
  }

  @Test(timeout = 4000)
  public void test16()  throws Throwable  {
      Monitor monitor0 = new Monitor(true);
      TimeUnit timeUnit0 = TimeUnit.MICROSECONDS;
      monitor0.enter((-1L), timeUnit0);
      assertTrue(monitor0.isFair());
  }

  @Test(timeout = 4000)
  public void test17()  throws Throwable  {
      Monitor monitor0 = new Monitor(false);
      monitor0.tryEnter();
      monitor0.enter();
      monitor0.leave();
      assertFalse(monitor0.isFair());
  }

  @Test(timeout = 4000)
  public void test18()  throws Throwable  {
      Monitor monitor0 = new Monitor();
      boolean boolean0 = monitor0.isFair();
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test19()  throws Throwable  {
      Monitor monitor0 = new Monitor(false);
      monitor0.isOccupiedByCurrentThread();
      assertFalse(monitor0.isFair());
  }

  @Test(timeout = 4000)
  public void test20()  throws Throwable  {
      Monitor monitor0 = new Monitor(true);
      monitor0.enterInterruptibly();
      assertTrue(monitor0.isFair());
  }

  @Test(timeout = 4000)
  public void test21()  throws Throwable  {
      Monitor monitor0 = new Monitor(false);
      monitor0.hasQueuedThreads();
      assertFalse(monitor0.isFair());
  }

  @Test(timeout = 4000)
  public void test22()  throws Throwable  {
      Monitor monitor0 = new Monitor(false);
      monitor0.isOccupied();
      assertFalse(monitor0.isFair());
  }

  @Test(timeout = 4000)
  public void test23()  throws Throwable  {
      Monitor monitor0 = new Monitor(false);
      monitor0.getOccupiedDepth();
      assertFalse(monitor0.isFair());
  }

  @Test(timeout = 4000)
  public void test24()  throws Throwable  {
      Monitor monitor0 = new Monitor();
      Thread thread0 = MockThread.currentThread();
      monitor0.hasQueuedThread(thread0);
      assertFalse(monitor0.isFair());
  }

  @Test(timeout = 4000)
  public void test25()  throws Throwable  {
      Monitor monitor0 = new Monitor(false);
      monitor0.getQueueLength();
      assertFalse(monitor0.isFair());
  }