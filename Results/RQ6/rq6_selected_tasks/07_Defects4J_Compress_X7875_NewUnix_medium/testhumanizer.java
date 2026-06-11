private static final long DEFAULT_UID_GID = 1000L;
    private static final int LOCAL_FILE_DATA_LENGTH = 7;
    private static final int CENTRAL_DIRECTORY_LENGTH = 7;
    private static final int HEADER_ID_VALUE = 30837;
    private static final byte[] EXPECTED_LOCAL_FILE_DATA = {(byte)1, (byte)2, (byte)(-24), (byte)3, (byte)2, (byte)(-24), (byte)3};

    @Test(timeout = 4000)
    public void testGetLocalFileDataLength() throws Throwable {
        // Given: A new instance of X7875_NewUnix
        X7875_NewUnix x7875_NewUnix = new X7875_NewUnix();

        // When: Retrieving the local file data length
        ZipShort zipShort = x7875_NewUnix.getLocalFileDataLength();

        // Then: The length should be 7
        assertEquals("Local file data length should be 7", LOCAL_FILE_DATA_LENGTH, zipShort.getValue());
    }

    @Test(timeout = 4000)
    public void testTrimLeadingZeroesForceMinLengthWithNull() throws Throwable {
        // Given: A null byte array

        // When: Trimming leading zeroes
        byte[] result = X7875_NewUnix.trimLeadingZeroesForceMinLength(null);

        // Then: The result should be null
        assertNull("Result should be null for null input", result);
    }

    @Test(timeout = 4000)
    public void testEqualsWithDifferentUID() throws Throwable {
        // Given: Two instances of X7875_NewUnix
        X7875_NewUnix x7875_NewUnix1 = new X7875_NewUnix();
        X7875_NewUnix x7875_NewUnix2 = new X7875_NewUnix();

        // When: Setting a different UID on the second instance
        x7875_NewUnix2.setUID(134695760L);

        // Then: The two instances should not be equal
        assertFalse("Instances should not be equal after setting different UID", x7875_NewUnix1.equals(x7875_NewUnix2));
    }

    @Test(timeout = 4000)
    public void testParseFromLocalFileData() throws Throwable {
        // Given: Two instances of X7875_NewUnix and a byte array
        X7875_NewUnix x7875_NewUnix1 = new X7875_NewUnix();
        X7875_NewUnix x7875_NewUnix2 = new X7875_NewUnix();
        byte[] byteArray = new byte[8];

        // When: Parsing local file data with specific offset and length
        x7875_NewUnix2.parseFromLocalFileData(byteArray, (byte)5, (-128));

        // Then: The two instances should not be equal
        assertFalse("Instances should not be equal after parsing different data", x7875_NewUnix1.equals(x7875_NewUnix2));
    }

    @Test(timeout = 4000)
    public void testEqualsWithSameInstance() throws Throwable {
        // Given: An instance of X7875_NewUnix
        X7875_NewUnix x7875_NewUnix = new X7875_NewUnix();

        // When: Comparing the instance with itself
        boolean isEqual = x7875_NewUnix.equals(x7875_NewUnix);

        // Then: The instance should be equal to itself
        assertTrue("Instance should be equal to itself", isEqual);
    }

    @Test(timeout = 4000)
    public void testEqualsWithNull() throws Throwable {
        // Given: An instance of X7875_NewUnix
        X7875_NewUnix x7875_NewUnix = new X7875_NewUnix();

        // When: Comparing the instance with null
        boolean isEqual = x7875_NewUnix.equals(null);

        // Then: The instance should not be equal to null
        assertFalse("Instance should not be equal to null", isEqual);
    }

    @Test(timeout = 4000)
    public void testParseFromCentralDirectoryData() throws Throwable {
        // Given: An instance of X7875_NewUnix and a byte array
        X7875_NewUnix x7875_NewUnix = new X7875_NewUnix();
        byte[] byteArray = new byte[8];

        // When: Parsing central directory data
        x7875_NewUnix.parseFromCentralDirectoryData(byteArray, (byte)59, 0);

        // Then: The byte array length should remain 8
        assertEquals("Byte array length should be 8", 8, byteArray.length);
    }

    @Test(timeout = 4000)
    public void testGetGID() throws Throwable {
        // Given: A new instance of X7875_NewUnix
        X7875_NewUnix x7875_NewUnix = new X7875_NewUnix();

        // When: Retrieving the GID
        long gid = x7875_NewUnix.getGID();

        // Then: The GID should be the default value
        assertEquals("GID should be the default value", DEFAULT_UID_GID, gid);
    }

    @Test(timeout = 4000)
    public void testHashCode() throws Throwable {
        // Given: A new instance of X7875_NewUnix
        X7875_NewUnix x7875_NewUnix = new X7875_NewUnix();

        // When: Calculating the hash code
        int hashCode = x7875_NewUnix.hashCode();

        // Then: The hash code should be calculated without exceptions
        assertNotNull("Hash code should be calculated", hashCode);
    }

    @Test(timeout = 4000)
    public void testGetCentralDirectoryData() throws Throwable {
        // Given: A new instance of X7875_NewUnix
        X7875_NewUnix x7875_NewUnix = new X7875_NewUnix();

        // When: Retrieving the central directory data
        byte[] data = x7875_NewUnix.getCentralDirectoryData();

        // Then: The data should be an empty array
        assertEquals("Central directory data should be empty", 0, data.length);
    }

    @Test(timeout = 4000)
    public void testGetHeaderId() throws Throwable {
        // Given: A new instance of X7875_NewUnix
        X7875_NewUnix x7875_NewUnix = new X7875_NewUnix();

        // When: Retrieving the header ID
        ZipShort headerId = x7875_NewUnix.getHeaderId();

        // Then: The header ID should match the expected value
        assertEquals("Header ID should match expected value", HEADER_ID_VALUE, headerId.getValue());
    }

    @Test(timeout = 4000)
    public void testGetCentralDirectoryLength() throws Throwable {
        // Given: A new instance of X7875_NewUnix
        X7875_NewUnix x7875_NewUnix = new X7875_NewUnix();

        // When: Retrieving the central directory length
        ZipShort length = x7875_NewUnix.getCentralDirectoryLength();

        // Then: The length should be 7
        assertEquals("Central directory length should be 7", CENTRAL_DIRECTORY_LENGTH, length.getValue());
    }

    @Test(timeout = 4000)
    public void testCloneAndModifyGID() throws Throwable {
        // Given: A new instance of X7875_NewUnix
        X7875_NewUnix x7875_NewUnix = new X7875_NewUnix();

        // When: Cloning and modifying the GID
        X7875_NewUnix cloned = (X7875_NewUnix) x7875_NewUnix.clone();
        cloned.setGID(3113L);

        // Then: The original and cloned instances should not be equal
        assertFalse("Original and cloned instances should not be equal after modifying GID", x7875_NewUnix.equals(cloned));
    }

    @Test(timeout = 4000)
    public void testSetGIDAndGetCentralDirectoryLength() throws Throwable {
        // Given: A new instance of X7875_NewUnix
        X7875_NewUnix x7875_NewUnix = new X7875_NewUnix();

        // When: Setting GID to 0 and retrieving central directory length
        x7875_NewUnix.setGID(0L);
        ZipShort length = x7875_NewUnix.getCentralDirectoryLength();

        // Then: The length should be 6
        assertEquals("Central directory length should be 6 after setting GID to 0", 6, length.getValue());
    }

    @Test(timeout = 4000)
    public void testGetLocalFileDataData() throws Throwable {
        // Given: A new instance of X7875_NewUnix
        X7875_NewUnix x7875_NewUnix = new X7875_NewUnix();

        // When: Retrieving the local file data
        byte[] data = x7875_NewUnix.getLocalFileDataData();

        // Then: The data should match the expected byte array
        assertArrayEquals("Local file data should match expected array", EXPECTED_LOCAL_FILE_DATA, data);
    }

    @Test(timeout = 4000)
    public void testGetUID() throws Throwable {
        // Given: A new instance of X7875_NewUnix
        X7875_NewUnix x7875_NewUnix = new X7875_NewUnix();

        // When: Retrieving the UID
        long uid = x7875_NewUnix.getUID();

        // Then: The UID should be the default value
        assertEquals("UID should be the default value", DEFAULT_UID_GID, uid);
    }

    @Test(timeout = 4000)
    public void testToString() throws Throwable {
        // Given: A new instance of X7875_NewUnix
        X7875_NewUnix x7875_NewUnix = new X7875_NewUnix();

        // When: Converting to string
        String stringRepresentation = x7875_NewUnix.toString();

        // Then: The string should match the expected format
        assertEquals("String representation should match expected format", "0x7875 Zip Extra Field: UID=1000 GID=1000", stringRepresentation);
    }