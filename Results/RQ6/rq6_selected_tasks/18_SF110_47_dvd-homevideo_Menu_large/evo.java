@Test(timeout = 4000)
  public void test0()  throws Throwable  {
      Menu menu0 = new Menu();
      // Undeclared exception!
      try { 
        menu0.DVDMainMenu();
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("Menu", e);
      }
  }

  @Test(timeout = 4000)
  public void test1()  throws Throwable  {
      Menu menu0 = new Menu();
      // Undeclared exception!
      try { 
        menu0.init();
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("Menu", e);
      }
  }

  @Test(timeout = 4000)
  public void test2()  throws Throwable  {
      Menu menu0 = new Menu();
      menu0.m_Error = true;
      boolean boolean0 = menu0.init();
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test3()  throws Throwable  {
      Menu menu0 = new Menu("\t</JTextField>", "IO Error in WriteProjectProperties in GUI.java\n", "IO Error in WriteProjectProperties in GUI.java\n", "", true, (GUI) null);
      // Undeclared exception!
      try { 
        menu0.createXML();
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("Menu", e);
      }
  }

  @Test(timeout = 4000)
  public void test4()  throws Throwable  {
      Menu menu0 = new Menu("", "GvkhxmkdjJ#9s]Bp", true, (GUI) null);
      assertTrue(menu0.pal_menu);
  }

  @Test(timeout = 4000)
  public void test5()  throws Throwable  {
      Menu menu0 = new Menu();
      // Undeclared exception!
      try { 
        menu0.run();
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("Menu", e);
      }
  }