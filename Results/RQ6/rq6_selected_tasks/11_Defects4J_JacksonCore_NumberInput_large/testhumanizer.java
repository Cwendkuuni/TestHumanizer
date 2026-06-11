private static final double DELTA = 0.01;
    private static final long DEFAULT_LONG = -9223372036854775808L;
    private static final int DEFAULT_INT = 29;

    @Test(timeout = 4000)
    public void testParseDoubleWithInvalidString() throws Throwable {
        // Given: An invalid string for parsing as double
        String invalidDouble = "ejR3G&5U5ot!";
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseDouble(invalidDouble);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testParseBigDecimalWithInvalidCharArray() throws Throwable {
        // Given: A character array with invalid length
        char[] charArray = new char[1];
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseBigDecimal(charArray, 0, -1385);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            verifyException("java.math.BigDecimal", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseAsLongWithInvalidString() throws Throwable {
        // Given: An invalid string for parsing as long
        String invalidLong = "-";
        
        // When: Parsing with default value
        long result = NumberInput.parseAsLong(invalidLong, DEFAULT_LONG);
        
        // Then: Result should be the default value
        assertEquals(DEFAULT_LONG, result);
    }

    @Test(timeout = 4000)
    public void testParseAsDoubleWithInvalidString() throws Throwable {
        // Given: An invalid string for parsing as double
        String invalidDouble = "|JnB";
        
        // When: Parsing with default value
        double result = NumberInput.parseAsDouble(invalidDouble, 0.0);
        
        // Then: Result should be the default value
        assertEquals(0.0, result, DELTA);
    }

    @Test(timeout = 4000)
    public void testParseAsDoubleWithEmptyString() throws Throwable {
        // Given: An empty string for parsing as double
        String emptyString = "";
        
        // When: Parsing with default value
        double result = NumberInput.parseAsDouble(emptyString, -412.97989257889);
        
        // Then: Result should be the default value
        assertEquals(-412.97989257889, result, DELTA);
    }

    @Test(timeout = 4000)
    public void testParseAsDoubleWithNullString() throws Throwable {
        // Given: A null string for parsing as double
        String nullString = null;
        
        // When: Parsing with default value
        double result = NumberInput.parseAsDouble(nullString, 29);
        
        // Then: Result should be the default value
        assertEquals(29.0, result, DELTA);
    }

    @Test(timeout = 4000)
    public void testParseAsDoubleWithSpecialString() throws Throwable {
        // Given: A special string for parsing as double
        String specialDouble = "2.2250738585072012e-308";
        
        // When: Parsing with default value
        double result = NumberInput.parseAsDouble(specialDouble, 0.0);
        
        // Then: Result should be the parsed value
        assertEquals(4.9E-324, result, DELTA);
    }

    @Test(timeout = 4000)
    public void testParseAsLongWithInvalidStringAndDefault() throws Throwable {
        // Given: An invalid string for parsing as long
        String invalidLong = ",PzPNNzZ4Z";
        
        // When: Parsing with default value
        long result = NumberInput.parseAsLong(invalidLong, 488L);
        
        // Then: Result should be the default value
        assertEquals(488L, result);
    }

    @Test(timeout = 4000)
    public void testParseAsLongWithValidString() throws Throwable {
        // Given: A valid string for parsing as long
        String validLong = "1";
        
        // When: Parsing with default value
        long result = NumberInput.parseAsLong(validLong, 0);
        
        // Then: Result should be the parsed value
        assertEquals(1L, result);
    }

    @Test(timeout = 4000)
    public void testParseAsLongWithInvalidStringAndDefault2() throws Throwable {
        // Given: An invalid string for parsing as long
        String invalidLong = "-].3x-M";
        
        // When: Parsing with default value
        long result = NumberInput.parseAsLong(invalidLong, 1383);
        
        // Then: Result should be the default value
        assertEquals(1383L, result);
    }

    @Test(timeout = 4000)
    public void testParseAsLongWithInvalidStringAndDefault3() throws Throwable {
        // Given: An invalid string for parsing as long
        String invalidLong = "+Ab~xDGB";
        
        // When: Parsing with default value
        long result = NumberInput.parseAsLong(invalidLong, -3163L);
        
        // Then: Result should be the default value
        assertEquals(-3163L, result);
    }

    @Test(timeout = 4000)
    public void testParseAsLongWithEmptyString() throws Throwable {
        // Given: An empty string for parsing as long
        String emptyString = "";
        
        // When: Parsing with default value
        long result = NumberInput.parseAsLong(emptyString, 0L);
        
        // Then: Result should be the default value
        assertEquals(0L, result);
    }

    @Test(timeout = 4000)
    public void testParseAsLongWithNullString() throws Throwable {
        // Given: A null string for parsing as long
        String nullString = null;
        
        // When: Parsing with default value
        long result = NumberInput.parseAsLong(nullString, 926);
        
        // Then: Result should be the default value
        assertEquals(926L, result);
    }

    @Test(timeout = 4000)
    public void testParseAsIntWithInvalidString() throws Throwable {
        // Given: An invalid string for parsing as int
        String invalidInt = "'@6!;:^>";
        
        // When: Parsing with default value
        int result = NumberInput.parseAsInt(invalidInt, 0);
        
        // Then: Result should be the default value
        assertEquals(0, result);
    }

    @Test(timeout = 4000)
    public void testParseAsIntWithInvalidStringAndDefault() throws Throwable {
        // Given: An invalid string for parsing as int
        String invalidInt = "-";
        
        // When: Parsing with default value
        int result = NumberInput.parseAsInt(invalidInt, 9);
        
        // Then: Result should be the default value
        assertEquals(9, result);
    }

    @Test(timeout = 4000)
    public void testParseAsIntWithInvalidStringAndDefault2() throws Throwable {
        // Given: An invalid string for parsing as int
        String invalidInt = "+5ogL";
        
        // When: Parsing with default value
        int result = NumberInput.parseAsInt(invalidInt, -2653);
        
        // Then: Result should be the default value
        assertEquals(-2653, result);
    }

    @Test(timeout = 4000)
    public void testParseAsIntWithEmptyString() throws Throwable {
        // Given: An empty string for parsing as int
        String emptyString = "";
        
        // When: Parsing with default value
        int result = NumberInput.parseAsInt(emptyString, -6);
        
        // Then: Result should be the default value
        assertEquals(-6, result);
    }

    @Test(timeout = 4000)
    public void testParseAsIntWithNullString() throws Throwable {
        // Given: A null string for parsing as int
        String nullString = null;
        
        // When: Parsing with default value
        int result = NumberInput.parseAsInt(nullString, DEFAULT_INT);
        
        // Then: Result should be the default value
        assertEquals(DEFAULT_INT, result);
    }

    @Test(timeout = 4000)
    public void testInLongRangeWithInvalidString() throws Throwable {
        // Given: An invalid string for checking long range
        String invalidLongRange = "9>(L$=`b1^<d_s0S1O";
        
        // When: Checking if in long range
        boolean result = NumberInput.inLongRange(invalidLongRange, true);
        
        // Then: Result should be false
        assertFalse(result);
    }

    @Test(timeout = 4000)
    public void testInLongRangeWithSpecialString() throws Throwable {
        // Given: A special string for checking long range
        String specialLongRange = "2.2250738585072012e-308";
        
        // When: Checking if in long range
        boolean result = NumberInput.inLongRange(specialLongRange, true);
        
        // Then: Result should be false
        assertFalse(result);
    }

    @Test(timeout = 4000)
    public void testInLongRangeWithInvalidString2() throws Throwable {
        // Given: An invalid string for checking long range
        String invalidLongRange = "8l?8$[/%(@x9pAY]m";
        
        // When: Checking if in long range
        boolean result = NumberInput.inLongRange(invalidLongRange, true);
        
        // Then: Result should be true
        assertTrue(result);
    }

    @Test(timeout = 4000)
    public void testInLongRangeWithInvalidString3() throws Throwable {
        // Given: An invalid string for checking long range
        String invalidLongRange = "{O9q/DNHl8'G;j3 yZ*";
        
        // When: Checking if in long range
        boolean result = NumberInput.inLongRange(invalidLongRange, false);
        
        // Then: Result should be false
        assertFalse(result);
    }

    @Test(timeout = 4000)
    public void testInLongRangeWithCharArray() throws Throwable {
        // Given: A character array for checking long range
        char[] charArray = new char[1];
        charArray[0] = '{';
        
        // When: Checking if in long range
        boolean result = NumberInput.inLongRange(charArray, 0, 19, false);
        
        // Then: Result should be false
        assertFalse(result);
    }

    @Test(timeout = 4000)
    public void testInLongRangeWithCharArray2() throws Throwable {
        // Given: A character array for checking long range
        char[] charArray = new char[13];
        charArray[1] = '9';
        
        // When: Checking if in long range
        boolean result = NumberInput.inLongRange(charArray, 1, 19, true);
        
        // Then: Result should be true
        assertTrue(result);
    }

    @Test(timeout = 4000)
    public void testInLongRangeWithEmptyCharArray() throws Throwable {
        // Given: An empty character array for checking long range
        char[] charArray = new char[0];
        
        // When: Checking if in long range
        boolean result = NumberInput.inLongRange(charArray, 0, 29, false);
        
        // Then: Result should be false
        assertFalse(result);
    }

    @Test(timeout = 4000)
    public void testInLongRangeWithCharArray3() throws Throwable {
        // Given: A character array for checking long range
        char[] charArray = new char[5];
        
        // When: Checking if in long range
        boolean result = NumberInput.inLongRange(charArray, 19, 0, false);
        
        // Then: Result should be true
        assertTrue(result);
    }

    @Test(timeout = 4000)
    public void testParseLongWithInvalidString() throws Throwable {
        // Given: An invalid string for parsing as long
        String invalidLong = "rbT[|(0T_;K` =L$";
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseLong(invalidLong);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            verifyException("java.lang.NumberFormatException", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseIntWithInvalidString() throws Throwable {
        // Given: An invalid string for parsing as int
        String invalidInt = "43925'";
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseInt(invalidInt);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            verifyException("java.lang.NumberFormatException", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseIntWithInvalidString2() throws Throwable {
        // Given: An invalid string for parsing as int
        String invalidInt = "3925>UU";
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseInt(invalidInt);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            verifyException("java.lang.NumberFormatException", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseIntWithLeadingZeros() throws Throwable {
        // Given: A string with leading zeros for parsing as int
        String validInt = "008";
        
        // When: Parsing the string
        int result = NumberInput.parseInt(validInt);
        
        // Then: Result should be the parsed value
        assertEquals(8, result);
    }

    @Test(timeout = 4000)
    public void testParseIntWithInvalidString3() throws Throwable {
        // Given: An invalid string for parsing as int
        String invalidInt = "00%";
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseInt(invalidInt);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            verifyException("java.lang.NumberFormatException", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseIntWithInvalidString4() throws Throwable {
        // Given: An invalid string for parsing as int
        String invalidInt = "06c";
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseInt(invalidInt);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            verifyException("java.lang.NumberFormatException", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseIntWithLeadingZeros2() throws Throwable {
        // Given: A string with leading zeros for parsing as int
        String validInt = "08";
        
        // When: Parsing the string
        int result = NumberInput.parseInt(validInt);
        
        // Then: Result should be the parsed value
        assertEquals(8, result);
    }

    @Test(timeout = 4000)
    public void testParseIntWithInvalidString5() throws Throwable {
        // Given: An invalid string for parsing as int
        String invalidInt = "9*9\"(3!";
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseInt(invalidInt);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            verifyException("java.lang.NumberFormatException", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseIntWithInvalidString6() throws Throwable {
        // Given: An invalid string for parsing as int
        String invalidInt = "0FC";
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseInt(invalidInt);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            verifyException("java.lang.NumberFormatException", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseIntWithValidString() throws Throwable {
        // Given: A valid string for parsing as int
        String validInt = "3995";
        
        // When: Parsing the string
        int result = NumberInput.parseInt(validInt);
        
        // Then: Result should be the parsed value
        assertEquals(3995, result);
    }

    @Test(timeout = 4000)
    public void testParseIntWithInvalidString7() throws Throwable {
        // Given: An invalid string for parsing as int
        String invalidInt = "#>$Yl=NL";
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseInt(invalidInt);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            verifyException("java.lang.NumberFormatException", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseLongWithInvalidString2() throws Throwable {
        // Given: An invalid string for parsing as long
        String invalidLong = "Z";
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseLong(invalidLong);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            verifyException("java.lang.NumberFormatException", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseIntWithInvalidString8() throws Throwable {
        // Given: An invalid string for parsing as int
        String invalidInt = "com.fasterxml.jackson.core.io.NumberInput";
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseInt(invalidInt);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            verifyException("java.lang.NumberFormatException", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseIntWithInvalidString9() throws Throwable {
        // Given: An invalid string for parsing as int
        String invalidInt = "-YeK Jnik75{F6ZI\f";
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseInt(invalidInt);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            verifyException("java.lang.NumberFormatException", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseIntWithInvalidString10() throws Throwable {
        // Given: An invalid string for parsing as int
        String invalidInt = "-";
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseInt(invalidInt);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            verifyException("java.lang.NumberFormatException", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseIntWithNegativeString() throws Throwable {
        // Given: A negative string for parsing as int
        String negativeInt = "-6";
        
        // When: Parsing the string
        int result = NumberInput.parseInt(negativeInt);
        
        // Then: Result should be the parsed value
        assertEquals(-6, result);
    }

    @Test(timeout = 4000)
    public void testParseIntWithCharArray() throws Throwable {
        // Given: A character array for parsing as int
        char[] charArray = new char[9];
        
        // When: Parsing the character array
        int result = NumberInput.parseInt(charArray, 0, 1383);
        
        // Then: Result should be the parsed value
        assertEquals(-1038366032, result);
    }

    @Test(timeout = 4000)
    public void testParseIntWithCharArray2() throws Throwable {
        // Given: A character array for parsing as int
        char[] charArray = new char[9];
        
        // When: Parsing the character array
        int result = NumberInput.parseInt(charArray, 1, 8);
        
        // Then: Result should be the parsed value
        assertEquals(-533333328, result);
    }

    @Test(timeout = 4000)
    public void testParseIntWithCharArray3() throws Throwable {
        // Given: A character array for parsing as int
        char[] charArray = new char[41];
        
        // When: Parsing the character array
        int result = NumberInput.parseInt(charArray, 5, 7);
        
        // Then: Result should be the parsed value
        assertEquals(-53333328, result);
    }

    @Test(timeout = 4000)
    public void testParseIntWithCharArray4() throws Throwable {
        // Given: A character array for parsing as int
        char[] charArray = new char[41];
        
        // When: Parsing the character array
        int result = NumberInput.parseInt(charArray, 5, 5);
        
        // Then: Result should be the parsed value
        assertEquals(-533328, result);
    }

    @Test(timeout = 4000)
    public void testParseIntWithCharArray5() throws Throwable {
        // Given: A character array for parsing as int
        char[] charArray = new char[13];
        
        // When: Parsing the character array
        int result = NumberInput.parseInt(charArray, 1, 4);
        
        // Then: Result should be the parsed value
        assertEquals(-53328, result);
    }

    @Test(timeout = 4000)
    public void testParseIntWithCharArray6() throws Throwable {
        // Given: A character array for parsing as int
        char[] charArray = new char[10];
        
        // When: Parsing the character array
        int result = NumberInput.parseInt(charArray, 3, 3);
        
        // Then: Result should be the parsed value
        assertEquals(-5328, result);
    }

    @Test(timeout = 4000)
    public void testParseIntWithCharArray7() throws Throwable {
        // Given: A character array for parsing as int
        char[] charArray = new char[25];
        
        // When: Parsing the character array
        int result = NumberInput.parseInt(charArray, 0, 2);
        
        // Then: Result should be the parsed value
        assertEquals(-528, result);
    }

    @Test(timeout = 4000)
    public void testParseIntWithCharArray8() throws Throwable {
        // Given: A character array for parsing as int
        char[] charArray = new char[8];
        
        // When: Parsing the character array
        int result = NumberInput.parseInt(charArray, 1, 6);
        
        // Then: Result should be the parsed value
        assertEquals(-5333328, result);
    }

    @Test(timeout = 4000)
    public void testNumberInputConstructor() throws Throwable {
        // Given: A new instance of NumberInput
        NumberInput numberInput = new NumberInput();
        
        // Then: Instance should be created successfully
        assertNotNull(numberInput);
    }

    @Test(timeout = 4000)
    public void testParseBigDecimalWithValidString() throws Throwable {
        // Given: A valid string for parsing as BigDecimal
        String validBigDecimal = "1";
        
        // When: Parsing the string
        BigDecimal result = NumberInput.parseBigDecimal(validBigDecimal);
        
        // Then: Result should be the parsed value
        assertEquals((byte) 1, result.byteValue());
    }

    @Test(timeout = 4000)
    public void testParseLongWithCharArray() throws Throwable {
        // Given: A character array for parsing as long
        char[] charArray = new char[1];
        
        // When & Then: Expect ArrayIndexOutOfBoundsException
        try {
            NumberInput.parseLong(charArray, 0, 0);
            fail("Expecting exception: ArrayIndexOutOfBoundsException");
        } catch (ArrayIndexOutOfBoundsException e) {
            verifyException("com.fasterxml.jackson.core.io.NumberInput", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseBigDecimalWithEmptyCharArray() throws Throwable {
        // Given: An empty character array for parsing as BigDecimal
        char[] charArray = new char[0];
        
        // When & Then: Expect NumberFormatException
        try {
            NumberInput.parseBigDecimal(charArray);
            fail("Expecting exception: NumberFormatException");
        } catch (NumberFormatException e) {
            verifyException("java.math.BigDecimal", e);
        }
    }