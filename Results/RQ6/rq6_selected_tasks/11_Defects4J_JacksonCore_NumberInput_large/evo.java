@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      try { 
        NumberInput.parseDouble("BG1xDK");
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
      }
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      char[] charArray0 = new char[2];
      try { 
        NumberInput.parseBigDecimal(charArray0, (-1), (-1));
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // Bad offset or len arguments for char[] input.
         //
         verifyException("java.math.BigDecimal", e);
      }
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      char[] charArray0 = new char[13];
      // Undeclared exception!
      try { 
        NumberInput.parseLong(charArray0, 0, 48);
        fail("Expecting exception: ArrayIndexOutOfBoundsException");
      
      } catch(ArrayIndexOutOfBoundsException e) {
         //
         // 39
         //
         verifyException("com.fasterxml.jackson.core.io.NumberInput", e);
      }
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      double double0 = NumberInput.parseAsDouble("", (-4633));
      assertEquals((-4633.0), double0, 0.01);
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      double double0 = NumberInput.parseAsDouble((String) null, 1296.1077);
      assertEquals(1296.1077, double0, 0.01);
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      double double0 = NumberInput.parseAsDouble("TGI>5J8g", (-918.5));
      assertEquals((-918.5), double0, 0.01);
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      long long0 = NumberInput.parseAsLong("#dFQYJZ", 1L);
      assertEquals(1L, long0);
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      long long0 = NumberInput.parseAsLong("43", 43);
      assertEquals(43L, long0);
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      long long0 = NumberInput.parseAsLong("-g{hwGX 4r<Y)!4b#|", 0L);
      assertEquals(0L, long0);
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      long long0 = NumberInput.parseAsLong("+", 606);
      assertEquals(606L, long0);
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      long long0 = NumberInput.parseAsLong("", 0L);
      assertEquals(0L, long0);
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      long long0 = NumberInput.parseAsLong((String) null, (-583L));
      assertEquals((-583L), long0);
  }

  @Test(timeout = 4000)
  public void test12()  throws Throwable  {
      int int0 = NumberInput.parseAsInt("-pt8R`%Af4S|", 34);
      assertEquals(34, int0);
  }

  @Test(timeout = 4000)
  public void test13()  throws Throwable  {
      int int0 = NumberInput.parseAsInt("+", 606);
      assertEquals(606, int0);
  }

  @Test(timeout = 4000)
  public void test14()  throws Throwable  {
      int int0 = NumberInput.parseAsInt("", (-4633));
      assertEquals((-4633), int0);
  }

  @Test(timeout = 4000)
  public void test15()  throws Throwable  {
      int int0 = NumberInput.parseAsInt((String) null, (-2058005160));
      assertEquals((-2058005160), int0);
  }

  @Test(timeout = 4000)
  public void test16()  throws Throwable  {
      int int0 = NumberInput.parseAsInt("2.2250738585072012e-308", 66);
      assertEquals(0, int0);
  }

  @Test(timeout = 4000)
  public void test17()  throws Throwable  {
      boolean boolean0 = NumberInput.inLongRange("\"*1 22Uq`9Ed+OQ^ Y", true);
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test18()  throws Throwable  {
      boolean boolean0 = NumberInput.inLongRange("9L~k09+U]dqi9 _='e|", false);
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test19()  throws Throwable  {
      boolean boolean0 = NumberInput.inLongRange("com.fasterxml.jackson.core.io.NumberInput", true);
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test20()  throws Throwable  {
      char[] charArray0 = new char[18];
      charArray0[0] = 'D';
      boolean boolean0 = NumberInput.inLongRange(charArray0, (int) '\u0000', 19, true);
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test21()  throws Throwable  {
      char[] charArray0 = new char[14];
      charArray0[0] = '9';
      boolean boolean0 = NumberInput.inLongRange(charArray0, (int) '\u0000', 19, true);
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test22()  throws Throwable  {
      char[] charArray0 = new char[2];
      boolean boolean0 = NumberInput.inLongRange(charArray0, 45, 0, true);
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test23()  throws Throwable  {
      char[] charArray0 = new char[1];
      boolean boolean0 = NumberInput.inLongRange(charArray0, (-2840), 66, false);
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test24()  throws Throwable  {
      // Undeclared exception!
      try { 
        NumberInput.parseLong("");
        fail("Expecting exception: StringIndexOutOfBoundsException");
      
      } catch(StringIndexOutOfBoundsException e) {
      }
  }

  @Test(timeout = 4000)
  public void test25()  throws Throwable  {
      // Undeclared exception!
      try { 
        NumberInput.parseLong("^[|J\"55l[5.");
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // For input string: \"^[|J\"55l[5.\"
         //
         verifyException("java.lang.NumberFormatException", e);
      }
  }

  @Test(timeout = 4000)
  public void test26()  throws Throwable  {
      int int0 = NumberInput.parseInt("94980");
      assertEquals(94980, int0);
  }

  @Test(timeout = 4000)
  public void test27()  throws Throwable  {
      // Undeclared exception!
      try { 
        NumberInput.parseInt("9498w");
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // For input string: \"9498w\"
         //
         verifyException("java.lang.NumberFormatException", e);
      }
  }

  @Test(timeout = 4000)
  public void test28()  throws Throwable  {
      int int0 = NumberInput.parseInt("493");
      assertEquals(493, int0);
  }

  @Test(timeout = 4000)
  public void test29()  throws Throwable  {
      // Undeclared exception!
      try { 
        NumberInput.parseInt("89(");
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // For input string: \"89(\"
         //
         verifyException("java.lang.NumberFormatException", e);
      }
  }

  @Test(timeout = 4000)
  public void test30()  throws Throwable  {
      // Undeclared exception!
      try { 
        NumberInput.parseInt("09D/$HH3B");
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // For input string: \"09D/$HH3B\"
         //
         verifyException("java.lang.NumberFormatException", e);
      }
  }

  @Test(timeout = 4000)
  public void test31()  throws Throwable  {
      int int0 = NumberInput.parseInt("43");
      assertEquals(43, int0);
  }

  @Test(timeout = 4000)
  public void test32()  throws Throwable  {
      // Undeclared exception!
      try { 
        NumberInput.parseInt("9!a");
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // For input string: \"9!a\"
         //
         verifyException("java.lang.NumberFormatException", e);
      }
  }

  @Test(timeout = 4000)
  public void test33()  throws Throwable  {
      // Undeclared exception!
      try { 
        NumberInput.parseInt("4D");
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // For input string: \"4D\"
         //
         verifyException("java.lang.NumberFormatException", e);
      }
  }

  @Test(timeout = 4000)
  public void test34()  throws Throwable  {
      // Undeclared exception!
      try { 
        NumberInput.parseInt("-%_");
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // For input string: \"-%_\"
         //
         verifyException("java.lang.NumberFormatException", e);
      }
  }

  @Test(timeout = 4000)
  public void test35()  throws Throwable  {
      // Undeclared exception!
      try { 
        NumberInput.parseInt("az\"");
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // For input string: \"az\"\"
         //
         verifyException("java.lang.NumberFormatException", e);
      }
  }

  @Test(timeout = 4000)
  public void test36()  throws Throwable  {
      // Undeclared exception!
      try { 
        NumberInput.parseInt("2.2250738585072012e-308");
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // For input string: \"2.2250738585072012e-308\"
         //
         verifyException("java.lang.NumberFormatException", e);
      }
  }

  @Test(timeout = 4000)
  public void test37()  throws Throwable  {
      // Undeclared exception!
      try { 
        NumberInput.parseInt("-g{hwGX 4r<Y)!4b#|");
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // For input string: \"-g{hwGX 4r<Y)!4b#|\"
         //
         verifyException("java.lang.NumberFormatException", e);
      }
  }

  @Test(timeout = 4000)
  public void test38()  throws Throwable  {
      // Undeclared exception!
      try { 
        NumberInput.parseInt("-");
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // For input string: \"-\"
         //
         verifyException("java.lang.NumberFormatException", e);
      }
  }

  @Test(timeout = 4000)
  public void test39()  throws Throwable  {
      int int0 = NumberInput.parseInt("-9");
      assertEquals((-9), int0);
  }

  @Test(timeout = 4000)
  public void test40()  throws Throwable  {
      // Undeclared exception!
      try { 
        NumberInput.parseInt("949$80");
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // For input string: \"949$80\"
         //
         verifyException("java.lang.NumberFormatException", e);
      }
  }

  @Test(timeout = 4000)
  public void test41()  throws Throwable  {
      char[] charArray0 = new char[18];
      int int0 = NumberInput.parseInt(charArray0, 8, 8);
      assertEquals((-533333328), int0);
  }

  @Test(timeout = 4000)
  public void test42()  throws Throwable  {
      char[] charArray0 = new char[9];
      int int0 = NumberInput.parseInt(charArray0, 0, 7);
      assertEquals((-53333328), int0);
  }

  @Test(timeout = 4000)
  public void test43()  throws Throwable  {
      char[] charArray0 = new char[12];
      int int0 = NumberInput.parseInt(charArray0, 6, 6);
      assertEquals((-5333328), int0);
  }

  @Test(timeout = 4000)
  public void test44()  throws Throwable  {
      char[] charArray0 = new char[18];
      int int0 = NumberInput.parseInt(charArray0, 4, 4);
      assertEquals((-53328), int0);
  }

  @Test(timeout = 4000)
  public void test45()  throws Throwable  {
      char[] charArray0 = new char[7];
      int int0 = NumberInput.parseInt(charArray0, 3, 3);
      assertEquals((-5328), int0);
  }

  @Test(timeout = 4000)
  public void test46()  throws Throwable  {
      char[] charArray0 = new char[47];
      int int0 = NumberInput.parseInt(charArray0, 5, 5);
      assertEquals((-533328), int0);
  }

  @Test(timeout = 4000)
  public void test47()  throws Throwable  {
      char[] charArray0 = new char[7];
      int int0 = NumberInput.parseInt(charArray0, 2, 2);
      assertEquals((-528), int0);
  }

  @Test(timeout = 4000)
  public void test48()  throws Throwable  {
      char[] charArray0 = new char[9];
      int int0 = NumberInput.parseInt(charArray0, 0, 0);
      assertEquals((-48), int0);
  }

  @Test(timeout = 4000)
  public void test49()  throws Throwable  {
      NumberInput numberInput0 = new NumberInput();
  }

  @Test(timeout = 4000)
  public void test50()  throws Throwable  {
      try { 
        NumberInput.parseBigDecimal("");
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("java.math.BigDecimal", e);
      }
  }

  @Test(timeout = 4000)
  public void test51()  throws Throwable  {
      char[] charArray0 = new char[2];
      try { 
        NumberInput.parseBigDecimal(charArray0);
        fail("Expecting exception: NumberFormatException");
      
      } catch(NumberFormatException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("java.math.BigDecimal", e);
      }
  }