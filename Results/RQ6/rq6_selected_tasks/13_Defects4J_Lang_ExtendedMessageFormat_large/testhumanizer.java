private static final String INVALID_FORMAT_EXCEPTION_MESSAGE = "Invalid format argument index at position ";
    private static final String UNSUPPORTED_OPERATION_EXCEPTION_MESSAGE = "no message in exception (getMessage() returned null)";
    private static final String UNTERMINATED_FORMAT_EXCEPTION_MESSAGE = "Unterminated format element at position ";

    @Test(timeout = 4000)
    public void testPatternInitializationWithLocale() throws Throwable {
        // Given
        Locale locale = Locale.TAIWAN;

        // When
        ExtendedMessageFormat extendedMessageFormat = new ExtendedMessageFormat("Unreadable format element at position ", locale);

        // Then
        assertEquals("Pattern should match the initialized pattern", "Unreadable format element at position ", extendedMessageFormat.toPattern());
    }

    @Test(timeout = 4000)
    public void testInvalidFormatArgumentIndexException1() throws Throwable {
        // Given
        HashMap<MessageFormat, Locale.LanguageRange> registry = new HashMap<>();

        // When & Then
        try {
            new ExtendedMessageFormat("&{ .q679,''mm$Wo", registry);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
            assertEquals(INVALID_FORMAT_EXCEPTION_MESSAGE + "2:  .", e.getMessage());
        }
    }

    @Test(timeout = 4000)
    public void testInvalidFormatArgumentIndexException2() throws Throwable {
        // Given
        HashMap<Object, MessageFormat> registry = new HashMap<>();
        Locale locale = Locale.FRENCH;

        // When & Then
        try {
            new ExtendedMessageFormat("A^{}1`w;W/Q", locale, registry);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
            assertEquals(INVALID_FORMAT_EXCEPTION_MESSAGE + "3: }", e.getMessage());
        }
    }

    @Test(timeout = 4000)
    public void testInvalidFormatArgumentIndexException3() throws Throwable {
        // Given
        HashMap<MessageFormat, Object> registry = new HashMap<>();

        // When & Then
        try {
            new ExtendedMessageFormat("eH{,W\n'uW1.6t", registry);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
            assertEquals(INVALID_FORMAT_EXCEPTION_MESSAGE + "3: ,", e.getMessage());
        }
    }

    @Test(timeout = 4000)
    public void testValidPatternWithRegistry() throws Throwable {
        // Given
        HashMap<MessageFormat, Object> registry = new HashMap<>();

        // When
        new ExtendedMessageFormat("j'O/-kQ5,((AnrH^_DD", registry);

        // Then
        // No exception expected
    }

    @Test(timeout = 4000)
    public void testUnsupportedSetFormatByArgumentIndex() throws Throwable {
        // Given
        Locale locale = Locale.ENGLISH;
        HashMap<Object, MessageFormat> registry = new HashMap<>();
        ExtendedMessageFormat extendedMessageFormat = new ExtendedMessageFormat("8a~", locale, registry);
        NumberFormat numberFormat = NumberFormat.getCurrencyInstance();

        // When & Then
        try {
            extendedMessageFormat.setFormatByArgumentIndex(-1209, numberFormat);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
            assertNull(UNSUPPORTED_OPERATION_EXCEPTION_MESSAGE, e.getMessage());
        }
    }

    @Test(timeout = 4000)
    public void testUnsupportedSetFormats() throws Throwable {
        // Given
        HashMap<MessageFormat, Object> registry = new HashMap<>();
        ExtendedMessageFormat extendedMessageFormat = new ExtendedMessageFormat("Uui*sdf!t@PftX", registry);

        // When & Then
        try {
            extendedMessageFormat.setFormats((Format[]) null);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
            assertNull(UNSUPPORTED_OPERATION_EXCEPTION_MESSAGE, e.getMessage());
        }
    }

    @Test(timeout = 4000)
    public void testPatternInitializationWithLocaleAndNullRegistry() throws Throwable {
        // Given
        Locale locale = new Locale(">FKFgdAL=t(X'*=!", "cPGUmleMLKv,");

        // When
        ExtendedMessageFormat extendedMessageFormat = new ExtendedMessageFormat(">FKFgdAL=t(X'*=!", locale, (Map) null);

        // Then
        assertEquals("Pattern should match the initialized pattern", ">FKFgdAL=t(X*=!", extendedMessageFormat.toPattern());
    }

    @Test(timeout = 4000)
    public void testUnsupportedSetFormat() throws Throwable {
        // Given
        HashMap<Locale.LanguageRange, Object> registry = new HashMap<>();
        ExtendedMessageFormat extendedMessageFormat = new ExtendedMessageFormat("2| /&4GR#", registry);
        DateFormat dateFormat = DateFormat.getTimeInstance();

        // When & Then
        try {
            extendedMessageFormat.setFormat(39, dateFormat);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
            assertNull(UNSUPPORTED_OPERATION_EXCEPTION_MESSAGE, e.getMessage());
        }
    }

    @Test(timeout = 4000)
    public void testPatternInitializationWithoutRegistry() throws Throwable {
        // Given & When
        new ExtendedMessageFormat("ZR@bK_a.(Lm5b\f?");

        // Then
        // No exception expected
    }

    @Test(timeout = 4000)
    public void testUnsupportedSetFormatsByArgumentIndex() throws Throwable {
        // Given
        HashMap<Object, Object> registry = new HashMap<>();
        ExtendedMessageFormat extendedMessageFormat = new ExtendedMessageFormat("[R", registry);
        Format[] formatArray = new Format[2];

        // When & Then
        try {
            extendedMessageFormat.setFormatsByArgumentIndex(formatArray);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
            assertNull(UNSUPPORTED_OPERATION_EXCEPTION_MESSAGE, e.getMessage());
        }
    }

    @Test(timeout = 4000)
    public void testApplyPatternThrowsIllegalArgumentException() throws Throwable {
        // Given
        HashMap<MessageFormat, Object> registry = new HashMap<>();
        ExtendedMessageFormat extendedMessageFormat = new ExtendedMessageFormat("", registry);

        // When & Then
        try {
            extendedMessageFormat.applyPattern("Lf-{06");
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.lang.text.ExtendedMessageFormat", e);
            assertEquals(UNTERMINATED_FORMAT_EXCEPTION_MESSAGE + "4", e.getMessage());
        }
    }