@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      Locale locale0 = Locale.US;
      HashMap<Object, MessageFormat> hashMap0 = new HashMap<Object, MessageFormat>();
      ExtendedMessageFormat extendedMessageFormat0 = new ExtendedMessageFormat("q3y~XNh}Q", locale0, hashMap0);
      extendedMessageFormat0.applyPattern("q3y~XNh}Q");
      assertEquals("q3y~XNh}Q", extendedMessageFormat0.toPattern());
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      Locale locale0 = Locale.UK;
      ExtendedMessageFormat extendedMessageFormat0 = new ExtendedMessageFormat(">iV~<32*I4]=!1X,", locale0);
      assertEquals(">iV~<32*I4]=!1X,", extendedMessageFormat0.toPattern());
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      HashMap<Object, Object> hashMap0 = new HashMap<Object, Object>();
      ExtendedMessageFormat extendedMessageFormat0 = new ExtendedMessageFormat(": ", hashMap0);
      assertEquals(": ", extendedMessageFormat0.toPattern());
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      Locale locale0 = Locale.GERMANY;
      HashMap<String, Object> hashMap0 = new HashMap<String, Object>();
      ExtendedMessageFormat extendedMessageFormat0 = null;
      try {
        extendedMessageFormat0 = new ExtendedMessageFormat("{}|R)tKxS.=w8J", locale0, hashMap0);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // Invalid format argument index at position 1: }
         //
         verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
      }
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      Locale locale0 = Locale.ITALIAN;
      HashMap<Object, String> hashMap0 = new HashMap<Object, String>();
      ExtendedMessageFormat extendedMessageFormat0 = null;
      try {
        extendedMessageFormat0 = new ExtendedMessageFormat("?9}byOLth9rLb{4", locale0, hashMap0);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // Unterminated format element at position 15
         //
         verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
      }
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      HashMap<String, Object> hashMap0 = new HashMap<String, Object>();
      ExtendedMessageFormat extendedMessageFormat0 = new ExtendedMessageFormat("''", hashMap0);
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      ExtendedMessageFormat extendedMessageFormat0 = new ExtendedMessageFormat("");
      DateFormat dateFormat0 = DateFormat.getDateTimeInstance();
      // Undeclared exception!
      try { 
        extendedMessageFormat0.setFormatByArgumentIndex(1738, dateFormat0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
      }
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      ExtendedMessageFormat extendedMessageFormat0 = new ExtendedMessageFormat("Unterminated format element at position ");
      // Undeclared exception!
      try { 
        extendedMessageFormat0.setFormats((Format[]) null);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
      }
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      HashMap<Locale.LanguageRange, Object> hashMap0 = new HashMap<Locale.LanguageRange, Object>();
      ExtendedMessageFormat extendedMessageFormat0 = null;
      try {
        extendedMessageFormat0 = new ExtendedMessageFormat("X}mBS],{,t", hashMap0);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // Invalid format argument index at position 8: ,
         //
         verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
      }
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      ExtendedMessageFormat extendedMessageFormat0 = new ExtendedMessageFormat("orJ.apache.commons.lang.text.StTMatcher");
      DecimalFormat decimalFormat0 = new DecimalFormat();
      // Undeclared exception!
      try { 
        extendedMessageFormat0.setFormat(38, decimalFormat0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
      }
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      ExtendedMessageFormat extendedMessageFormat0 = new ExtendedMessageFormat("");
      // Undeclared exception!
      try { 
        extendedMessageFormat0.setFormatsByArgumentIndex((Format[]) null);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
      }
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      Locale locale0 = Locale.US;
      HashMap<Object, MessageFormat> hashMap0 = new HashMap<Object, MessageFormat>();
      ExtendedMessageFormat extendedMessageFormat0 = new ExtendedMessageFormat("q3y~XNh}Q", locale0, hashMap0);
      String string0 = extendedMessageFormat0.toPattern();
      assertEquals("q3y~XNh}Q", string0);
  }