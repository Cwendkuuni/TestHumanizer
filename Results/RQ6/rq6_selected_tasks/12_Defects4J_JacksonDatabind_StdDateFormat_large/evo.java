@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      TimeZone timeZone0 = TimeZone.getDefault();
      Locale locale0 = Locale.CHINESE;
      StdDateFormat stdDateFormat0 = new StdDateFormat(timeZone0, locale0);
      ParsePosition parsePosition0 = new ParsePosition(1);
      stdDateFormat0.parseAsRFC1123("U.MZ5V?l<c!o", parsePosition0);
      assertEquals(1, parsePosition0.getErrorIndex());
      assertEquals("java.text.ParsePosition[index=1,errorIndex=1]", parsePosition0.toString());
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      StdDateFormat stdDateFormat0 = StdDateFormat.instance;
      boolean boolean0 = stdDateFormat0.looksLikeISO8601("6@|5_%vnVih'");
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      Locale locale0 = Locale.CHINA;
      MockSimpleDateFormat mockSimpleDateFormat0 = (MockSimpleDateFormat)StdDateFormat.getRFC1123Format((TimeZone) null, locale0);
      assertEquals("EEE, jj nnn aaaa HH:mm:ss zzz", mockSimpleDateFormat0.toLocalizedPattern());
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      TimeZone timeZone0 = TimeZone.getTimeZone("");
      Locale locale0 = Locale.KOREAN;
      MockSimpleDateFormat mockSimpleDateFormat0 = (MockSimpleDateFormat)StdDateFormat.getISO8601Format(timeZone0, locale0);
      assertEquals("yyyy-MM-dd'T'HH:mm:ss.SSSZ", mockSimpleDateFormat0.toPattern());
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      ZoneOffset zoneOffset0 = ZoneOffset.ofTotalSeconds((-2592));
      TimeZone timeZone0 = TimeZone.getTimeZone((ZoneId) zoneOffset0);
      StdDateFormat stdDateFormat0 = new StdDateFormat(timeZone0);
      MockDate mockDate0 = new MockDate();
      StringBuffer stringBuffer0 = new StringBuffer("");
      Format.Field format_Field0 = mock(Format.Field.class, new ViolatedAssumptionAnswer());
      FieldPosition fieldPosition0 = new FieldPosition(format_Field0);
      stdDateFormat0.format((Date) mockDate0, stringBuffer0, fieldPosition0);
      assertEquals(28, stringBuffer0.length());
      assertEquals("2014-02-14T20:21:21.320+0000", stringBuffer0.toString());
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      SimpleTimeZone simpleTimeZone0 = new SimpleTimeZone((-827), "GMT");
      Locale locale0 = Locale.CANADA;
      StdDateFormat stdDateFormat0 = new StdDateFormat(simpleTimeZone0, locale0);
      ParsePosition parsePosition0 = new ParsePosition(1232);
      stdDateFormat0.parseAsISO8601("yyyy-MM-dd'T'HH:mm:ss.SSSZ", parsePosition0);
      assertEquals(1232, parsePosition0.getErrorIndex());
      assertEquals("java.text.ParsePosition[index=1232,errorIndex=1232]", parsePosition0.toString());
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      StdDateFormat stdDateFormat0 = StdDateFormat.instance;
      // Undeclared exception!
      try { 
        stdDateFormat0.parseAsISO8601("[ -.-9*", (ParsePosition) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
      }
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      StdDateFormat stdDateFormat0 = StdDateFormat.instance;
      // Undeclared exception!
      try { 
        stdDateFormat0.parseAsISO8601("yyyy-MM-dd", (ParsePosition) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
      }
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      StdDateFormat stdDateFormat0 = StdDateFormat.instance;
      // Undeclared exception!
      try { 
        stdDateFormat0.parseAsISO8601("d+Rq*3|E<", (ParsePosition) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
      }
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      TimeZone timeZone0 = StdDateFormat.getDefaultTimeZone();
      StdDateFormat stdDateFormat0 = new StdDateFormat(timeZone0);
      ParsePosition parsePosition0 = new ParsePosition(33);
      Date date0 = stdDateFormat0.parseAsISO8601("4zy}'uuu.Q,CuWV", parsePosition0);
      assertNull(date0);
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      TimeZone timeZone0 = StdDateFormat.getDefaultTimeZone();
      StdDateFormat stdDateFormat0 = new StdDateFormat(timeZone0);
      ParsePosition parsePosition0 = new ParsePosition(33);
      Date date0 = stdDateFormat0.parseAsISO8601(":v3mFQ+3m, ", parsePosition0);
      assertNull(date0);
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      TimeZone timeZone0 = StdDateFormat.getDefaultTimeZone();
      StdDateFormat stdDateFormat0 = new StdDateFormat(timeZone0);
      ParsePosition parsePosition0 = new ParsePosition(84);
      Date date0 = stdDateFormat0.parseAsISO8601("3]gD19*Klo*-/e", parsePosition0);
      assertNull(date0);
  }

  @Test(timeout = 4000)
  public void test12()  throws Throwable  {
      StdDateFormat stdDateFormat0 = StdDateFormat.instance;
      // Undeclared exception!
      try { 
        stdDateFormat0.parseAsISO8601("8%{EVU:y:S?ZCd+y!", (ParsePosition) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
      }
  }

  @Test(timeout = 4000)
  public void test13()  throws Throwable  {
      StdDateFormat stdDateFormat0 = StdDateFormat.instance;
      ParsePosition parsePosition0 = new ParsePosition((-18));
      // Undeclared exception!
      try { 
        stdDateFormat0.parseAsISO8601("jS8]@Ea6/IiX+` :CO", parsePosition0);
        fail("Expecting exception: StringIndexOutOfBoundsException");
      
      } catch(StringIndexOutOfBoundsException e) {
      }
  }

  @Test(timeout = 4000)
  public void test14()  throws Throwable  {
      StdDateFormat stdDateFormat0 = StdDateFormat.instance;
      String string0 = "\\u9s`ACwZ";
      // Undeclared exception!
      try { 
        stdDateFormat0.parseAsISO8601(string0, (ParsePosition) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
      }
  }

  @Test(timeout = 4000)
  public void test15()  throws Throwable  {
      StdDateFormat stdDateFormat0 = new StdDateFormat();
      // Undeclared exception!
      try { 
        stdDateFormat0.parseAsISO8601("zqJMOA9:X>Z", (ParsePosition) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
      }
  }

  @Test(timeout = 4000)
  public void test16()  throws Throwable  {
      StdDateFormat stdDateFormat0 = StdDateFormat.instance;
      // Undeclared exception!
      try { 
        stdDateFormat0.parseAsISO8601("E}'!?$6", (ParsePosition) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
      }
  }

  @Test(timeout = 4000)
  public void test17()  throws Throwable  {
      TimeZone timeZone0 = StdDateFormat.getDefaultTimeZone();
      StdDateFormat stdDateFormat0 = new StdDateFormat(timeZone0);
      ParsePosition parsePosition0 = new ParsePosition(84);
      Date date0 = stdDateFormat0.parseAsISO8601("\", \"", parsePosition0);
      assertNull(date0);
  }

  @Test(timeout = 4000)
  public void test18()  throws Throwable  {
      StdDateFormat stdDateFormat0 = new StdDateFormat();
      // Undeclared exception!
      try { 
        stdDateFormat0.parse("6@|5_%vn`VihX'", (ParsePosition) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
      }
  }

  @Test(timeout = 4000)
  public void test19()  throws Throwable  {
      TimeZone timeZone0 = StdDateFormat.getDefaultTimeZone();
      StdDateFormat stdDateFormat0 = new StdDateFormat(timeZone0);
      ParsePosition parsePosition0 = new ParsePosition(84);
      Date date0 = stdDateFormat0.parse("3]gD19*Klo*-/e", parsePosition0);
      assertNull(date0);
  }

  @Test(timeout = 4000)
  public void test20()  throws Throwable  {
      StdDateFormat stdDateFormat0 = StdDateFormat.instance;
      String string0 = stdDateFormat0.instance.toString();
      assertEquals("DateFormat com.fasterxml.jackson.databind.util.StdDateFormat(locale: en_US)", string0);
  }

  @Test(timeout = 4000)
  public void test21()  throws Throwable  {
      StdDateFormat stdDateFormat0 = StdDateFormat.instance;
      MockDate mockDate0 = new MockDate();
      stdDateFormat0.instance.format((Date) mockDate0);
      Date date0 = stdDateFormat0.parse("2014-02-14T20:21:21.320+0000");
      assertEquals("Fri Feb 14 20:21:21 GMT 2014", date0.toString());
  }

  @Test(timeout = 4000)
  public void test22()  throws Throwable  {
      StdDateFormat stdDateFormat0 = new StdDateFormat();
      // Undeclared exception!
      try { 
        stdDateFormat0.parse("00");
        fail("Expecting exception: NoClassDefFoundError");
      
      } catch(NoClassDefFoundError e) {
         //
         // com/fasterxml/jackson/core/io/NumberInput
         //
         verifyException("com.fasterxml.jackson.databind.util.StdDateFormat", e);
      }
  }

  @Test(timeout = 4000)
  public void test23()  throws Throwable  {
      StdDateFormat stdDateFormat0 = new StdDateFormat();
      try { 
        stdDateFormat0.parse("h");
        fail("Expecting exception: ParseException");
      
      } catch(ParseException e) {
         //
         // Can not parse date \"h\": not compatible with any of standard forms (\"yyyy-MM-dd'T'HH:mm:ss.SSSZ\", \"yyyy-MM-dd'T'HH:mm:ss.SSS'Z'\", \"EEE, dd MMM yyyy HH:mm:ss zzz\", \"yyyy-MM-dd\")
         //
         verifyException("com.fasterxml.jackson.databind.util.StdDateFormat", e);
      }
  }

  @Test(timeout = 4000)
  public void test24()  throws Throwable  {
      StdDateFormat stdDateFormat0 = new StdDateFormat();
      Date date0 = stdDateFormat0.parse("-0");
      assertEquals("Thu Jan 01 00:00:00 GMT 1970", date0.toString());
  }

  @Test(timeout = 4000)
  public void test25()  throws Throwable  {
      StdDateFormat stdDateFormat0 = StdDateFormat.instance;
      try { 
        stdDateFormat0.parse("m=(aG(4aa/RW%o");
        fail("Expecting exception: ParseException");
      
      } catch(ParseException e) {
         //
         // Can not parse date \"m=(aG(4aa/RW%o\": not compatible with any of standard forms (\"yyyy-MM-dd'T'HH:mm:ss.SSSZ\", \"yyyy-MM-dd'T'HH:mm:ss.SSS'Z'\", \"EEE, dd MMM yyyy HH:mm:ss zzz\", \"yyyy-MM-dd\")
         //
         verifyException("com.fasterxml.jackson.databind.util.StdDateFormat", e);
      }
  }

  @Test(timeout = 4000)
  public void test26()  throws Throwable  {
      StdDateFormat stdDateFormat0 = StdDateFormat.instance;
      TimeZone timeZone0 = StdDateFormat.getDefaultTimeZone();
      stdDateFormat0.instance.setTimeZone(timeZone0);
      assertEquals("GMT", timeZone0.getID());
  }

  @Test(timeout = 4000)
  public void test27()  throws Throwable  {
      TimeZone timeZone0 = StdDateFormat.getDefaultTimeZone();
      StdDateFormat stdDateFormat0 = new StdDateFormat(timeZone0);
      stdDateFormat0.setTimeZone(timeZone0);
      assertEquals("GMT", timeZone0.getID());
  }

  @Test(timeout = 4000)
  public void test28()  throws Throwable  {
      StdDateFormat stdDateFormat0 = StdDateFormat.instance;
      Locale locale0 = Locale.JAPANESE;
      StdDateFormat stdDateFormat1 = stdDateFormat0.withLocale(locale0);
      assertNotSame(stdDateFormat1, stdDateFormat0);
  }

  @Test(timeout = 4000)
  public void test29()  throws Throwable  {
      StdDateFormat stdDateFormat0 = StdDateFormat.instance;
      StdDateFormat stdDateFormat1 = stdDateFormat0.withTimeZone((TimeZone) null);
      assertNotSame(stdDateFormat1, stdDateFormat0);
  }

  @Test(timeout = 4000)
  public void test30()  throws Throwable  {
      TimeZone timeZone0 = StdDateFormat.getDefaultTimeZone();
      StdDateFormat stdDateFormat0 = new StdDateFormat(timeZone0);
      StdDateFormat stdDateFormat1 = stdDateFormat0.withTimeZone(timeZone0);
      assertSame(stdDateFormat1, stdDateFormat0);
  }

  @Test(timeout = 4000)
  public void test31()  throws Throwable  {
      StdDateFormat stdDateFormat0 = new StdDateFormat();
      Locale locale0 = Locale.US;
      StdDateFormat stdDateFormat1 = stdDateFormat0.withLocale(locale0);
      assertSame(stdDateFormat1, stdDateFormat0);
  }

  @Test(timeout = 4000)
  public void test32()  throws Throwable  {
      MockSimpleDateFormat mockSimpleDateFormat0 = (MockSimpleDateFormat)StdDateFormat.getBlueprintISO8601Format();
      assertEquals("yyyy-MM-dd'T'HH:mm:ss.SSSZ", mockSimpleDateFormat0.toPattern());
  }

  @Test(timeout = 4000)
  public void test33()  throws Throwable  {
      TimeZone timeZone0 = TimeZone.getDefault();
      MockSimpleDateFormat mockSimpleDateFormat0 = (MockSimpleDateFormat)StdDateFormat.getRFC1123Format(timeZone0);
      assertEquals("EEE, dd MMM yyyy HH:mm:ss zzz", mockSimpleDateFormat0.toPattern());
  }

  @Test(timeout = 4000)
  public void test34()  throws Throwable  {
      TimeZone timeZone0 = StdDateFormat.getDefaultTimeZone();
      MockSimpleDateFormat mockSimpleDateFormat0 = (MockSimpleDateFormat)StdDateFormat.getISO8601Format(timeZone0);
      assertEquals("yyyy-MM-dd'T'HH:mm:ss.SSSZ", mockSimpleDateFormat0.toPattern());
  }

  @Test(timeout = 4000)
  public void test35()  throws Throwable  {
      MockSimpleDateFormat mockSimpleDateFormat0 = (MockSimpleDateFormat)StdDateFormat.getBlueprintRFC1123Format();
      assertEquals("EEE, dd MMM yyyy HH:mm:ss zzz", mockSimpleDateFormat0.toPattern());
  }

  @Test(timeout = 4000)
  public void test36()  throws Throwable  {
      TimeZone timeZone0 = StdDateFormat.getDefaultTimeZone();
      StdDateFormat stdDateFormat0 = new StdDateFormat(timeZone0);
      StdDateFormat stdDateFormat1 = stdDateFormat0.clone();
      assertNotSame(stdDateFormat0, stdDateFormat1);
  }