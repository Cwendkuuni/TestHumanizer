@Test(timeout = 4000)
  public void test0()  throws Throwable  {
      SessionProperties sessionProperties0 = new SessionProperties();
      DisplayableListPanel displayableListPanel0 = null;
      try {
        displayableListPanel0 = new DisplayableListPanel(sessionProperties0, (DisplayableListParentForm) null, "userInterfaceFactory", false, false);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("macaw.util.DisplayableListPanel", e);
      }
  }

  @Test(timeout = 4000)
  public void test1()  throws Throwable  {
      SessionProperties sessionProperties0 = new SessionProperties();
      DisplayableListPanel displayableListPanel0 = null;
      try {
        displayableListPanel0 = new DisplayableListPanel(sessionProperties0, (DisplayableListParentForm) null, "currentUser", false);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("macaw.util.DisplayableListPanel", e);
      }
  }