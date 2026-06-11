@Test(timeout = 4000)
  public void test0()  throws Throwable  {
      TabbedPane tabbedPane0 = null;
      try {
        tabbedPane0 = new TabbedPane((FollowAppAttributes) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("ghm.follow.gui.TabbedPane", e);
      }
  }