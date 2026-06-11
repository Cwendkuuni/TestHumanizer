@Test(timeout = 4000)
  public void test0()  throws Throwable  {
      FSPathExplorer fSPathExplorer0 = new FSPathExplorer();
      assertNotNull(fSPathExplorer0);
      
      // Undeclared exception!
      try { 
        fSPathExplorer0.start();
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
      }
  }

  @Test(timeout = 4000)
  public void test1()  throws Throwable  {
      FSPathExplorer.showWelcome();
  }

  @Test(timeout = 4000)
  public void test2()  throws Throwable  {
      FSPathExplorer.showHelp();
  }

  @Test(timeout = 4000)
  public void test3()  throws Throwable  {
      FSPathExplorer fSPathExplorer0 = new FSPathExplorer();
      assertNotNull(fSPathExplorer0);
      
      fSPathExplorer0.createFSPath();
  }

  @Test(timeout = 4000)
  public void test4()  throws Throwable  {
      FSPathExplorer fSPathExplorer0 = new FSPathExplorer();
      assertNotNull(fSPathExplorer0);
      
      String[] stringArray0 = new String[8];
      // Undeclared exception!
      try { 
        fSPathExplorer0.configureExplorer(stringArray0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
      }
  }

  @Test(timeout = 4000)
  public void test5()  throws Throwable  {
      SystemInUtil.addInputLine("exit");
      String[] stringArray0 = new String[0];
      FSPathExplorer.main(stringArray0);
      assertEquals(0, stringArray0.length);
  }

  @Test(timeout = 4000)
  public void test6()  throws Throwable  {
      SystemInUtil.addInputLine("&");
      String[] stringArray0 = new String[9];
      stringArray0[0] = "-find";
      stringArray0[1] = "&";
      stringArray0[2] = "&";
      stringArray0[3] = "-find";
      stringArray0[4] = "-find";
      stringArray0[5] = "&";
      stringArray0[6] = "&";
      stringArray0[7] = "-find";
      stringArray0[8] = "&";
      // Undeclared exception!
      FSPathExplorer.main(stringArray0);
  }

  @Test(timeout = 4000)
  public void test7()  throws Throwable  {
      String[] stringArray0 = new String[6];
      stringArray0[0] = "xd!PFUOBAm:MDC>Ho";
      stringArray0[1] = "-p";
      stringArray0[2] = "o";
      stringArray0[3] = "F}=%q G+j/omzB7!w";
      stringArray0[4] = "-p";
      stringArray0[5] = "o";
      // Undeclared exception!
      try { 
        FSPathExplorer.main(stringArray0);
        fail("Expecting exception: InstantiationError");
      
      } catch(InstantiationError e) {
         //
         // the java.io.File specified must be a Directory
         //
         verifyException("net.sf.sugar.fspath.DefaultFSPath", e);
      }
  }

  @Test(timeout = 4000)
  public void test8()  throws Throwable  {
      String[] stringArray0 = new String[7];
      stringArray0[0] = "path";
      stringArray0[1] = "path";
      stringArray0[2] = "-p";
      stringArray0[3] = "-path";
      // Undeclared exception!
      try { 
        FSPathExplorer.main(stringArray0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
      }
  }

  @Test(timeout = 4000)
  public void test9()  throws Throwable  {
      SystemInUtil.addInputLine("help");
      String[] stringArray0 = new String[2];
      stringArray0[0] = "";
      stringArray0[1] = "";
      // Undeclared exception!
      FSPathExplorer.main(stringArray0);
  }