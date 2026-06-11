// Constants for test strings
    private static final String INVALID_DATE_STRING_1 = "61982-11-01T00:00:00.000Z";
    private static final String INVALID_DATE_STRING_2 = "Sm %(=4jp 4U";
    private static final String INVALID_DATE_STRING_3 = "qJ,`&&xs/";
    private static final String INVALID_DATE_STRING_4 = "+0000";
    private static final String INVALID_DATE_STRING_5 = "";
    private static final String INVALID_DATE_STRING_6 = "208770102-06-02T17:13:34Z";
    private static final String INVALID_DATE_STRING_7 = "248768-08-14T06:31:16.000Z";
    private static final String VALID_DATE_STRING_1 = "2014-02-14T20:21:21Z";
    private static final String VALID_DATE_STRING_2 = "2014-02-14T20:21:21.320Z";

    @Test(timeout = 4000)
    public void testParseInvalidDateString1() throws Throwable {
        // Given
        ParsePosition parsePosition = new ParsePosition(0);

        // When & Then
        try {
            ISO8601Utils.parse(INVALID_DATE_STRING_1, parsePosition);
            fail("Expecting exception: ParseException");
        } catch (ParseException e) {
            verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseInvalidDateString2() throws Throwable {
        // Given
        ParsePosition parsePosition = new ParsePosition(1);

        // When & Then
        try {
            ISO8601Utils.parse(INVALID_DATE_STRING_2, parsePosition);
            fail("Expecting exception: ParseException");
        } catch (ParseException e) {
            verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseInvalidDateString3() throws Throwable {
        // Given
        ParsePosition parsePosition = new ParsePosition(2147483645);

        // When & Then
        try {
            ISO8601Utils.parse(INVALID_DATE_STRING_3, parsePosition);
            fail("Expecting exception: ParseException");
        } catch (ParseException e) {
            verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseInvalidDateString4() throws Throwable {
        // Given
        ParsePosition parsePosition = new ParsePosition(1);

        // When & Then
        try {
            ISO8601Utils.parse(INVALID_DATE_STRING_4, parsePosition);
            fail("Expecting exception: ParseException");
        } catch (ParseException e) {
            verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseEmptyString() throws Throwable {
        // Given
        ParsePosition parsePosition = new ParsePosition(0);

        // When & Then
        try {
            ISO8601Utils.parse(INVALID_DATE_STRING_5, parsePosition);
            fail("Expecting exception: ParseException");
        } catch (ParseException e) {
            verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseNullString() throws Throwable {
        // Given
        ParsePosition parsePosition = new ParsePosition(-1483);

        // When & Then
        try {
            ISO8601Utils.parse(null, parsePosition);
            fail("Expecting exception: ParseException");
        } catch (ParseException e) {
            verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseValidDateString1() throws Throwable {
        // Given
        ParsePosition parsePosition = new ParsePosition(0);

        // When
        Date date = ISO8601Utils.parse(VALID_DATE_STRING_1, parsePosition);

        // Then
        assertEquals("Fri Feb 14 20:21:21 GMT 2014", date.toString());
    }

    @Test(timeout = 4000)
    public void testParseInvalidDateString6() throws Throwable {
        // Given
        ParsePosition parsePosition = new ParsePosition(0);

        // When & Then
        try {
            ISO8601Utils.parse(INVALID_DATE_STRING_6, parsePosition);
            fail("Expecting exception: ParseException");
        } catch (ParseException e) {
            verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseValidDateString2() throws Throwable {
        // Given
        ParsePosition parsePosition = new ParsePosition(0);

        // When
        Date date = ISO8601Utils.parse(VALID_DATE_STRING_2, parsePosition);

        // Then
        assertEquals("Fri Feb 14 20:21:21 GMT 2014", date.toString());
    }

    @Test(timeout = 4000)
    public void testParseInvalidDateString7() throws Throwable {
        // Given
        ParsePosition parsePosition = new ParsePosition(0);

        // When & Then
        try {
            ISO8601Utils.parse(INVALID_DATE_STRING_7, parsePosition);
            fail("Expecting exception: ParseException");
        } catch (ParseException e) {
            verifyException("com.google.gson.internal.bind.util.ISO8601Utils", e);
        }
    }

    @Test(timeout = 4000)
    public void testFormatDateWithMillisecondsAndTimezone() throws Throwable {
        // Given
        MockDate mockDate = new MockDate(-2685, -2685, -2685);
        SimpleTimeZone simpleTimeZone = new SimpleTimeZone(-2685, "1018-11-23T00:00:00Z");

        // When
        String formattedDate = ISO8601Utils.format(mockDate, true, simpleTimeZone);

        // Then
        assertEquals("1018-11-22T23:59:57.315-00:00", formattedDate);
    }

    @Test(timeout = 4000)
    public void testFormatDateWithMillisecondsAndTimezone2() throws Throwable {
        // Given
        MockDate mockDate = new MockDate(1, 1, 1);
        SimpleTimeZone simpleTimeZone = new SimpleTimeZone(1, "1901-02-01T00:00:00.000Z");

        // When
        String formattedDate = ISO8601Utils.format(mockDate, true, simpleTimeZone);

        // Then
        assertEquals("1901-02-01T00:00:00.001+00:00", formattedDate);
    }

    @Test(timeout = 4000)
    public void testFormatDateWithMilliseconds() throws Throwable {
        // Given
        MockDate mockDate = new MockDate();

        // When
        String formattedDate = ISO8601Utils.format(mockDate, true);

        // Then
        assertEquals("2014-02-14T20:21:21.320Z", formattedDate);
    }

    @Test(timeout = 4000)
    public void testISO8601UtilsConstructor() throws Throwable {
        // Given & When
        ISO8601Utils iso8601Utils = new ISO8601Utils();

        // Then
        assertNotNull(iso8601Utils);
    }

    @Test(timeout = 4000)
    public void testFormatDate() throws Throwable {
        // Given
        MockDate mockDate = new MockDate(50, 2147483645, -2024, 2147483645, 50, 1356);

        // When
        String formattedDate = ISO8601Utils.format(mockDate);

        // Then
        assertEquals("179203898-08-23T06:12:36Z", formattedDate);
    }