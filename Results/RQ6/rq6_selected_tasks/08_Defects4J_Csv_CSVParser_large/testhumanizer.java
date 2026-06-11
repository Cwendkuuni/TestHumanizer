@Test(timeout = 4000)
    public void testParseStringWithExcelFormat() throws Throwable {
        // Given: A CSV string and Excel format
        StringReader stringReader = new StringReader("UTF-8");
        CSVFormat format = CSVFormat.EXCEL;

        // When: Parsing the string
        CSVParser parser = format.parse(stringReader);
        CSVRecord record = parser.nextRecord();

        // Then: The record should match the expected output
        assertEquals("Record should match expected output", "[UTF-8]", record.toString());
    }

    @Test(timeout = 4000)
    public void testIteratorNotNull() throws Throwable {
        // Given: A CSV string and Excel format
        CSVFormat format = CSVFormat.EXCEL;

        // When: Parsing the string and getting the iterator
        CSVParser parser = CSVParser.parse("m(", format);
        Iterator<CSVRecord> iterator = parser.iterator();

        // Then: The iterator should not be null
        assertNotNull("Iterator should not be null", iterator);
    }

    @Test(timeout = 4000)
    public void testParserNotClosedInitially() throws Throwable {
        // Given: An empty CSV string and default format
        CSVFormat format = CSVFormat.DEFAULT;
        StringReader stringReader = new StringReader("");

        // When: Parsing the string
        CSVParser parser = format.parse(stringReader);

        // Then: The parser should not be closed initially
        assertFalse("Parser should not be closed initially", parser.isClosed());
    }

    @Test(timeout = 4000)
    public void testForEachThrowsRuntimeException() throws Throwable {
        // Given: A CSV string with unmatched quote and RFC4180 format
        CSVFormat format = CSVFormat.RFC4180.withQuoteChar('(');
        CSVParser parser = CSVParser.parse("('8ne ", format);
        Consumer<Object> consumer = mock(Consumer.class, new ViolatedAssumptionAnswer());

        // When & Then: Expecting a RuntimeException due to unmatched quote
        try {
            parser.forEach(consumer);
            fail("Expecting exception: RuntimeException");
        } catch (RuntimeException e) {
            verifyException("org.apache.commons.csv.CSVParser$1", e);
        }
    }

    @Test(timeout = 4000)
    public void testParseNonExistentFileThrowsFileNotFoundException() throws Throwable {
        // Given: A non-existent file and TDF format
        CSVFormat format = CSVFormat.TDF;
        MockFile mockFile = new MockFile("");

        // When & Then: Expecting a FileNotFoundException
        try {
            CSVParser.parse((File) mockFile, format);
            fail("Expecting exception: FileNotFoundException");
        } catch (FileNotFoundException e) {
            verifyException("org.evosuite.runtime.mock.java.io.MockFileInputStream", e);
        }
    }

    @Test(timeout = 4000)
    public void testForEachWithCommentStart() throws Throwable {
        // Given: A CSV string with comment start and default format
        CSVFormat format = CSVFormat.DEFAULT.withCommentStart('c');
        StringReader stringReader = new StringReader("charset");

        // When: Parsing the string and iterating over records
        CSVParser parser = format.parse(stringReader);
        Consumer<Object> consumer = mock(Consumer.class, new ViolatedAssumptionAnswer());
        parser.forEach(consumer);

        // Then: No records should be processed
        assertEquals("No records should be processed", 0L, parser.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testForEachWithNewLine() throws Throwable {
        // Given: A CSV string with new line and RFC4180 format
        CSVFormat format = CSVFormat.RFC4180;
        StringReader stringReader = new StringReader("\r\n");

        // When: Parsing the string and iterating over records
        CSVParser parser = format.parse(stringReader);
        Consumer<Object> consumer = mock(Consumer.class, new ViolatedAssumptionAnswer());
        parser.forEach(consumer);

        // Then: One record should be processed
        assertEquals("One record should be processed", 1L, parser.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testForEachAfterClose() throws Throwable {
        // Given: An empty CSV string and default format
        CSVFormat format = CSVFormat.DEFAULT;
        StringReader stringReader = new StringReader("");

        // When: Parsing the string, closing the parser, and iterating over records
        CSVParser parser = format.parse(stringReader);
        parser.close();
        Consumer<Object> consumer = mock(Consumer.class, new ViolatedAssumptionAnswer());
        parser.forEach(consumer);

        // Then: No records should be processed
        assertEquals("No records should be processed", 0L, parser.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testParseWithHeaderAndQuoteChar() throws Throwable {
        // Given: A CSV string with header and quote char
        CSVFormat format = CSVFormat.DEFAULT.withSkipHeaderRecord(true).withQuoteChar('#').withHeader(new String[1]);
        StringReader stringReader = new StringReader("$OOiSsDELB2R");

        // When: Parsing the string
        CSVParser parser = format.parse(stringReader);

        // Then: One record should be processed
        assertEquals("One record should be processed", 1L, parser.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testParseWithEmptyHeader() throws Throwable {
        // Given: An empty CSV string and Excel format with empty header
        CSVFormat format = CSVFormat.EXCEL.withHeader(new String[0]);
        StringReader stringReader = new StringReader("");

        // When: Parsing the string
        CSVParser parser = new CSVParser(stringReader, format);

        // Then: No records should be processed
        assertEquals("No records should be processed", 0L, parser.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testParseWithDelimiterAndQuoteChar() throws Throwable {
        // Given: A CSV string with delimiter and quote char
        CSVFormat format = CSVFormat.DEFAULT.withHeader(new String[0]);
        String csvString = "Delimiter=<,> QuoteChar=<d> RecordSeparator=<> EmptyLines:ignored SkipHeaderRecord:false";

        // When: Parsing the string
        CSVParser parser = CSVParser.parse(csvString, format);

        // Then: One record should be processed
        assertEquals("One record should be processed", 1L, parser.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testParseWithHeaderAndUTF8String() throws Throwable {
        // Given: A CSV string with UTF-8 and Excel format with header
        StringReader stringReader = new StringReader("UTF-8");
        CSVFormat format = CSVFormat.EXCEL.withHeader(new String[1]);

        // When: Parsing the string
        CSVParser parser = format.parse(stringReader);

        // Then: No records should be processed
        assertEquals("No records should be processed", 0L, parser.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testGetRecordsIncrementsRecordNumber() throws Throwable {
        // Given: A CSV string and default format
        CSVFormat format = CSVFormat.DEFAULT;
        String csvString = "WDUEX^G\"\"aeRt";

        // When: Parsing the string and getting records
        CSVParser parser = CSVParser.parse(csvString, format);
        parser.getRecords();

        // Then: One record should be processed
        assertEquals("One record should be processed", 1L, parser.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testForEachWithNullString() throws Throwable {
        // Given: A CSV string and Excel format with null string
        StringReader stringReader = new StringReader("UTF-8");
        stringReader.read();
        CSVFormat format = CSVFormat.EXCEL.withNullString("UTF-8");

        // When: Parsing the string and iterating over records
        CSVParser parser = format.parse(stringReader);
        Consumer<Object> consumer = mock(Consumer.class, new ViolatedAssumptionAnswer());
        parser.forEach(consumer);

        // Then: One record should be processed
        assertEquals("One record should be processed", 1L, parser.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testParseURLWithExcelFormat() throws Throwable {
        // Given: A URL and Excel format
        CSVFormat format = CSVFormat.EXCEL;
        EvoSuiteURL evoSuiteURL = new EvoSuiteURL("http://www.someFakeButWellFormedURL.org/fooExample");
        NetworkHandling.createRemoteTextFile(evoSuiteURL, "`rM;hXp2u?Dx ");
        URL url = MockURL.getHttpExample();
        Charset charset = Charset.forName("UTF-8");

        // When: Parsing the URL
        CSVParser parser = CSVParser.parse(url, charset, format);

        // Then: No records should be processed
        assertEquals("No records should be processed", 0L, parser.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testGetHeaderMapThrowsNullPointerException() throws Throwable {
        // Given: A CSV string and TDF format
        CSVFormat format = CSVFormat.TDF;
        CSVParser parser = CSVParser.parse("Z\"FHS3K1omEH'Oieu:~", format);

        // When & Then: Expecting a NullPointerException
        try {
            parser.getHeaderMap();
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testGetRecordNumberInitiallyZero() throws Throwable {
        // Given: A CSV string and Excel format
        CSVFormat format = CSVFormat.EXCEL;
        CSVParser parser = CSVParser.parse("m(", format);

        // When: Getting the record number
        long recordNumber = parser.getRecordNumber();

        // Then: The record number should be zero initially
        assertEquals("Record number should be zero initially", 0L, recordNumber);
    }

    @Test(timeout = 4000)
    public void testGetCurrentLineNumberInitiallyZero() throws Throwable {
        // Given: An empty CSV string and default format
        CSVFormat format = CSVFormat.DEFAULT;
        StringReader stringReader = new StringReader("");

        // When: Parsing the string and getting the current line number
        CSVParser parser = format.parse(stringReader);
        long lineNumber = parser.getCurrentLineNumber();

        // Then: The current line number should be zero initially
        assertEquals("Current line number should be zero initially", 0L, lineNumber);
    }