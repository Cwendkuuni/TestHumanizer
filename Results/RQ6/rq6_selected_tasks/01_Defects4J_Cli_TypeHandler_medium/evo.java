@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      URL uRL0 = TypeHandler.createURL((String) null);
      assertNull(uRL0);
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      // Undeclared exception!
      try { 
        TypeHandler.createNumber("t;^s{@9>8Zim77~Z{.=");
        fail("Expecting exception: NoClassDefFoundError");
      
      } catch(NoClassDefFoundError e) {
         //
         // org/apache/commons/lang/math/NumberUtils
         //
         verifyException("org.apache.commons.cli.TypeHandler", e);
      }
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      File[] fileArray0 = TypeHandler.createFiles("ro;U0");
      assertNull(fileArray0);
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      File file0 = TypeHandler.createFile("JXgsOs}+r");
      assertFalse(file0.exists());
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      Date date0 = TypeHandler.createDate("tcVL355A?EM<:O");
      assertNull(date0);
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      Class class0 = TypeHandler.createClass("");
      assertNull(class0);
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      Object object0 = TypeHandler.createObject("[J");
      assertNull(object0);
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      Object object0 = TypeHandler.createObject("");
      MockFile mockFile0 = (MockFile)TypeHandler.createValue("", ((PatternOptionBuilder) object0).FILE_VALUE);
      assertTrue(mockFile0.canExecute());
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      Object object0 = TypeHandler.createObject("org.apache.commons.cli.PatternOptionBuilder");
      Object object1 = TypeHandler.createValue("org.apache.commons.cli.PatternOptionBuilder", ((PatternOptionBuilder) object0).DATE_VALUE);
      assertNull(object1);
      assertEquals("org.apache.commons.cli.PatternOptionBuilder", object1);
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      Class<Object> class0 = Object.class;
      Object object0 = TypeHandler.createValue("", class0);
      assertNull(object0);
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      TypeHandler typeHandler0 = new TypeHandler();
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      Object object0 = TypeHandler.createObject("n");
      Object object1 = TypeHandler.createValue("n", ((PatternOptionBuilder) object0).FILES_VALUE);
      assertNull(object1);
  }

  @Test(timeout = 4000)
  public void test12()  throws Throwable  {
      Object object0 = TypeHandler.createObject("pnciC5r__!Yw`xqSfm");
      // Undeclared exception!
      try { 
        TypeHandler.createValue("pnciC5r__!Yw`xqSfm", ((PatternOptionBuilder) object0).NUMBER_VALUE);
        fail("Expecting exception: NoClassDefFoundError");
      
      } catch(NoClassDefFoundError e) {
         //
         // org/apache/commons/lang/math/NumberUtils
         //
         verifyException("org.apache.commons.cli.TypeHandler", e);
      }
  }

  @Test(timeout = 4000)
  public void test13()  throws Throwable  {
      Object object0 = TypeHandler.createObject("pnciC5r__!Yw`xqSfm");
      Object object1 = TypeHandler.createValue("g~l41<SA_", ((PatternOptionBuilder) object0).CLASS_VALUE);
      assertNull(object1);
  }

  @Test(timeout = 4000)
  public void test14()  throws Throwable  {
      Object object0 = TypeHandler.createValue("", (Object) null);
      assertNull(object0);
  }