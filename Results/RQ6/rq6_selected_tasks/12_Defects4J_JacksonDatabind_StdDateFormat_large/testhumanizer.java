private static final String RFC1123_PATTERN = "EEE, dd MMM yyyy HH:mm:ss zzz";
    private static final String ISO8601_PATTERN = "yyyy-MM-dd'T'HH:mm:ss.SSSZ";
    private static final String DEFAULT_TIMEZONE_ID = "GMT";

    @Test(timeout = 4000)
    public void testParseAsRFC1123WithEmptyString() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = new StdDateFormat();
        ParsePosition parsePosition = new ParsePosition(1508);

        // When
        Date date = stdDateFormat.parseAsRFC1123("", parsePosition);

        // Then
        assertNull("Expected null when parsing an empty string as RFC1123", date);
    }

    @Test(timeout = 4000)
    public void testLooksLikeISO8601WithInvalidString() throws Throwable {
        // Given
        TimeZone timeZone = TimeZone.getTimeZone("$IO0|u+c-rZ}");
        Locale locale = Locale.KOREA;
        StdDateFormat stdDateFormat = new StdDateFormat(timeZone, locale);

        // When
        boolean result = stdDateFormat.looksLikeISO8601("$IO0|u+c-rZ}");

        // Then
        assertFalse("Expected false for a string that does not look like ISO8601", result);
    }

    @Test(timeout = 4000)
    public void testGetISO8601Format() throws Throwable {
        // Given
        SimpleTimeZone simpleTimeZone = new SimpleTimeZone(1148, "Fnv*oR!8");
        Locale locale = Locale.UK;

        // When
        MockSimpleDateFormat mockSimpleDateFormat = (MockSimpleDateFormat) StdDateFormat.getISO8601Format(simpleTimeZone, locale);

        // Then
        assertEquals("Expected ISO8601 pattern", ISO8601_PATTERN, mockSimpleDateFormat.toLocalizedPattern());
    }

    @Test(timeout = 4000)
    public void testFormatDate() throws Throwable {
        // Given
        TimeZone timeZone = StdDateFormat.getDefaultTimeZone();
        StdDateFormat stdDateFormat = new StdDateFormat(timeZone);
        MockDate mockDate = new MockDate(2601, -723, -723);
        StringBuffer stringBuffer = new StringBuffer();
        FieldPosition fieldPosition = new FieldPosition(45);

        // When
        stdDateFormat.format(mockDate, stringBuffer, fieldPosition);

        // Then
        assertEquals("Expected formatted date length", 28, stringBuffer.length());
        assertEquals("Expected formatted date string", "4438-10-08T00:00:00.000+0000", stringBuffer.toString());
    }

    @Test(timeout = 4000)
    public void testWithTimeZoneReturnsSameInstance() throws Throwable {
        // Given
        TimeZone timeZone = TimeZone.getTimeZone("");
        StdDateFormat stdDateFormat = new StdDateFormat(timeZone);

        // When
        StdDateFormat result = stdDateFormat.withTimeZone(timeZone);

        // Then
        assertSame("Expected the same instance when setting the same time zone", stdDateFormat, result);
    }

    @Test(timeout = 4000)
    public void testWithTimeZoneAndLocale() throws Throwable {
        // Given
        Locale locale = Locale.FRENCH;
        StdDateFormat stdDateFormat = new StdDateFormat(null, locale);

        // When
        StdDateFormat result = stdDateFormat.withTimeZone(null);
        String resultString = result.toString();

        // Then
        assertEquals("Expected specific string representation", 
            "DateFormat com.fasterxml.jackson.databind.util.StdDateFormat (timezone: sun.util.calendar.ZoneInfo[id=\"GMT\",offset=0,dstSavings=0,useDaylight=false,transitions=0,lastRule=null])(locale: fr)", 
            resultString);
    }

    @Test(timeout = 4000)
    public void testGetRFC1123Format() throws Throwable {
        // Given
        TimeZone timeZone = StdDateFormat.getDefaultTimeZone();
        Locale locale = Locale.JAPAN;

        // When
        MockSimpleDateFormat mockSimpleDateFormat = (MockSimpleDateFormat) StdDateFormat.getRFC1123Format(timeZone, locale);

        // Then
        assertEquals("Expected RFC1123 pattern", RFC1123_PATTERN, mockSimpleDateFormat.toLocalizedPattern());
    }

    @Test(timeout = 4000)
    public void testParseAsISO8601WithNullPosition() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = new StdDateFormat();

        // When & Then
        try {
            stdDateFormat.parseAsISO8601("oh5o(wF@LfldWrE-S\"", null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testParseAsISO8601WithInvalidString() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = new StdDateFormat();

        // When & Then
        try {
            stdDateFormat.parseAsISO8601("P-3x(.", null);
            fail("Expecting exception: StringIndexOutOfBoundsException");
        } catch (StringIndexOutOfBoundsException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testParseAsISO8601WithNullPositionInstance() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = StdDateFormat.instance;

        // When & Then
        try {
            stdDateFormat.parseAsISO8601("vm+Sjjj&", null);
            fail("Expecting exception: StringIndexOutOfBoundsException");
        } catch (StringIndexOutOfBoundsException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testParseAsISO8601WithNullPositionGT() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = StdDateFormat.instance;

        // When & Then
        try {
            stdDateFormat.parseAsISO8601("GT", null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testParseAsISO8601WithNullPositionQeN() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = StdDateFormat.instance;

        // When & Then
        try {
            stdDateFormat.parseAsISO8601("qeN,JDyd", null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testParseAsISO8601WithInvalidStringAndPosition() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = new StdDateFormat();
        ParsePosition parsePosition = new ParsePosition(1581);

        // When
        Date date = stdDateFormat.parseAsISO8601("O-N:Gz@V8{;I`z<G", parsePosition);

        // Then
        assertNull("Expected null when parsing an invalid ISO8601 string", date);
    }

    @Test(timeout = 4000)
    public void testParseAsISO8601WithNullPositionX() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = StdDateFormat.instance;

        // When & Then
        try {
            stdDateFormat.parseAsISO8601("X%fcJJs5<=-B=b(2", null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testParseAsISO8601WithNullPositionR() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = StdDateFormat.instance;

        // When & Then
        try {
            stdDateFormat.parseAsISO8601("R%n+'d", null);
            fail("Expecting exception: StringIndexOutOfBoundsException");
        } catch (StringIndexOutOfBoundsException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testParseAsISO8601WithNullPositionColon() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = StdDateFormat.instance;

        // When & Then
        try {
            stdDateFormat.parseAsISO8601(":J+r:9s", null);
            fail("Expecting exception: StringIndexOutOfBoundsException");
        } catch (StringIndexOutOfBoundsException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testParseAsISO8601WithNullPosition9ASM() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = StdDateFormat.instance;

        // When & Then
        try {
            stdDateFormat.parseAsISO8601("9ASM4d<b9[CDv:[qZ", null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testParseWithMockDate() throws Throwable {
        // Given
        MockDate mockDate = new MockDate(696, 696, -585);
        StdDateFormat stdDateFormat = StdDateFormat.instance;
        ParsePosition parsePosition = new ParsePosition(696);

        // When
        stdDateFormat.parse("L", parsePosition);
        stdDateFormat.parseAsISO8601("yyyy-MM-dd'T'HH:mm:ss.SSSZ", parsePosition);
        stdDateFormat.parse("yyyy-MM-dd'T'HH:mm:ss.SSSZ", parsePosition);
        System.setCurrentTimeMillis(0L);

        // Then
        // No exception expected
    }

    @Test(timeout = 4000)
    public void testParseAsISO8601WithValidString() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = StdDateFormat.instance;
        ParsePosition parsePosition = new ParsePosition(696);

        // When
        Date date = stdDateFormat.parseAsISO8601("yyyy-MM-dd'T'HH:mm:ss.SSSZ", parsePosition);

        // Then
        assertNull("Expected null when parsing a valid ISO8601 string with incorrect position", date);
    }

    @Test(timeout = 4000)
    public void testParseAsISO8601WithNullPosition8() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = StdDateFormat.instance;

        // When & Then
        try {
            stdDateFormat.parseAsISO8601("8", null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testParseWithInvalidString() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = new StdDateFormat();

        // When & Then
        try {
            stdDateFormat.parse("6Vv9WHnf7:k");
            fail("Expecting exception: ParseException");
        } catch (ParseException e) {
            verifyException("com.fasterxml.jackson.databind.util.StdDateFormat", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseWithAnotherInvalidString() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = new StdDateFormat();

        // When & Then
        try {
            stdDateFormat.parse("2mv`46p#1_");
            fail("Expecting exception: ParseException");
        } catch (ParseException e) {
            verifyException("com.fasterxml.jackson.databind.util.StdDateFormat", e);
        }
    }

    @Test(timeout = 4000)
    public void testInstanceToString() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = new StdDateFormat();

        // When
        String result = stdDateFormat.instance.toString();

        // Then
        assertEquals("Expected specific string representation", 
            "DateFormat com.fasterxml.jackson.databind.util.StdDateFormat(locale: en_US)", 
            result);
    }

    @Test(timeout = 4000)
    public void testParseWithNoClassDefFoundError() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = new StdDateFormat();

        // When & Then
        try {
            stdDateFormat.parse("00");
            fail("Expecting exception: NoClassDefFoundError");
        } catch (NoClassDefFoundError e) {
            verifyException("com.fasterxml.jackson.databind.util.StdDateFormat", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseValidISO8601Date() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = StdDateFormat.instance;

        // When
        Date date = stdDateFormat.parse("2014-02-14T20:21:21.320+0000");

        // Then
        assertEquals("Expected specific date string", "Fri Feb 14 20:21:21 GMT 2014", date.toString());
    }

    @Test(timeout = 4000)
    public void testParseNegativeDate() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = StdDateFormat.instance;

        // When
        Date date = stdDateFormat.parse("-3");

        // Then
        assertEquals("Expected specific date string", "Wed Dec 31 23:59:59 GMT 1969", date.toString());
    }

    @Test(timeout = 4000)
    public void testSetTimeZone() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = new StdDateFormat();
        TimeZone timeZone = StdDateFormat.getDefaultTimeZone();

        // When
        stdDateFormat.setTimeZone(timeZone);

        // Then
        assertEquals("Expected default time zone ID", DEFAULT_TIMEZONE_ID, timeZone.getID());
    }

    @Test(timeout = 4000)
    public void testSetTimeZoneWithCustomTimeZone() throws Throwable {
        // Given
        TimeZone timeZone = TimeZone.getTimeZone("$IO0|u+c-rZ}");
        Locale locale = Locale.KOREA;
        StdDateFormat stdDateFormat = new StdDateFormat(timeZone, locale);

        // When
        stdDateFormat.setTimeZone(timeZone);

        // Then
        assertEquals("Expected default time zone ID", DEFAULT_TIMEZONE_ID, timeZone.getID());
    }

    @Test(timeout = 4000)
    public void testWithLocaleReturnsSameInstance() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = StdDateFormat.instance;
        Locale locale = Locale.US;

        // When
        StdDateFormat result = stdDateFormat.withLocale(locale);

        // Then
        assertSame("Expected the same instance when setting the same locale", stdDateFormat, result);
    }

    @Test(timeout = 4000)
    public void testParseWithInvalidPosition() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = StdDateFormat.instance;
        Locale locale = Locale.JAPANESE;
        StdDateFormat result = stdDateFormat.withLocale(locale);
        ParsePosition parsePosition = new ParsePosition(-796);

        // When & Then
        try {
            result.parse("2002-02-02T00:00:00.000+0000", parsePosition);
            fail("Expecting exception: StringIndexOutOfBoundsException");
        } catch (StringIndexOutOfBoundsException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testGetBlueprintISO8601Format() throws Throwable {
        // When
        MockSimpleDateFormat mockSimpleDateFormat = (MockSimpleDateFormat) StdDateFormat.getBlueprintISO8601Format();

        // Then
        assertEquals("Expected ISO8601 pattern", ISO8601_PATTERN, mockSimpleDateFormat.toPattern());
    }

    @Test(timeout = 4000)
    public void testGetRFC1123FormatWithDefaultTimeZone() throws Throwable {
        // Given
        TimeZone timeZone = StdDateFormat.getDefaultTimeZone();

        // When
        MockSimpleDateFormat mockSimpleDateFormat = (MockSimpleDateFormat) StdDateFormat.getRFC1123Format(timeZone);

        // Then
        assertEquals("Expected RFC1123 pattern", RFC1123_PATTERN, mockSimpleDateFormat.toPattern());
    }

    @Test(timeout = 4000)
    public void testGetISO8601FormatWithDefaultTimeZone() throws Throwable {
        // Given
        TimeZone timeZone = StdDateFormat.getDefaultTimeZone();

        // When
        MockSimpleDateFormat mockSimpleDateFormat = (MockSimpleDateFormat) StdDateFormat.getISO8601Format(timeZone);

        // Then
        assertEquals("Expected ISO8601 pattern", ISO8601_PATTERN, mockSimpleDateFormat.toPattern());
    }

    @Test(timeout = 4000)
    public void testGetBlueprintRFC1123Format() throws Throwable {
        // When
        DateFormat dateFormat = StdDateFormat.getBlueprintRFC1123Format();

        // Then
        assertTrue("Expected lenient date format", dateFormat.isLenient());
    }

    @Test(timeout = 4000)
    public void testClone() throws Throwable {
        // Given
        StdDateFormat stdDateFormat = new StdDateFormat();

        // When
        StdDateFormat clonedFormat = stdDateFormat.clone();

        // Then
        assertNotSame("Expected a different instance after cloning", clonedFormat, stdDateFormat);
    }