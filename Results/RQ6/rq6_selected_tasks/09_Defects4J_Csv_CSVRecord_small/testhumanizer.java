private static final long RECORD_NUMBER_NEGATIVE_2203 = -2203L;
    private static final long RECORD_NUMBER_ZERO = 0L;
    private static final long RECORD_NUMBER_NEGATIVE_11 = -11L;
    private static final String COMMENT_SAMPLE = "Hi6wv?h8*v/P";
    private static final String COMMENT_EMPTY = "";
    private static final String COMMENT_NULL = null;
    private static final String COLUMN_NAME_EMPTY = "";
    private static final String COLUMN_NAME_NULL = null;
    private static final String COLUMN_NAME_SAMPLE = "},BHK<rd0#x7u@Tv?Do";
    private static final int INDEX_NEGATIVE_1084 = -1084;
    private static final int INDEX_NEGATIVE_638 = -638;
    private static final int INDEX_ONE = 1;

    @Test(timeout = 4000)
    public void testIteratorAndGetRecordNumber() throws Throwable {
        // Given
        String[] values = new String[3];
        HashMap<String, Integer> mapping = new HashMap<>();
        CSVRecord record = new CSVRecord(values, mapping, COMMENT_SAMPLE, RECORD_NUMBER_NEGATIVE_2203);

        // When
        record.iterator();

        // Then
        assertEquals("Record number should be -2203", RECORD_NUMBER_NEGATIVE_2203, record.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testIsSetWithEmptyColumnName() throws Throwable {
        // Given
        String[] values = new String[7];
        HashMap<String, Integer> mapping = new HashMap<>();
        CSVRecord record = new CSVRecord(values, mapping, "l", RECORD_NUMBER_NEGATIVE_11);
        mapping.put(COLUMN_NAME_EMPTY, 1701);

        // When
        boolean isSet = record.isSet(COLUMN_NAME_EMPTY);

        // Then
        assertFalse("Column should not be set", isSet);
        assertEquals("Record number should be -11", RECORD_NUMBER_NEGATIVE_11, record.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testIsSetWithNullColumnName() throws Throwable {
        // Given
        HashMap<String, Integer> mapping = new HashMap<>();
        mapping.put(COLUMN_NAME_NULL, INDEX_NEGATIVE_1084);
        CSVRecord record = new CSVRecord(null, mapping, COMMENT_NULL, RECORD_NUMBER_ZERO);

        // When
        boolean isSet = record.isSet(COLUMN_NAME_NULL);

        // Then
        assertTrue("Column should be set", isSet);
    }

    @Test(timeout = 4000)
    public void testIsMappedWithEmptyColumnName() throws Throwable {
        // Given
        String[] values = new String[3];
        HashMap<String, Integer> mapping = new HashMap<>();
        mapping.put(COLUMN_NAME_EMPTY, INDEX_ONE);
        CSVRecord record = new CSVRecord(values, mapping, COMMENT_SAMPLE, RECORD_NUMBER_NEGATIVE_2203);

        // When
        boolean isMapped = record.isMapped(COLUMN_NAME_EMPTY);

        // Then
        assertTrue("Column should be mapped", isMapped);
        assertEquals("Record number should be -2203", RECORD_NUMBER_NEGATIVE_2203, record.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testIsMappedWithEmptyColumnNameNotMapped() throws Throwable {
        // Given
        String[] values = new String[3];
        HashMap<String, Integer> mapping = new HashMap<>();
        CSVRecord record = new CSVRecord(values, mapping, COMMENT_SAMPLE, RECORD_NUMBER_NEGATIVE_2203);

        // When
        boolean isMapped = record.isMapped(COLUMN_NAME_EMPTY);

        // Then
        assertFalse("Column should not be mapped", isMapped);
        assertEquals("Record number should be -2203", RECORD_NUMBER_NEGATIVE_2203, record.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testIsSetWithNullMapping() throws Throwable {
        // Given
        String[] values = new String[2];
        CSVRecord record = new CSVRecord(values, null, COMMENT_EMPTY, RECORD_NUMBER_ZERO);

        // When
        boolean isSet = record.isSet(COLUMN_NAME_NULL);

        // Then
        assertFalse("Column should not be set", isSet);
    }

    @Test(timeout = 4000)
    public void testIsConsistentWithInconsistentRecord() throws Throwable {
        // Given
        String[] values = new String[1];
        HashMap<String, Integer> mapping = new HashMap<>();
        CSVRecord record = new CSVRecord(values, mapping, COLUMN_NAME_SAMPLE, RECORD_NUMBER_ZERO);

        // When
        boolean isConsistentBefore = record.isConsistent();
        mapping.put(COLUMN_NAME_SAMPLE, INDEX_NEGATIVE_638);
        boolean isConsistentAfter = record.isConsistent();

        // Then
        assertFalse("Record should be inconsistent before adding mapping", isConsistentBefore);
        assertTrue("Record should be consistent after adding mapping", isConsistentAfter);
    }

    @Test(timeout = 4000)
    public void testIsConsistentWithNullMapping() throws Throwable {
        // Given
        String[] values = new String[8];
        CSVRecord record = new CSVRecord(values, null, COMMENT_EMPTY, RECORD_NUMBER_ZERO);

        // When
        boolean isConsistent = record.isConsistent();

        // Then
        assertTrue("Record should be consistent", isConsistent);
    }

    @Test(timeout = 4000)
    public void testIsConsistentWithInconsistentMapping() throws Throwable {
        // Given
        String[] values = new String[3];
        HashMap<String, Integer> mapping = new HashMap<>();
        CSVRecord record = new CSVRecord(values, mapping, COMMENT_SAMPLE, RECORD_NUMBER_NEGATIVE_2203);

        // When
        boolean isConsistent = record.isConsistent();

        // Then
        assertFalse("Record should be inconsistent", isConsistent);
        assertEquals("Record number should be -2203", RECORD_NUMBER_NEGATIVE_2203, record.getRecordNumber());
    }

    @Test(timeout = 4000)
    public void testGetWithNullColumnNameThrowsException() throws Throwable {
        // Given
        HashMap<String, Integer> mapping = new HashMap<>();
        mapping.put(COLUMN_NAME_NULL, INDEX_NEGATIVE_1084);
        CSVRecord record = new CSVRecord(null, mapping, COMMENT_NULL, RECORD_NUMBER_ZERO);

        // When & Then
        try {
            record.get(COLUMN_NAME_NULL);
            fail("Expecting exception: ArrayIndexOutOfBoundsException");
        } catch (ArrayIndexOutOfBoundsException e) {
            verifyException("org.apache.commons.csv.CSVRecord", e);
        }
    }

    @Test(timeout = 4000)
    public void testGetWithUnmappedColumnNameThrowsException() throws Throwable {
        // Given
        String[] values = new String[8];
        CSVRecord record = new CSVRecord(values, null, COMMENT_EMPTY, RECORD_NUMBER_ZERO);

        // When & Then
        try {
            record.get("org.apache.commons.csv.CSVRecord");
            fail("Expecting exception: IllegalStateException");
        } catch (IllegalStateException e) {
            verifyException("org.apache.commons.csv.CSVRecord", e);
        }
    }

    @Test(timeout = 4000)
    public void testGetWithUnmappedColumnNameReturnsNull() throws Throwable {
        // Given
        HashMap<String, Integer> mapping = new HashMap<>();
        CSVRecord record = new CSVRecord(null, mapping, COMMENT_NULL, RECORD_NUMBER_ZERO);

        // When
        String result = record.get("x}4H^468:{u");

        // Then
        assertNull("Result should be null", result);
    }

    @Test(timeout = 4000)
    public void testSizeWithNullValues() throws Throwable {
        // Given
        HashMap<String, Integer> mapping = new HashMap<>();
        CSVRecord record = new CSVRecord(null, mapping, "BJ,o", RECORD_NUMBER_ZERO);

        // When
        int size = record.size();

        // Then
        assertEquals("Size should be 0", 0, size);
    }

    @Test(timeout = 4000)
    public void testGetRecordNumberAndToString() throws Throwable {
        // Given
        HashMap<String, Integer> mapping = new HashMap<>();
        CSVRecord record = new CSVRecord(null, mapping, COMMENT_NULL, RECORD_NUMBER_ZERO);

        // When
        long recordNumber = record.getRecordNumber();
        String recordString = record.toString();

        // Then
        assertEquals("Record number should be 0", RECORD_NUMBER_ZERO, recordNumber);
        assertEquals("String representation should be empty array", "[]", recordString);
    }

    @Test(timeout = 4000)
    public void testGetWithIndexThrowsException() throws Throwable {
        // Given
        HashMap<String, Integer> mapping = new HashMap<>();
        CSVRecord record = new CSVRecord(null, mapping, "BJ,o", RECORD_NUMBER_ZERO);

        // When & Then
        try {
            record.get(0);
            fail("Expecting exception: ArrayIndexOutOfBoundsException");
        } catch (ArrayIndexOutOfBoundsException e) {
            verifyException("org.apache.commons.csv.CSVRecord", e);
        }
    }

    @Test(timeout = 4000)
    public void testValuesWithNullValues() throws Throwable {
        // Given
        HashMap<String, Integer> mapping = new HashMap<>();
        CSVRecord record = new CSVRecord(null, mapping, COMMENT_NULL, RECORD_NUMBER_ZERO);

        // When
        String[] values = record.values();

        // Then
        assertNotNull("Values should not be null", values);
        assertEquals("String representation should be empty array", "[]", record.toString());
    }

    @Test(timeout = 4000)
    public void testToStringWithNullValues() throws Throwable {
        // Given
        HashMap<String, Integer> mapping = new HashMap<>();
        CSVRecord record = new CSVRecord(null, mapping, COMMENT_NULL, RECORD_NUMBER_ZERO);

        // When
        String recordString = record.toString();

        // Then
        assertEquals("String representation should be empty array", "[]", recordString);
    }

    @Test(timeout = 4000)
    public void testGetCommentAndIsConsistent() throws Throwable {
        // Given
        String[] values = new String[4];
        HashMap<String, Integer> mapping = new HashMap<>();
        CSVRecord record = new CSVRecord(values, mapping, "F=@n>7HkuXom*g", RECORD_NUMBER_ZERO);

        // When
        String comment = record.getComment();
        boolean isConsistent = record.isConsistent();

        // Then
        assertEquals("Comment should match", "F=@n>7HkuXom*g", comment);
        assertFalse("Record should be inconsistent", isConsistent);
    }