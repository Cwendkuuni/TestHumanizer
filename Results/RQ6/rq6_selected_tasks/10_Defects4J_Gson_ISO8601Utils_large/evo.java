@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      ParsePosition parsePosition0 = new ParsePosition(5);
      try { 
        ISO8601Utils.parse("1969-12-31T23:51:42Z", parsePosition0);
        fail("Expecting exception: ParseException");
      
      } catch(ParseException e) {
         //
         // Failed to parse date [\"1969-12-31T23:51:42Z']: Invalid number: 12-3
         //
         verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
      }
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      ParsePosition parsePosition0 = new ParsePosition(1);
      try { 
        ISO8601Utils.parse("6J (bRI~Q/H", parsePosition0);
        fail("Expecting exception: ParseException");
      
      } catch(ParseException e) {
         //
         // Failed to parse date [\"6J (bRI~Q/H']: Invalid number: J (b
         //
         verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
      }
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      ParsePosition parsePosition0 = new ParsePosition(2147483645);
      try { 
        ISO8601Utils.parse("hS.", parsePosition0);
        fail("Expecting exception: ParseException");
      
      } catch(ParseException e) {
         //
         // Failed to parse date [\"hS.']: hS.
         //
         verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
      }
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      ParsePosition parsePosition0 = new ParsePosition(1);
      try { 
        ISO8601Utils.parse("+0000", parsePosition0);
        fail("Expecting exception: ParseException");
      
      } catch(ParseException e) {
         //
         // Failed to parse date [\"+0000']: +0000
         //
         verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
      }
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      ParsePosition parsePosition0 = new ParsePosition((-20));
      try { 
        ISO8601Utils.parse("", parsePosition0);
        fail("Expecting exception: ParseException");
      
      } catch(ParseException e) {
         //
         // Failed to parse date [\"']: (java.lang.NumberFormatException)
         //
         verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
      }
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      ParsePosition parsePosition0 = new ParsePosition((-1781));
      try { 
        ISO8601Utils.parse((String) null, parsePosition0);
        fail("Expecting exception: ParseException");
      
      } catch(ParseException e) {
         //
         // Failed to parse date [null]: (java.lang.NumberFormatException)
         //
         verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
      }
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      ParsePosition parsePosition0 = new ParsePosition(0);
      Date date0 = ISO8601Utils.parse("2014-02-14T20:21:21Z", parsePosition0);
      assertEquals("Fri Feb 14 20:21:21 GMT 2014", date0.toString());
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      ParsePosition parsePosition0 = new ParsePosition(0);
      try { 
        ISO8601Utils.parse("209019154-06-21T19:17:34Z", parsePosition0);
        fail("Expecting exception: ParseException");
      
      } catch(ParseException e) {
         //
         // Failed to parse date [\"209019154-06-21T19:17:34Z']: Invalid time zone indicator '4'
         //
         verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
      }
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      ParsePosition parsePosition0 = new ParsePosition(0);
      Date date0 = ISO8601Utils.parse("2014-02-14T20:21:21.320Z", parsePosition0);
      assertEquals("Fri Feb 14 20:21:21 GMT 2014", date0.toString());
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      ParsePosition parsePosition0 = new ParsePosition(3);
      try { 
        ISO8601Utils.parse("209019154-06-21T19:17:34Z", parsePosition0);
        fail("Expecting exception: ParseException");
      
      } catch(ParseException e) {
         //
         // Failed to parse date [\"209019154-06-21T19:17:34Z']: Mismatching time zone indicator: GMT-21T19:17:34Z given, resolves to GMT
         //
         verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
      }
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      MockDate mockDate0 = new MockDate();
      SimpleTimeZone simpleTimeZone0 = new SimpleTimeZone((-900), "U\"36PY:H?exL");
      String string0 = ISO8601Utils.format((Date) mockDate0, true, (TimeZone) simpleTimeZone0);
      assertEquals("2014-02-14T20:21:20.420-00:00", string0);
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      MockDate mockDate0 = new MockDate((-671), 2012, 1, (-671), 2012, (-671));
      SimpleTimeZone simpleTimeZone0 = new SimpleTimeZone(2244, "p21$V^");
      String string0 = ISO8601Utils.format((Date) mockDate0, false, (TimeZone) simpleTimeZone0);
      assertEquals("1396-08-05T10:20:51+00:00", string0);
  }

  @Test(timeout = 4000)
  public void test12()  throws Throwable  {
      MockDate mockDate0 = new MockDate();
      String string0 = ISO8601Utils.format((Date) mockDate0, true);
      assertEquals("2014-02-14T20:21:21.320Z", string0);
  }

  @Test(timeout = 4000)
  public void test13()  throws Throwable  {
      ISO8601Utils iSO8601Utils0 = new ISO8601Utils();
  }

  @Test(timeout = 4000)
  public void test14()  throws Throwable  {
      MockDate mockDate0 = new MockDate(0, (-824), 0, (-824), 0, 0);
      String string0 = ISO8601Utils.format((Date) mockDate0);
      assertEquals("1831-03-26T16:00:00Z", string0);
  }